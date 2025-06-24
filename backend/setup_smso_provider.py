#!/usr/bin/env python3
"""
Setup SMSO SMS Provider

This script initializes the SMSO SMS provider in the database with
configuration from environment variables.

Usage:
    python setup_smso_provider.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.database import init_mongodb
from app.config import Config
from app.utils.encryption import initialize_encryption
from app.services.sms.provider_config_service import get_provider_config_service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Initialize SMSO provider in the database"""
    try:
        # Check for required environment variables
        if not os.environ.get('SMSO_API_KEY'):
            logger.error("SMSO_API_KEY not found in environment variables")
            logger.info("Please add SMSO_API_KEY to your .env file")
            return False
        
        if not os.environ.get('ENCRYPTION_MASTER_KEY'):
            logger.error("ENCRYPTION_MASTER_KEY not found in environment variables")
            logger.info("Generate a key using: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
            return False
        
        # Initialize database
        logger.info("Initializing database connection...")
        init_mongodb(Config)
        
        # Initialize encryption
        logger.info("Initializing encryption system...")
        initialize_encryption(
            master_key=os.environ.get('ENCRYPTION_MASTER_KEY'),
            jwt_secret=os.environ.get('JWT_SECRET_KEY')
        )
        
        # Get provider config service
        config_service = get_provider_config_service()
        
        # Check if SMSO provider already exists
        from app.models.sms_provider import SmsProvider
        existing = SmsProvider.find_by_slug('smso')
        
        if existing:
            logger.info("SMSO provider already exists, updating configuration...")
            
            # Update existing provider
            success, result = config_service.update_provider(
                str(existing._id),
                {
                    'name': 'SMSO.ro',
                    'is_active': True,
                    'is_default': False,  # Keep mock as default in development
                    'priority': 50,
                    'config': {
                        'api_key': os.environ.get('SMSO_API_KEY'),
                        'sender_id': os.environ.get('SMSO_SENDER_ID', 'PeFocLemne'),
                        'api_base_url': os.environ.get('SMSO_API_BASE_URL'),
                        'webhook_url': os.environ.get('SMSO_WEBHOOK_URL')
                    }
                }
            )
        else:
            logger.info("Creating new SMSO provider...")
            
            # Create new provider
            success, result = config_service.create_provider({
                'name': 'SMSO.ro',
                'slug': 'smso',
                'provider_type': 'smso',
                'is_active': True,
                'is_default': False,  # Keep mock as default in development
                'priority': 50,
                'config': {
                    'api_key': os.environ.get('SMSO_API_KEY'),
                    'sender_id': os.environ.get('SMSO_SENDER_ID', 'PeFocLemne'),
                    'api_base_url': os.environ.get('SMSO_API_BASE_URL'),
                    'webhook_url': os.environ.get('SMSO_WEBHOOK_URL')
                }
            })
        
        if success:
            logger.info(f"✓ {result['message']}")
            
            # Test the provider
            logger.info("Testing SMSO provider configuration...")
            if existing:
                provider_id = str(existing._id)
            else:
                provider_id = result.get('provider_id')
            
            test_success, test_error = config_service.test_provider(provider_id)
            
            if test_success:
                logger.info("✓ SMSO provider test successful!")
                logger.info("\nSMSO provider is now configured and ready to use.")
                logger.info("To make it the default provider, update ACTIVE_SMS_PROVIDER=smso in your .env file")
            else:
                logger.warning(f"⚠ SMSO provider test failed: {test_error}")
                logger.info("Please check your API key and configuration")
            
            return True
        else:
            logger.error(f"✗ Failed to configure SMSO provider: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up SMSO provider: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)