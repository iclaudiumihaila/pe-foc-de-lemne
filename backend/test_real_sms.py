#!/usr/bin/env python3
"""
Force test with real SMS provider
"""

import os
os.environ['TEST_REAL_SMS'] = '1'
os.environ['FLASK_ENV'] = 'production'  # Force production mode

import sys
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config
from app.services.sms.sms_manager import get_sms_manager
from app.services.sms.provider_interface import SmsMessage

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app to initialize everything properly
app = create_app(Config)

def main():
    """Test real SMS sending"""
    with app.app_context():
        try:
            # Get phone number
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
            
            # Get SMS manager
            sms_manager = get_sms_manager()
            
            # Force clear cache to reload providers
            sms_manager.clear_cache()
            sms_manager._is_development = False  # Force production mode
            
            # Check active provider
            provider = sms_manager.get_active_provider()
            if provider:
                logger.info(f"Active provider: {provider.__class__.__name__}")
            else:
                logger.error("No active SMS provider found")
                return False
            
            # Create test message
            import random
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            message = SmsMessage(
                to=phone_number,
                body=f"Pe Foc de Lemne - Cod verificare: {code}. Valabil 5 minute.",
                message_type='otp'
            )
            
            # Send SMS
            logger.info("Sending SMS...")
            result = sms_manager.send_sms(message)
            
            if result.success:
                logger.info("✓ SMS sent successfully!")
                logger.info(f"  Message ID: {result.message_id}")
                logger.info(f"  Cost: {result.cost} EUR")
                logger.info(f"  Your code is: {code}")
                return True
            else:
                logger.error(f"✗ Failed to send SMS: {result.error_message}")
                logger.error(f"  Error code: {result.error_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("REAL SMS TEST - SMSO.ro")
    print("="*60)
    print("\nThis will send a REAL SMS and incur charges!")
    print("Make sure your SMSO account has credits.\n")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Test cancelled.")
        sys.exit(0)
    
    print()
    success = main()
    sys.exit(0 if success else 1)