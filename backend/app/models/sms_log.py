"""
SMS Log Model for tracking all SMS operations
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from bson import ObjectId
from app.database import get_database

class SmsLog:
    """
    Model for logging SMS operations with detailed tracking.
    """
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_DELIVERED = 'delivered'
    STATUS_FAILED = 'failed'
    STATUS_EXPIRED = 'expired'
    
    def __init__(self, data: Dict[str, Any] = None):
        """Initialize SMS log instance"""
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.provider = data.get('provider', '')
        self.phone_number = data.get('phone_number', '')
        self.phone_masked = data.get('phone_masked', '')
        self.message_type = data.get('message_type', '')
        self.message = data.get('message', '')
        self.status = data.get('status', self.STATUS_PENDING)
        self.response_token = data.get('response_token')
        self.provider_response = data.get('provider_response', {})
        self.cost = data.get('cost', 0.0)  # In eurocents
        self.cost_currency = data.get('cost_currency', 'EUR')
        self.delivery_time = data.get('delivery_time')  # Seconds
        self.error = data.get('error')
        self.retry_count = data.get('retry_count', 0)
        self.metadata = data.get('metadata', {})
        self.created_at = data.get('created_at', datetime.utcnow())
        self.sent_at = data.get('sent_at')
        self.delivered_at = data.get('delivered_at')
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.expires_at = data.get('expires_at')
    
    def mask_phone_number(self, phone: str) -> str:
        """Mask phone number for privacy"""
        if len(phone) > 4:
            return f"****{phone[-4:]}"
        return "****"
    
    def calculate_delivery_time(self) -> Optional[float]:
        """Calculate delivery time in seconds"""
        if self.sent_at and self.delivered_at:
            delta = self.delivered_at - self.sent_at
            return delta.total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            '_id': self._id,
            'provider': self.provider,
            'phone_number': self.phone_number,
            'phone_masked': self.phone_masked,
            'message_type': self.message_type,
            'message': self.message,
            'status': self.status,
            'response_token': self.response_token,
            'provider_response': self.provider_response,
            'cost': self.cost,
            'cost_currency': self.cost_currency,
            'delivery_time': self.delivery_time,
            'error': self.error,
            'retry_count': self.retry_count,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'sent_at': self.sent_at,
            'delivered_at': self.delivered_at,
            'updated_at': self.updated_at,
            'expires_at': self.expires_at
        }
    
    def save(self) -> ObjectId:
        """Save log to database"""
        db = get_database()
        collection = db.sms_logs
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        # Mask phone number for privacy
        if self.phone_number and not self.phone_masked:
            self.phone_masked = self.mask_phone_number(self.phone_number)
        
        # Calculate delivery time if applicable
        if self.status == self.STATUS_DELIVERED and not self.delivery_time:
            self.delivery_time = self.calculate_delivery_time()
        
        # Set expiration for log retention (90 days)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=90)
        
        # Prepare document
        doc = self.to_dict()
        
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
        
        return self._id
    
    @classmethod
    def find_by_id(cls, log_id: ObjectId) -> Optional['SmsLog']:
        """Find log by ID"""
        db = get_database()
        doc = db.sms_logs.find_one({'_id': log_id})
        return cls(doc) if doc else None
    
    @classmethod
    def find_by_response_token(cls, token: str) -> Optional['SmsLog']:
        """Find log by provider response token"""
        db = get_database()
        doc = db.sms_logs.find_one({'response_token': token})
        return cls(doc) if doc else None
    
    @classmethod
    def get_logs(cls, filters: Dict[str, Any] = None, 
                 limit: int = 100, skip: int = 0) -> List['SmsLog']:
        """Get logs with filtering and pagination"""
        db = get_database()
        query = filters or {}
        
        logs = []
        cursor = db.sms_logs.find(query).sort('created_at', -1).skip(skip).limit(limit)
        
        for doc in cursor:
            logs.append(cls(doc))
        
        return logs
    
    @classmethod
    def count_logs(cls, filters: Dict[str, Any] = None) -> int:
        """Count logs matching filters"""
        db = get_database()
        query = filters or {}
        return db.sms_logs.count_documents(query)
    
    @classmethod
    def get_statistics(cls, provider: str = None, 
                      start_date: datetime = None,
                      end_date: datetime = None) -> Dict[str, Any]:
        """Get SMS statistics for a provider and date range"""
        db = get_database()
        
        # Build match query
        match_query = {}
        if provider:
            match_query['provider'] = provider
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            match_query['created_at'] = date_query
        
        # Aggregation pipeline
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': {
                        'provider': '$provider',
                        'status': '$status'
                    },
                    'count': {'$sum': 1},
                    'total_cost': {'$sum': '$cost'},
                    'avg_delivery_time': {'$avg': '$delivery_time'}
                }
            },
            {
                '$group': {
                    '_id': '$_id.provider',
                    'stats': {
                        '$push': {
                            'status': '$_id.status',
                            'count': '$count',
                            'total_cost': '$total_cost',
                            'avg_delivery_time': '$avg_delivery_time'
                        }
                    },
                    'total_count': {'$sum': '$count'},
                    'total_cost': {'$sum': '$total_cost'}
                }
            }
        ]
        
        results = list(db.sms_logs.aggregate(pipeline))
        
        # Format results
        statistics = {}
        for result in results:
            provider_name = result['_id']
            stats_by_status = {
                stat['status']: {
                    'count': stat['count'],
                    'cost': stat['total_cost'],
                    'avg_delivery_time': stat['avg_delivery_time']
                }
                for stat in result['stats']
            }
            
            statistics[provider_name] = {
                'total_count': result['total_count'],
                'total_cost': result['total_cost'],
                'by_status': stats_by_status
            }
        
        return statistics
    
    @classmethod
    def create_indexes(cls):
        """Create database indexes for SMS logs"""
        db = get_database()
        collection = db.sms_logs
        
        # Single field indexes
        collection.create_index('phone_masked')  # For privacy-safe queries
        collection.create_index('provider')
        collection.create_index('status')
        collection.create_index('response_token')
        collection.create_index('message_type')
        
        # Date index for queries and sorting
        collection.create_index([('created_at', -1)])
        
        # Compound indexes for common queries
        # Admin dashboard: filter by provider and date
        collection.create_index([
            ('provider', 1),
            ('created_at', -1)
        ])
        
        # Status tracking: find pending/failed by provider
        collection.create_index([
            ('provider', 1),
            ('status', 1),
            ('created_at', -1)
        ])
        
        # Phone number history: find by phone and date
        collection.create_index([
            ('phone_masked', 1),
            ('created_at', -1)
        ])
        
        # Cost analysis: by provider and date range
        collection.create_index([
            ('provider', 1),
            ('created_at', 1),
            ('cost', 1)
        ])
        
        # TTL index for automatic log cleanup (90 days)
        collection.create_index(
            'expires_at',
            expireAfterSeconds=0
        )
        
        # Text index for message search (optional)
        collection.create_index([('message', 'text')])
        
        print("SMS log indexes created successfully")
    
    @classmethod
    def cleanup_old_logs(cls, days: int = 90):
        """Manually cleanup logs older than specified days"""
        db = get_database()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = db.sms_logs.delete_many({
            'created_at': {'$lt': cutoff_date}
        })
        
        return result.deleted_count