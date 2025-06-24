#!/usr/bin/env python3
"""Direct SMSO API Test"""

import os
os.environ['FLASK_ENV'] = 'production'

from dotenv import load_dotenv
load_dotenv()

from app.database import init_mongodb
from app.config import Config
from app.utils.encryption import initialize_encryption
from app.models.sms_provider import SmsProvider
from app.services.sms.providers.smso_provider import SmsoProvider
from app.services.sms.provider_interface import SmsMessage

# Initialize
init_mongodb(Config)
initialize_encryption(
    master_key=os.environ.get('ENCRYPTION_MASTER_KEY'),
    jwt_secret=os.environ.get('JWT_SECRET_KEY')
)

# Get SMSO provider from database
smso_model = SmsProvider.find_by_slug('smso')
if not smso_model:
    print("SMSO provider not found!")
    exit(1)

print(f"Found SMSO provider: {smso_model.name}")
print(f"Active: {smso_model.is_active}, Default: {smso_model.is_default}")

# Get decrypted config
config = {
    'api_key': smso_model.get_api_key(),
    'sender_id': smso_model.config.get('sender_id', 'INFO'),
    'api_base_url': smso_model.config.get('api_base_url'),
    'webhook_url': smso_model.config.get('webhook_url')
}

print(f"Sender ID: {config['sender_id']}")
print(f"API Key: {'*' * 20 + config['api_key'][-10:] if config['api_key'] else 'NOT SET'}")

# Create provider instance
provider = SmsoProvider(config)

# Create message
message = SmsMessage(
    to='+40722123456',
    body='Test SMS from Pe Foc de Lemne. Cod: 123456',
    message_type='transactional'
)

print("\nSending SMS...")
try:
    result = provider.send_sms(message)
    if result.success:
        print(f"✓ SUCCESS! Message ID: {result.message_id}")
        print(f"Cost: {result.cost} EUR")
    else:
        print(f"✗ FAILED: {result.error_message}")
        print(f"Error code: {result.error_code}")
except Exception as e:
    print(f"✗ Exception: {e}")
    import traceback
    traceback.print_exc()