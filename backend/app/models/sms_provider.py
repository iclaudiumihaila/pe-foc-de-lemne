"""
SMS Provider Model for managing multiple SMS service providers
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from bson import ObjectId
import json
from app.database import get_database
from app.utils.encryption import get_encryption_manager, get_sms_encryption_manager

class SmsProvider:
    """
    Model for SMS provider configuration and management.
    Supports multiple providers with encrypted API credentials.
    """
    
    # Provider types
    PROVIDER_SMSO = 'smso'
    PROVIDER_TWILIO = 'twilio'
    PROVIDER_VONAGE = 'vonage'
    PROVIDER_MOCK = 'mock'
    
    # Message types
    MSG_TYPE_OTP = 'otp'
    MSG_TYPE_TRANSACTIONAL = 'transactional'
    MSG_TYPE_MARKETING = 'marketing'
    
    def __init__(self, data: Dict[str, Any] = None):
        """Initialize SMS provider instance"""
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.name = data.get('name', '')
        self.slug = data.get('slug', '')
        self.provider_type = data.get('provider_type', '')
        self.is_active = data.get('is_active', False)
        self.is_default = data.get('is_default', False)
        self.priority = data.get('priority', 100)
        self.config = data.get('config', {})
        self.features = data.get('features', [])
        self.rate_limits = data.get('rate_limits', {})
        self.usage_stats = data.get('usage_stats', {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'total_cost': 0.0,
            'last_used': None
        })
        self.health_status = data.get('health_status', {
            'is_healthy': True,
            'last_check': None,
            'error_message': None
        })
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        
        # Get encryption manager
        self._encryption_manager = None
    
    @property
    def encryption_manager(self):
        """Get encryption manager lazily"""
        if self._encryption_manager is None:
            try:
                self._encryption_manager = get_sms_encryption_manager()
            except:
                # Fallback to default encryption manager
                from app.utils.encryption import EncryptionManager
                self._encryption_manager = EncryptionManager(
                    key_env_var='SMS_ENCRYPTION_KEY',
                    salt_env_var='SMS_ENCRYPTION_SALT'
                )
        return self._encryption_manager
    
    def encrypt_config_value(self, key: str, value: str) -> None:
        """Encrypt a configuration value"""
        if value:
            encrypted = self.encryption_manager.encrypt(value)
            self.config[f"{key}_encrypted"] = encrypted
            # Don't store the plain value
            if key in self.config:
                del self.config[key]
    
    def decrypt_config_value(self, key: str) -> Optional[str]:
        """Decrypt a configuration value"""
        encrypted_key = f"{key}_encrypted"
        if encrypted_key in self.config:
            try:
                encrypted = self.config[encrypted_key]
                return self.encryption_manager.decrypt_sensitive_data(encrypted)
            except Exception as e:
                print(f"Error decrypting {key}: {e}")
                return None
        return self.config.get(key)
    
    def validate(self) -> List[str]:
        """Validate provider data"""
        errors = []
        
        if not self.name:
            errors.append("Provider name is required")
        
        if not self.slug:
            errors.append("Provider slug is required")
        elif not self.slug.replace('_', '').replace('-', '').isalnum():
            errors.append("Provider slug must be alphanumeric with underscores/hyphens")
        
        if not self.provider_type:
            errors.append("Provider type is required")
        
        # Validate provider-specific config
        if self.provider_type == self.PROVIDER_SMSO:
            if not self.decrypt_config_value('api_key'):
                errors.append("SMSO API key is required")
            # Sender ID is optional - SMSO will use default if not provided
        
        return errors
    
    def encrypt_config_value(self, key: str, value: str) -> None:
        """Encrypt and store a configuration value"""
        if not value:
            return
            
        encrypted = self.encryption_manager.encrypt_sensitive_data(value)
        self.config[f"{key}_encrypted"] = encrypted
        
        # Remove plain text value if it exists
        if key in self.config:
            del self.config[key]
    
    def set_api_key(self, api_key: str) -> None:
        """Set and encrypt API key"""
        self.encrypt_config_value('api_key', api_key)
    
    def get_api_key(self) -> Optional[str]:
        """Get decrypted API key"""
        return self.decrypt_config_value('api_key')
    
    def update_usage_stats(self, sent: int = 0, delivered: int = 0, 
                          failed: int = 0, cost: float = 0.0) -> None:
        """Update usage statistics"""
        self.usage_stats['total_sent'] += sent
        self.usage_stats['total_delivered'] += delivered
        self.usage_stats['total_failed'] += failed
        self.usage_stats['total_cost'] += cost
        self.usage_stats['last_used'] = datetime.utcnow()
    
    def update_health_status(self, is_healthy: bool, error_message: str = None) -> None:
        """Update health check status"""
        self.health_status['is_healthy'] = is_healthy
        self.health_status['last_check'] = datetime.utcnow()
        self.health_status['error_message'] = error_message
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            '_id': self._id,
            'name': self.name,
            'slug': self.slug,
            'provider_type': self.provider_type,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'config': self.config.copy(),
            'features': self.features,
            'rate_limits': self.rate_limits,
            'usage_stats': self.usage_stats,
            'health_status': self.health_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Remove sensitive data unless explicitly requested
        if not include_sensitive:
            # Remove encrypted values from config
            data['config'] = {k: v for k, v in self.config.items() 
                            if not k.endswith('_encrypted')}
        
        return data
    
    def save(self) -> ObjectId:
        """Save provider to database"""
        db = get_database()
        collection = db.sms_providers
        
        # Validate before saving
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        # Prepare document
        doc = self.to_dict(include_sensitive=True)
        
        if self._id:
            # Update existing
            doc.pop('_id', None)
            collection.update_one(
                {'_id': self._id},
                {'$set': doc}
            )
        else:
            # Insert new
            doc.pop('_id', None)
            result = collection.insert_one(doc)
            self._id = result.inserted_id
        
        # If setting as default, unset other defaults
        if self.is_default:
            collection.update_many(
                {'_id': {'$ne': self._id}},
                {'$set': {'is_default': False}}
            )
        
        return self._id
    
    def delete(self):
        """Delete this provider from the database"""
        db = get_database()
        db.sms_providers.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_id(cls, provider_id: Union[str, ObjectId]) -> Optional['SmsProvider']:
        """Find provider by ID"""
        db = get_database()
        if isinstance(provider_id, str):
            try:
                provider_id = ObjectId(provider_id)
            except:
                return None
        doc = db.sms_providers.find_one({'_id': provider_id})
        return cls(doc) if doc else None
    
    @classmethod
    def get_collection(cls):
        """Get the MongoDB collection for SmsProvider"""
        db = get_database()
        return db.sms_providers
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['SmsProvider']:
        """Find provider by slug"""
        db = get_database()
        doc = db.sms_providers.find_one({'slug': slug})
        return cls(doc) if doc else None
    
    @classmethod
    def get_active_provider(cls) -> Optional['SmsProvider']:
        """Get the active default provider"""
        db = get_database()
        # First try to get default provider
        doc = db.sms_providers.find_one({
            'is_active': True,
            'is_default': True
        })
        
        # If no default, get any active provider
        if not doc:
            doc = db.sms_providers.find_one({'is_active': True})
        
        return cls(doc) if doc else None
    
    @classmethod
    def get_all_providers(cls, active_only: bool = False) -> List['SmsProvider']:
        """Get all providers"""
        db = get_database()
        query = {'is_active': True} if active_only else {}
        
        providers = []
        for doc in db.sms_providers.find(query).sort('name', 1):
            providers.append(cls(doc))
        
        return providers
    
    @classmethod
    def count_active(cls) -> int:
        """Count active SMS providers"""
        db = get_database()
        return db.sms_providers.count_documents({'is_active': True})
    
    @classmethod
    def create_indexes(cls):
        """Create database indexes"""
        db = get_database()
        collection = db.sms_providers
        
        # Unique index on slug
        collection.create_index('slug', unique=True)
        
        # Index for finding active providers
        collection.create_index([
            ('is_active', 1),
            ('is_default', -1)
        ])
        
        # Index for provider type
        collection.create_index('provider_type')
        
        print("SMS provider indexes created successfully")
    
    @classmethod
    def seed_mock_provider(cls):
        """Create a mock provider for development"""
        mock_provider = cls({
            'name': 'Mock Provider',
            'slug': 'mock',
            'provider_type': cls.PROVIDER_MOCK,
            'is_active': True,
            'is_default': True,
            'config': {
                'delay_seconds': 0,
                'success_rate': 1.0,
                'cost_per_sms': 0.0
            },
            'features': [cls.MSG_TYPE_OTP, cls.MSG_TYPE_TRANSACTIONAL],
            'rate_limits': {
                'per_minute': 100,
                'per_hour': 1000,
                'per_day': 10000
            }
        })
        
        # Check if already exists
        existing = cls.find_by_slug('mock')
        if not existing:
            mock_provider.save()
            print("Mock SMS provider created")
        
        return mock_provider