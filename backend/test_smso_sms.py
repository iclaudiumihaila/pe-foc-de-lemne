#!/usr/bin/env python3
"""
Test SMSO SMS Sending

This script tests sending an SMS through the SMSO provider.
"""

import os
import sys
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force real SMS in development
os.environ['TEST_REAL_SMS'] = '1'

from app.database import init_mongodb
from app.config import Config
from app.utils.encryption import initialize_encryption
from app.services.sms.sms_manager import get_sms_manager
from app.services.sms.provider_interface import SmsMessage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Test SMSO SMS sending"""
    try:
        # Get phone number for testing
        phone_number = input("Enter Romanian phone number (format: 0722123456): ").strip()
        
        if not phone_number:
            logger.error("Phone number is required")
            return False
        
        # Normalize phone number
        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                phone_number = '+4' + phone_number
            else:
                phone_number = '+40' + phone_number
        
        logger.info(f"Testing SMS to: {phone_number}")
        
        # Initialize systems
        logger.info("Initializing database...")
        init_mongodb(Config)
        
        logger.info("Initializing encryption...")
        initialize_encryption(
            master_key=os.environ.get('ENCRYPTION_MASTER_KEY'),
            jwt_secret=os.environ.get('JWT_SECRET_KEY')
        )
        
        # Get SMS manager
        sms_manager = get_sms_manager()
        
        # Check active provider
        provider = sms_manager.get_active_provider()
        if provider:
            logger.info(f"Active provider: {provider.__class__.__name__}")
        else:
            logger.error("No active SMS provider found")
            return False
        
        # Create test message
        message = SmsMessage(
            to=phone_number,
            body="Testare sistem SMS Pe Foc de Lemne. Cod verificare: 123456",
            message_type='transactional'
        )
        
        # Send SMS
        logger.info("Sending SMS...")
        result = sms_manager.send_sms(message)
        
        if result.success:
            logger.info("✓ SMS sent successfully!")
            logger.info(f"  Message ID: {result.message_id}")
            logger.info(f"  Cost: {result.cost} EUR")
            logger.info(f"  Parts: {result.parts_count}")
            
            # Get delivery status
            if result.message_id:
                logger.info("\nChecking delivery status...")
                status = sms_manager.get_sms_status(result.message_id)
                logger.info(f"  Status: {status.status}")
                if status.delivered_at:
                    logger.info(f"  Delivered at: {status.delivered_at}")
            
            return True
        else:
            logger.error(f"✗ Failed to send SMS: {result.error_message}")
            logger.error(f"  Error code: {result.error_code}")
            return False
            
    except KeyboardInterrupt:
        logger.info("\nTest cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    if not os.environ.get('SMSO_API_KEY'):
        logger.error("SMSO_API_KEY not found in environment")
        sys.exit(1)
    
    if not os.environ.get('ENCRYPTION_MASTER_KEY'):
        logger.error("ENCRYPTION_MASTER_KEY not found in environment")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("SMSO SMS TEST")
    print("="*60)
    print("\nThis will send a real SMS message and incur charges.")
    print("Make sure you have credits in your SMSO account.\n")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Test cancelled.")
        sys.exit(0)
    
    print()
    success = main()
    sys.exit(0 if success else 1)