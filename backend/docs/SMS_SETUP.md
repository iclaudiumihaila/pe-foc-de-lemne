# SMS Provider Setup Guide

This guide explains how to configure SMS providers for the Pe Foc de Lemne application.

## Overview

The application supports multiple SMS providers:
- **Mock Provider** (default in development) - Simulates SMS sending without actual API calls
- **SMSO.ro** - Romanian SMS gateway service
- **Twilio** (legacy support) - International SMS service

## Environment Configuration

### 1. Generate Encryption Key

First, generate a master encryption key for securing API credentials:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Update .env File

Add the following to your `.env` file:

```env
# Encryption key (use the key generated above)
ENCRYPTION_MASTER_KEY=your-generated-encryption-key-here

# SMSO Configuration
SMSO_API_KEY=your-smso-api-key-here
SMSO_SENDER_ID=PeFocLemne  # Or your verified phone number
SMSO_API_BASE_URL=  # Leave empty for production API
SMSO_WEBHOOK_URL=   # Optional webhook for delivery reports

# Active SMS Provider (mock, smso, twilio)
ACTIVE_SMS_PROVIDER=mock  # Change to 'smso' when ready
```

### 3. Get SMSO API Key

1. Create an account at [SMSO.ro](https://www.smso.ro)
2. Go to your account dashboard: https://app.smso.ro/account/api
3. Generate an API key
4. Copy the API key to your `.env` file

## Setup SMSO Provider

Run the setup script to configure SMSO in the database:

```bash
cd backend
python setup_smso_provider.py
```

This script will:
- Check for required environment variables
- Initialize the SMSO provider in the database
- Encrypt and store the API key securely
- Test the provider configuration

## Switching Providers

### Development Mode

In development, the mock provider is used by default. To test with real SMS:

```bash
# Set environment variable to use real SMS
export TEST_REAL_SMS=1

# Or update .env file
ACTIVE_SMS_PROVIDER=smso
```

### Production Mode

In production, update your environment variables:

```env
FLASK_ENV=production
ACTIVE_SMS_PROVIDER=smso
```

## Testing SMS Functionality

### 1. Test with Mock Provider (Development)

```bash
# The mock provider returns a fixed OTP code: 123456
curl -X POST http://localhost:8000/api/checkout/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "0722123456"}'
```

### 2. Test with SMSO Provider

```bash
# Make sure ACTIVE_SMS_PROVIDER=smso in .env
# This will send a real SMS
curl -X POST http://localhost:8000/api/checkout/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "0722123456"}'
```

## Admin Management

Future updates will include admin UI for:
- Viewing all configured providers
- Switching between providers
- Monitoring SMS usage and costs
- Viewing delivery reports

## Troubleshooting

### Common Issues

1. **"No SMS provider available" error**
   - Ensure at least one provider is active in the database
   - Run `python setup_smso_provider.py` to initialize

2. **"ENCRYPTION_MASTER_KEY not set" error**
   - Generate and add encryption key to `.env`
   - Restart the application

3. **SMS not sending in development**
   - Check if mock provider is active (default)
   - Set `TEST_REAL_SMS=1` to use real provider

4. **SMSO authentication failed**
   - Verify API key is correct
   - Check if your SMSO account has credits
   - Ensure sender ID is approved (if using custom)

## Security Notes

- Never commit `.env` files with real API keys
- Keep `ENCRYPTION_MASTER_KEY` secure and backed up
- API keys are encrypted in the database
- Use environment-specific configurations

## Cost Considerations

- SMSO charges per SMS part (160 characters)
- Longer messages are split into multiple parts
- Romanian text with diacritics uses Unicode (70 chars/part)
- Monitor usage through SMSO dashboard