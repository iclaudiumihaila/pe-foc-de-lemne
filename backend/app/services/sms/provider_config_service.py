"""
SMS Provider Configuration Service

Manages SMS provider configurations including creation, update,
activation/deactivation, and secure storage of credentials.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from bson import ObjectId

from app.models.sms_provider import SmsProvider
from app.models.sms_log import SmsLog
from app.services.sms.sms_manager import get_sms_manager
from app.services.sms.provider_interface import SmsProviderInterface
from app.utils.encryption import get_sms_encryption_manager

logger = logging.getLogger(__name__)

class ProviderConfigService:
    """Service for managing SMS provider configurations"""
    
    # Supported provider types
    SUPPORTED_PROVIDERS = {
        'mock': {
            'name': 'Mock Provider',
            'description': 'Development/testing provider',
            'required_fields': [],
            'optional_fields': ['success_rate', 'fixed_otp_code', 'log_messages'],
            'sensitive_fields': []
        },
        'smso': {
            'name': 'SMSO.ro',
            'description': 'Romanian SMS gateway provider',
            'required_fields': ['api_key'],
            'optional_fields': ['sender_id', 'webhook_url', 'api_base_url'],
            'sensitive_fields': ['api_key']
        }
    }
    
    def __init__(self):
        """Initialize provider configuration service"""
        self.encryption_manager = get_sms_encryption_manager()
        self.sms_manager = get_sms_manager()
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Get list of supported provider types"""
        return [
            {
                'type': provider_type,
                'name': info['name'],
                'description': info['description'],
                'required_fields': info['required_fields'],
                'optional_fields': info['optional_fields']
            }
            for provider_type, info in self.SUPPORTED_PROVIDERS.items()
        ]
    
    def create_provider(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new SMS provider configuration.
        
        Args:
            data: Provider configuration data
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Validate provider type
            provider_type = data.get('provider_type')
            if provider_type not in self.SUPPORTED_PROVIDERS:
                return False, {'error': f'Unsupported provider type: {provider_type}'}
            
            # Validate required fields
            provider_info = self.SUPPORTED_PROVIDERS[provider_type]
            missing_fields = []
            for field in provider_info['required_fields']:
                if field not in data.get('config', {}):
                    missing_fields.append(field)
            
            if missing_fields:
                return False, {'error': f'Missing required fields: {", ".join(missing_fields)}'}
            
            # Check for duplicate slug
            slug = data.get('slug')
            if SmsProvider.find_by_slug(slug):
                return False, {'error': f'Provider with slug "{slug}" already exists'}
            
            # Create provider
            provider = SmsProvider({
                'name': data['name'],
                'slug': slug,
                'provider_type': provider_type,
                'config': {},
                'is_active': data.get('is_active', False),
                'is_default': data.get('is_default', False),
                'priority': data.get('priority', 100)
            })
            
            # Set configuration with encryption for sensitive fields
            config = data.get('config', {})
            for key, value in config.items():
                if key in provider_info['sensitive_fields']:
                    provider.encrypt_config_value(key, value)
                else:
                    provider.config[key] = value
            
            # Save provider
            provider.save()
            
            # If set as default, update other providers
            if provider.is_default:
                self._update_default_provider(provider._id)
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Created SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'provider_id': str(provider._id),
                'message': f'Provider {provider.name} created successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to create provider: {e}")
            return False, {'error': str(e)}
    
    def update_provider(self, provider_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an existing SMS provider configuration.
        
        Args:
            provider_id: Provider ID
            data: Updated configuration data
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return False, {'error': 'Provider not found'}
            
            # Update basic fields
            if 'name' in data:
                provider.name = data['name']
            
            if 'is_active' in data:
                provider.is_active = data['is_active']
            
            if 'is_default' in data:
                provider.is_default = data['is_default']
            
            if 'priority' in data:
                provider.priority = data['priority']
            
            # Update configuration
            if 'config' in data:
                provider_info = self.SUPPORTED_PROVIDERS[provider.provider_type]
                new_config = data['config']
                
                # Update or add config values
                for key, value in new_config.items():
                    if key in provider_info['sensitive_fields']:
                        # Only update if value is provided (not masked)
                        if value and not value.startswith('***'):
                            provider.encrypt_config_value(key, value)
                    else:
                        provider.config[key] = value
            
            # Update timestamps
            provider.updated_at = datetime.now(timezone.utc)
            
            # Save provider
            provider.save()
            
            # If set as default, update other providers
            if provider.is_default:
                self._update_default_provider(provider._id)
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Updated SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'message': f'Provider {provider.name} updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to update provider: {e}")
            return False, {'error': str(e)}
    
    def delete_provider(self, provider_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete an SMS provider configuration.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return False, {'error': 'Provider not found'}
            
            # Don't delete if it's the only active provider
            active_count = SmsProvider.count_active()
            if provider.is_active and active_count <= 1:
                return False, {'error': 'Cannot delete the only active provider'}
            
            # Don't delete mock provider in development
            if provider.slug == 'mock' and self.sms_manager._is_development:
                return False, {'error': 'Cannot delete mock provider in development mode'}
            
            # Delete provider
            provider.delete()
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Deleted SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'message': f'Provider {provider.name} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete provider: {e}")
            return False, {'error': str(e)}
    
    def activate_provider(self, provider_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Activate an SMS provider.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return False, {'error': 'Provider not found'}
            
            if provider.is_active:
                return True, {'message': 'Provider is already active'}
            
            # Test provider before activation
            success, error = self.test_provider(provider_id)
            if not success:
                return False, {'error': f'Provider test failed: {error}'}
            
            # Activate provider
            provider.is_active = True
            provider.updated_at = datetime.now(timezone.utc)
            provider.save()
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Activated SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'message': f'Provider {provider.name} activated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to activate provider: {e}")
            return False, {'error': str(e)}
    
    def deactivate_provider(self, provider_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Deactivate an SMS provider.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return False, {'error': 'Provider not found'}
            
            if not provider.is_active:
                return True, {'message': 'Provider is already inactive'}
            
            # Don't deactivate if it's the only active provider
            active_count = SmsProvider.count_active()
            if active_count <= 1:
                return False, {'error': 'Cannot deactivate the only active provider'}
            
            # Deactivate provider
            provider.is_active = False
            provider.is_default = False  # Can't be default if inactive
            provider.updated_at = datetime.now(timezone.utc)
            provider.save()
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Deactivated SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'message': f'Provider {provider.name} deactivated successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to deactivate provider: {e}")
            return False, {'error': str(e)}
    
    def set_default_provider(self, provider_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Set a provider as the default.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Tuple of (success, result/error)
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return False, {'error': 'Provider not found'}
            
            if not provider.is_active:
                return False, {'error': 'Cannot set inactive provider as default'}
            
            # Update providers
            provider.is_default = True
            provider.save()
            
            self._update_default_provider(provider._id)
            
            # Clear SMS manager cache
            self.sms_manager.clear_cache()
            
            logger.info(f"Set default SMS provider: {provider.name} ({provider.slug})")
            
            return True, {
                'message': f'Provider {provider.name} set as default'
            }
            
        except Exception as e:
            logger.error(f"Failed to set default provider: {e}")
            return False, {'error': str(e)}
    
    def test_provider(self, provider_id: str) -> Tuple[bool, Optional[str]]:
        """
        Test a provider's configuration and connectivity.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Find provider
            provider_model = SmsProvider.find_by_id(provider_id)
            if not provider_model:
                return False, 'Provider not found'
            
            # Get provider instance
            provider = self.sms_manager._get_provider_instance(provider_model)
            if not provider:
                return False, 'Failed to initialize provider'
            
            # Run health check
            is_healthy, error = provider.health_check()
            
            if is_healthy:
                logger.info(f"Provider test successful: {provider_model.name}")
                return True, None
            else:
                logger.warning(f"Provider test failed: {provider_model.name} - {error}")
                return False, error or 'Health check failed'
                
        except Exception as e:
            logger.error(f"Provider test error: {e}")
            return False, str(e)
    
    def get_provider_stats(self, provider_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get provider statistics.
        
        Args:
            provider_id: Provider ID
            days: Number of days to look back
            
        Returns:
            Provider statistics
        """
        try:
            # Find provider
            provider = SmsProvider.find_by_id(provider_id)
            if not provider:
                return {'error': 'Provider not found'}
            
            # Get stats from logs
            stats = SmsLog.get_provider_stats(provider._id, days)
            
            return {
                'provider': {
                    'name': provider.name,
                    'type': provider.provider_type,
                    'is_active': provider.is_active,
                    'is_default': provider.is_default
                },
                'stats': stats,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to get provider stats: {e}")
            return {'error': str(e)}
    
    def _update_default_provider(self, provider_id: ObjectId):
        """Update default provider settings"""
        # Remove default from all other providers
        SmsProvider.get_collection().update_many(
            {'_id': {'$ne': provider_id}},
            {'$set': {'is_default': False}}
        )

# Global instance
_provider_config_service = None

def get_provider_config_service() -> ProviderConfigService:
    """Get global provider config service instance"""
    global _provider_config_service
    if _provider_config_service is None:
        _provider_config_service = ProviderConfigService()
    return _provider_config_service