"""
SMS System Initialization
"""

import logging
from app.models.sms_provider import SmsProvider

logger = logging.getLogger(__name__)

def initialize_sms_system():
    """Initialize SMS system with default providers"""
    try:
        # Ensure indexes are created
        SmsProvider.create_indexes()
        
        # Check if mock provider exists
        mock = SmsProvider.find_by_slug('mock')
        if not mock:
            # Create mock provider for development
            logger.info("Creating mock SMS provider for development")
            SmsProvider.seed_mock_provider()
        
        # In production, check for real providers
        # This is where you'd add SMSO configuration
        
        logger.info("SMS system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize SMS system: {e}")
        # Don't fail app startup, just log the error