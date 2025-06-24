# SMS System Architecture

**Created**: 2025-06-22T15:35:00Z
**Architect**: Orchestrator

## System Overview

### Core Components

1. **SMS Provider Interface** (`app/services/sms/provider_interface.py`)
   - Abstract base class defining provider contract
   - Methods: send_sms, check_status, get_balance
   - Standardized response format

2. **Provider Implementations** (`app/services/sms/providers/`)
   - `smso_provider.py` - SMSO.ro implementation
   - `mock_provider.py` - Development/testing provider
   - Future: `twilio_provider.py`, `vonage_provider.py`

3. **SMS Service Manager** (`app/services/sms/sms_manager.py`)
   - Provider selection logic
   - Failover handling
   - Queue management
   - Metric collection

4. **Provider Configuration** (`app/models/sms_provider.py`)
   - MongoDB model for provider settings
   - Encrypted API key storage
   - Provider-specific configuration

5. **Admin Interface** (`app/routes/admin/sms_admin.py`)
   - Provider management endpoints
   - Usage statistics API
   - Test SMS functionality

## Database Schema

### sms_providers Collection
```javascript
{
  _id: ObjectId,
  name: "SMSO",
  slug: "smso",
  is_active: true,
  is_default: true,
  config: {
    api_key: "encrypted_key",
    sender_id: "PeFocLemne",
    api_base_url: "https://app.smso.ro/api/v1"
  },
  features: ["otp", "marketing", "transactional"],
  created_at: ISODate,
  updated_at: ISODate
}
```

### sms_logs Collection
```javascript
{
  _id: ObjectId,
  provider: "smso",
  phone_number: "+40755123456",
  message_type: "otp",
  message: "Codul tau este: 123456",
  status: "delivered",
  response_token: "uuid",
  cost: 3.5, // eurocents
  created_at: ISODate,
  delivered_at: ISODate,
  error: null
}
```

### sms_statistics Collection
```javascript
{
  _id: ObjectId,
  provider: "smso",
  date: ISODate("2025-06-22"),
  sent_count: 150,
  delivered_count: 148,
  failed_count: 2,
  total_cost: 525, // eurocents
  avg_delivery_time: 2.3 // seconds
}
```

## API Design

### Provider Management
- `GET /api/admin/sms/providers` - List all providers
- `GET /api/admin/sms/providers/:id` - Get provider details
- `PUT /api/admin/sms/providers/:id` - Update provider config
- `POST /api/admin/sms/providers/:id/activate` - Set as active provider
- `POST /api/admin/sms/providers/:id/test` - Send test SMS

### SMS Operations (Internal)
- `POST /internal/sms/send` - Send SMS (used by services)
- `GET /internal/sms/status/:token` - Check delivery status
- `GET /internal/sms/balance` - Get current balance

### Statistics
- `GET /api/admin/sms/statistics` - Usage statistics
- `GET /api/admin/sms/logs` - SMS logs with filtering

## Security Considerations

1. **API Key Encryption**
   - Use Fernet symmetric encryption
   - Keys stored encrypted in database
   - Decrypted only when needed

2. **Access Control**
   - Admin-only endpoints require authentication
   - Internal endpoints not exposed publicly
   - Rate limiting on all SMS operations

3. **Audit Logging**
   - Log all SMS operations
   - Track admin actions
   - Store provider responses

## Implementation Flow

1. Admin adds SMSO provider with API key
2. System encrypts and stores configuration
3. Admin activates SMSO as default provider
4. Checkout flow calls SMS service
5. SMS Manager selects active provider (SMSO)
6. SMSO provider sends SMS via API
7. Response logged and returned to checkout
8. Background job checks delivery status

## Error Handling

1. **Provider Errors**
   - Invalid API key → Alert admin
   - Insufficient credit → Alert + failover
   - API timeout → Retry with backoff

2. **System Errors**
   - No active provider → Use mock in dev, error in prod
   - Database errors → Queue for retry
   - Network errors → Exponential backoff

## Monitoring

1. **Metrics to Track**
   - SMS sent/delivered/failed per provider
   - Average delivery time
   - Cost per provider
   - API response times
   - Error rates

2. **Alerts**
   - Low credit balance
   - High failure rate
   - Provider API down
   - Unusual usage patterns