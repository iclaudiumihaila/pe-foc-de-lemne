"""
SMS Manager - Orchestrates SMS sending through multiple providers
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, Type
from datetime import datetime
from flask import current_app
from app.models.sms_provider import SmsProvider
from app.models.sms_log import SmsLog
from app.services.sms.provider_interface import (
    SmsProviderInterface,
    SmsMessage,
    SmsResponse,
    SmsStatus,
    ProviderBalance
)

logger = logging.getLogger(__name__)

class SmsManager:
    """
    Manages SMS sending through multiple providers.
    Handles provider selection, failover, and logging.
    """
    
    # Provider class mapping
    PROVIDER_CLASSES = {
        'mock': 'app.services.sms.providers.mock_provider.MockProvider',
        'smso': 'app.services.sms.providers.smso_provider.SmsoProvider',
        'twilio': 'app.services.sms.providers.twilio_provider.TwilioProvider',
        'vonage': 'app.services.sms.providers.vonage_provider.VonageProvider'
    }
    
    def __init__(self):
        """Initialize SMS manager"""
        self._providers_cache: Dict[str, SmsProviderInterface] = {}
        self._default_provider = None
        self._is_development = self._check_development_mode()
        
        # Initialize indexes on startup
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure database indexes are created"""
        try:
            SmsProvider.create_indexes()
            SmsLog.create_indexes()
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def _check_development_mode(self) -> bool:
        """Check if running in development mode"""
        # Check Flask debug mode
        try:
            if current_app and current_app.debug:
                return True
        except RuntimeError:
            # Outside of application context
            pass
        
        # Check environment
        env = os.environ.get('FLASK_ENV', os.environ.get('ENV', '')).lower()
        return env in ['development', 'dev']
    
    def _load_provider_class(self, provider_type: str) -> Optional[Type[SmsProviderInterface]]:
        """Dynamically load provider class"""
        class_path = self.PROVIDER_CLASSES.get(provider_type)
        if not class_path:
            logger.error(f"Unknown provider type: {provider_type}")
            return None
        
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)
            return provider_class
        except Exception as e:
            logger.error(f"Failed to load provider class {class_path}: {e}")
            return None
    
    def _get_provider_instance(self, provider_model: SmsProvider) -> Optional[SmsProviderInterface]:
        """Get or create provider instance"""
        # Check cache
        cache_key = str(provider_model._id)
        if cache_key in self._providers_cache:
            return self._providers_cache[cache_key]
        
        # Load provider class
        provider_class = self._load_provider_class(provider_model.provider_type)
        if not provider_class:
            return None
        
        try:
            # Prepare configuration
            config = provider_model.config.copy()
            
            # Decrypt sensitive values
            if provider_model.get_api_key():
                config['api_key'] = provider_model.get_api_key()
            
            # Create instance
            instance = provider_class(config)
            
            # Cache it
            self._providers_cache[cache_key] = instance
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create provider instance: {e}")
            return None
    
    def get_active_provider(self) -> Optional[SmsProviderInterface]:
        """Get the active SMS provider"""
        # Skip mock provider check - always use the configured provider
        
        # Get active provider from database
        provider_model = SmsProvider.get_active_provider()
        if not provider_model:
            logger.warning("No active SMS provider configured")
            # Fallback to mock in development
            if self._is_development:
                return self._get_mock_provider()
            return None
        
        # Get provider instance
        provider = self._get_provider_instance(provider_model)
        if not provider:
            logger.error(f"Failed to load provider: {provider_model.name}")
            return None
        
        # Health check
        is_healthy, error = provider.health_check()
        if not is_healthy:
            logger.warning(f"Provider {provider_model.name} unhealthy: {error}")
            # Try to find backup provider
            return self._get_backup_provider(exclude_id=provider_model._id)
        
        return provider
    
    def _get_mock_provider(self) -> Optional[SmsProviderInterface]:
        """Get mock provider for development"""
        # Check if mock provider exists in DB
        mock_model = SmsProvider.find_by_slug('mock')
        if not mock_model:
            # Create default mock provider
            mock_model = SmsProvider.seed_mock_provider()
        
        return self._get_provider_instance(mock_model)
    
    def _get_backup_provider(self, exclude_id=None) -> Optional[SmsProviderInterface]:
        """Get backup provider for failover"""
        # Get all active providers
        providers = SmsProvider.get_all_providers(active_only=True)
        
        for provider_model in providers:
            # Skip excluded provider
            if exclude_id and provider_model._id == exclude_id:
                continue
            
            # Try to get instance
            provider = self._get_provider_instance(provider_model)
            if not provider:
                continue
            
            # Health check
            is_healthy, _ = provider.health_check()
            if is_healthy:
                logger.info(f"Using backup provider: {provider_model.name}")
                return provider
        
        # Last resort: mock provider in development
        if self._is_development:
            return self._get_mock_provider()
        
        return None
    
    def send_sms(self, message: SmsMessage) -> SmsResponse:
        """
        Send SMS through active provider.
        
        Args:
            message: SMS message to send
            
        Returns:
            SmsResponse with result
        """
        # Get provider
        provider = self.get_active_provider()
        if not provider:
            return SmsResponse(
                success=False,
                error_code='NO_PROVIDER',
                error_message='No SMS provider available'
            )
        
        # Log attempt
        log = SmsLog({
            'provider': provider.get_provider_name().lower(),
            'phone_number': message.to,
            'message_type': message.message_type,
            'message': message.body,
            'status': SmsLog.STATUS_PENDING,
            'metadata': message.metadata
        })
        log.save()
        
        # Send SMS
        start_time = datetime.utcnow()
        response = provider.send_sms(message)
        
        # Update log with result
        log.status = SmsLog.STATUS_SENT if response.success else SmsLog.STATUS_FAILED
        log.response_token = response.message_id
        log.provider_response = response.provider_response
        log.cost = response.cost or 0
        log.error = response.error_message
        
        if response.success:
            log.sent_at = datetime.utcnow()
            # Update provider usage stats
            self._update_provider_stats(provider, sent=1, cost=response.cost)
        else:
            # Update provider failure stats
            self._update_provider_stats(provider, failed=1)
        
        log.save()
        
        # Add log ID to response for tracking
        response.provider_response['log_id'] = str(log._id)
        
        return response
    
    def get_message_status(self, message_id: str, provider_slug: str = None) -> SmsStatus:
        """
        Get message delivery status.
        
        Args:
            message_id: Provider's message ID
            provider_slug: Optional provider slug
            
        Returns:
            SmsStatus with current status
        """
        # Find log by response token
        log = SmsLog.find_by_response_token(message_id)
        if not log:
            return SmsStatus(
                message_id=message_id,
                status='not_found',
                error_code='MESSAGE_NOT_FOUND',
                error_message='Message not found in logs'
            )
        
        # Get provider
        if provider_slug:
            provider_model = SmsProvider.find_by_slug(provider_slug)
        else:
            provider_model = SmsProvider.find_by_slug(log.provider)
        
        if not provider_model:
            # Return status from log
            return SmsStatus(
                message_id=message_id,
                status=log.status,
                delivered_at=log.delivered_at
            )
        
        # Get provider instance
        provider = self._get_provider_instance(provider_model)
        if not provider:
            return SmsStatus(
                message_id=message_id,
                status=log.status,
                delivered_at=log.delivered_at
            )
        
        # Get fresh status from provider
        try:
            status = provider.get_status(message_id)
            
            # Update log if status changed
            if status.status != log.status:
                log.status = status.status
                if status.status == SmsLog.STATUS_DELIVERED:
                    log.delivered_at = status.delivered_at or datetime.utcnow()
                    log.delivery_time = log.calculate_delivery_time()
                    # Update provider delivery stats
                    self._update_provider_stats(provider, delivered=1)
                elif status.status == SmsLog.STATUS_FAILED:
                    log.error = status.error_message
                
                log.save()
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get status from provider: {e}")
            # Return status from log
            return SmsStatus(
                message_id=message_id,
                status=log.status,
                delivered_at=log.delivered_at
            )
    
    def get_provider_balance(self, provider_slug: str = None) -> Optional[ProviderBalance]:
        """Get provider balance"""
        if provider_slug:
            provider_model = SmsProvider.find_by_slug(provider_slug)
        else:
            provider_model = SmsProvider.get_active_provider()
        
        if not provider_model:
            return None
        
        provider = self._get_provider_instance(provider_model)
        if not provider:
            return None
        
        try:
            return provider.get_balance()
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return None
    
    def _update_provider_stats(self, provider: SmsProviderInterface, 
                             sent: int = 0, delivered: int = 0, 
                             failed: int = 0, cost: float = 0):
        """Update provider usage statistics"""
        try:
            # Find provider model
            provider_name = provider.get_provider_name().lower()
            provider_model = SmsProvider.find_by_slug(provider_name)
            
            if provider_model:
                provider_model.update_usage_stats(
                    sent=sent,
                    delivered=delivered,
                    failed=failed,
                    cost=cost
                )
                provider_model.save()
                
        except Exception as e:
            logger.error(f"Failed to update provider stats: {e}")
    
    def handle_webhook(self, provider_slug: str, data: Dict[str, Any]) -> bool:
        """
        Handle provider webhook for delivery reports.
        
        Args:
            provider_slug: Provider identifier
            data: Webhook payload
            
        Returns:
            True if webhook was processed
        """
        # Get provider
        provider_model = SmsProvider.find_by_slug(provider_slug)
        if not provider_model:
            logger.warning(f"Unknown provider for webhook: {provider_slug}")
            return False
        
        provider = self._get_provider_instance(provider_model)
        if not provider:
            return False
        
        try:
            # Let provider parse webhook
            status = provider.handle_webhook(data)
            if not status:
                return False
            
            # Update log
            log = SmsLog.find_by_response_token(status.message_id)
            if log:
                log.status = status.status
                if status.delivered_at:
                    log.delivered_at = status.delivered_at
                    log.delivery_time = log.calculate_delivery_time()
                log.save()
                
                # Update provider stats
                if status.status == SmsLog.STATUS_DELIVERED:
                    self._update_provider_stats(provider, delivered=1)
                elif status.status == SmsLog.STATUS_FAILED:
                    self._update_provider_stats(provider, failed=1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False
    
    def clear_cache(self):
        """Clear provider instance cache"""
        self._providers_cache.clear()
    
    @classmethod
    def generate_verification_code(cls) -> str:
        """Generate a 6-digit verification code"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])


# Global SMS manager instance
_sms_manager = None

def get_sms_manager() -> SmsManager:
    """
    Get SMS manager instance (singleton pattern).
    
    Returns:
        SmsManager instance
    """
    global _sms_manager
    if _sms_manager is None:
        _sms_manager = SmsManager()
    return _sms_manager