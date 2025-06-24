#!/usr/bin/env python3
"""
Activate SMSO as the default SMS provider
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
from app.models.sms_provider import SmsProvider

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Make SMSO the active default provider"""
    try:
        # Initialize database
        logger.info("Initializing database connection...")
        init_mongodb(Config)
        
        # Initialize encryption
        logger.info("Initializing encryption system...")
        initialize_encryption(
            master_key=os.environ.get('ENCRYPTION_MASTER_KEY'),
            jwt_secret=os.environ.get('JWT_SECRET_KEY')
        )
        
        # Find SMSO provider
        smso = SmsProvider.find_by_slug('smso')
        if not smso:
            logger.error("SMSO provider not found. Please run setup_smso_provider.py first")
            return False
        
        # Deactivate all other providers
        logger.info("Deactivating other providers...")
        from app.database import get_database
        db = get_database()
        db.sms_providers.update_many(
            {'_id': {'$ne': smso._id}},
            {'$set': {'is_active': False, 'is_default': False}}
        )
        
        # Make SMSO active and default
        logger.info("Activating SMSO as default provider...")
        smso.is_active = True
        smso.is_default = True
        smso.priority = 100  # Highest priority
        smso.save()
        
        logger.info("✓ SMSO is now the active default SMS provider")
        
        # Verify
        active = SmsProvider.get_active_provider()
        if active and active.slug == 'smso':
            logger.info("✓ Verification successful - SMSO is active")
            return True
        else:
            logger.error("✗ Verification failed")
            return False
            
    except Exception as e:
        logger.error(f"Error activating SMSO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)