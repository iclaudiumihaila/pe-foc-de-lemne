"""
Analytics Data Models for Local Producer Web Application

This module provides data models for analytics tracking, business intelligence,
and performance monitoring with Romanian marketplace optimization.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from bson import ObjectId
from app.database import get_database


@dataclass
class AnalyticsEvent:
    """Base analytics event model"""
    event_type: str
    event_category: str
    event_action: str
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    page_url: str = ""
    referrer: str = ""
    user_agent: str = ""
    ip_address: str = ""
    data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return result


@dataclass
class EcommerceEvent(AnalyticsEvent):
    """E-commerce specific analytics event"""
    product_id: Optional[str] = None
    product_name: Optional[str] = ""
    product_category: Optional[str] = ""
    producer_name: Optional[str] = ""
    price: Optional[float] = 0.0
    quantity: Optional[int] = 1
    currency: str = "RON"
    transaction_id: Optional[str] = None
    revenue: Optional[float] = 0.0


@dataclass
class PerformanceMetric:
    """Performance monitoring data"""
    metric_name: str
    metric_value: float
    metric_unit: str
    timestamp: datetime
    page_url: str
    user_agent: str = ""
    connection_type: str = ""
    device_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class UserJourneyStep:
    """User journey tracking"""
    step_name: str
    step_order: int
    timestamp: datetime
    session_id: str
    page_url: str
    action_type: str  # 'page_view', 'click', 'form_submit', etc.
    duration_ms: Optional[int] = None
    data: Dict[str, Any] = None


@dataclass
class BusinessKPI:
    """Romanian marketplace business KPIs"""
    kpi_name: str
    kpi_value: float
    timestamp: datetime
    time_period: str  # 'daily', 'weekly', 'monthly'
    market: str = "romania"
    currency: str = "RON"
    category: str = ""
    additional_data: Dict[str, Any] = None


class AnalyticsRepository:
    """Repository for analytics data operations"""
    
    def __init__(self):
        self.db = get_database()
        self.events_collection = self.db['analytics_events']
        self.performance_collection = self.db['performance_metrics']
        self.journey_collection = self.db['user_journeys']
        self.kpi_collection = self.db['business_kpis']
        self.session_collection = self.db['user_sessions']
        
        # Create indexes for performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for analytics collections"""
        try:
            # Events collection indexes
            self.events_collection.create_index([
                ("timestamp", -1),
                ("event_category", 1),
                ("session_id", 1)
            ])
            
            self.events_collection.create_index([
                ("event_type", 1),
                ("timestamp", -1)
            ])
            
            # Performance collection indexes
            self.performance_collection.create_index([
                ("timestamp", -1),
                ("metric_name", 1)
            ])
            
            # Journey collection indexes
            self.journey_collection.create_index([
                ("session_id", 1),
                ("step_order", 1),
                ("timestamp", -1)
            ])
            
            # KPI collection indexes
            self.kpi_collection.create_index([
                ("timestamp", -1),
                ("kpi_name", 1),
                ("time_period", 1)
            ])
            
            # Session collection indexes
            self.session_collection.create_index([
                ("session_id", 1),
                ("start_time", -1)
            ])
            
        except Exception as e:
            print(f"Warning: Could not create analytics indexes: {e}")
    
    def store_event(self, event: AnalyticsEvent) -> str:
        """Store analytics event in database"""
        try:
            event_doc = event.to_dict()
            event_doc['created_at'] = datetime.now(timezone.utc)
            
            result = self.events_collection.insert_one(event_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing analytics event: {e}")
            raise
    
    def store_events_batch(self, events: List[AnalyticsEvent]) -> List[str]:
        """Store multiple analytics events in batch"""
        try:
            event_docs = []
            created_at = datetime.now(timezone.utc)
            
            for event in events:
                event_doc = event.to_dict()
                event_doc['created_at'] = created_at
                event_docs.append(event_doc)
            
            result = self.events_collection.insert_many(event_docs)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            print(f"Error storing analytics events batch: {e}")
            raise
    
    def store_performance_metric(self, metric: PerformanceMetric) -> str:
        """Store performance metric"""
        try:
            metric_doc = metric.to_dict()
            metric_doc['created_at'] = datetime.now(timezone.utc)
            
            result = self.performance_collection.insert_one(metric_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing performance metric: {e}")
            raise
    
    def store_journey_step(self, step: UserJourneyStep) -> str:
        """Store user journey step"""
        try:
            step_doc = asdict(step)
            step_doc['timestamp'] = step.timestamp.isoformat()
            step_doc['created_at'] = datetime.now(timezone.utc)
            
            result = self.journey_collection.insert_one(step_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing journey step: {e}")
            raise
    
    def store_business_kpi(self, kpi: BusinessKPI) -> str:
        """Store business KPI"""
        try:
            kpi_doc = asdict(kpi)
            kpi_doc['timestamp'] = kpi.timestamp.isoformat()
            kpi_doc['created_at'] = datetime.now(timezone.utc)
            
            result = self.kpi_collection.insert_one(kpi_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing business KPI: {e}")
            raise
    
    def get_events(self, filters: Dict[str, Any], limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Retrieve analytics events with filters"""
        try:
            # Build MongoDB query from filters
            query = {}
            
            if 'start_date' in filters and 'end_date' in filters:
                query['timestamp'] = {
                    '$gte': filters['start_date'],
                    '$lte': filters['end_date']
                }
            
            if 'event_category' in filters:
                query['event_category'] = filters['event_category']
            
            if 'event_type' in filters:
                query['event_type'] = filters['event_type']
            
            if 'session_id' in filters:
                query['session_id'] = filters['session_id']
            
            cursor = self.events_collection.find(query).sort('timestamp', -1).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error retrieving events: {e}")
            raise
    
    def get_performance_metrics(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve performance metrics"""
        try:
            query = {}
            
            if 'start_date' in filters and 'end_date' in filters:
                query['timestamp'] = {
                    '$gte': filters['start_date'],
                    '$lte': filters['end_date']
                }
            
            if 'metric_name' in filters:
                query['metric_name'] = filters['metric_name']
            
            cursor = self.performance_collection.find(query).sort('timestamp', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error retrieving performance metrics: {e}")
            raise
    
    def get_user_journey(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve user journey for a session"""
        try:
            cursor = self.journey_collection.find({
                'session_id': session_id
            }).sort('step_order', 1)
            return list(cursor)
        except Exception as e:
            print(f"Error retrieving user journey: {e}")
            raise
    
    def get_business_kpis(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve business KPIs"""
        try:
            query = {}
            
            if 'start_date' in filters and 'end_date' in filters:
                query['timestamp'] = {
                    '$gte': filters['start_date'],
                    '$lte': filters['end_date']
                }
            
            if 'kpi_name' in filters:
                query['kpi_name'] = filters['kpi_name']
            
            if 'time_period' in filters:
                query['time_period'] = filters['time_period']
            
            cursor = self.kpi_collection.find(query).sort('timestamp', -1)
            return list(cursor)
        except Exception as e:
            print(f"Error retrieving business KPIs: {e}")
            raise
    
    def get_analytics_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics summary for a time period"""
        try:
            pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_date.isoformat(),
                            '$lte': end_date.isoformat()
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'event_category': '$event_category',
                            'event_action': '$event_action'
                        },
                        'count': {'$sum': 1},
                        'unique_sessions': {'$addToSet': '$session_id'}
                    }
                },
                {
                    '$project': {
                        'event_category': '$_id.event_category',
                        'event_action': '$_id.event_action',
                        'count': 1,
                        'unique_sessions_count': {'$size': '$unique_sessions'}
                    }
                }
            ]
            
            results = list(self.events_collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error getting analytics summary: {e}")
            raise
    
    def get_romanian_marketplace_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Romanian marketplace specific metrics"""
        try:
            # Product category performance
            category_pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_date.isoformat(),
                            '$lte': end_date.isoformat()
                        },
                        'event_type': 'ecommerce',
                        'product_category': {'$exists': True}
                    }
                },
                {
                    '$group': {
                        '_id': '$product_category',
                        'views': {'$sum': {'$cond': [{'$eq': ['$event_action', 'product_viewed']}, 1, 0]}},
                        'purchases': {'$sum': {'$cond': [{'$eq': ['$event_action', 'purchase']}, 1, 0]}},
                        'cart_adds': {'$sum': {'$cond': [{'$eq': ['$event_action', 'add_to_cart']}, 1, 0]}},
                        'revenue': {'$sum': {'$cond': [{'$eq': ['$event_action', 'purchase']}, '$revenue', 0]}}
                    }
                }
            ]
            
            category_metrics = list(self.events_collection.aggregate(category_pipeline))
            
            # Producer performance
            producer_pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_date.isoformat(),
                            '$lte': end_date.isoformat()
                        },
                        'event_type': 'ecommerce',
                        'producer_name': {'$exists': True, '$ne': ''}
                    }
                },
                {
                    '$group': {
                        '_id': '$producer_name',
                        'product_views': {'$sum': {'$cond': [{'$eq': ['$event_action', 'product_viewed']}, 1, 0]}},
                        'sales': {'$sum': {'$cond': [{'$eq': ['$event_action', 'purchase']}, 1, 0]}},
                        'revenue': {'$sum': {'$cond': [{'$eq': ['$event_action', 'purchase']}, '$revenue', 0]}}
                    }
                },
                {'$sort': {'revenue': -1}},
                {'$limit': 20}
            ]
            
            producer_metrics = list(self.events_collection.aggregate(producer_pipeline))
            
            return {
                'category_performance': category_metrics,
                'producer_performance': producer_metrics,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        except Exception as e:
            print(f"Error getting Romanian marketplace metrics: {e}")
            raise
    
    def get_conversion_funnel(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get conversion funnel data"""
        try:
            pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_date.isoformat(),
                            '$lte': end_date.isoformat()
                        },
                        'event_action': {'$in': ['product_viewed', 'add_to_cart', 'begin_checkout', 'purchase']}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'session_id': '$session_id',
                            'event_action': '$event_action'
                        },
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$group': {
                        '_id': '$_id.event_action',
                        'unique_sessions': {'$sum': 1},
                        'total_events': {'$sum': '$count'}
                    }
                }
            ]
            
            funnel_data = list(self.events_collection.aggregate(pipeline))
            
            # Calculate conversion rates
            funnel_dict = {item['_id']: item for item in funnel_data}
            
            result = {
                'product_views': funnel_dict.get('product_viewed', {}).get('unique_sessions', 0),
                'cart_additions': funnel_dict.get('add_to_cart', {}).get('unique_sessions', 0),
                'checkout_starts': funnel_dict.get('begin_checkout', {}).get('unique_sessions', 0),
                'purchases': funnel_dict.get('purchase', {}).get('unique_sessions', 0)
            }
            
            # Calculate rates
            if result['product_views'] > 0:
                result['cart_conversion_rate'] = result['cart_additions'] / result['product_views']
                result['checkout_conversion_rate'] = result['checkout_starts'] / result['product_views'] 
                result['purchase_conversion_rate'] = result['purchases'] / result['product_views']
            
            return result
        except Exception as e:
            print(f"Error getting conversion funnel: {e}")
            raise
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.now(timezone.utc).replace(days=-days_to_keep)
            cutoff_iso = cutoff_date.isoformat()
            
            # Clean up events
            events_result = self.events_collection.delete_many({
                'timestamp': {'$lt': cutoff_iso}
            })
            
            # Clean up performance metrics
            performance_result = self.performance_collection.delete_many({
                'timestamp': {'$lt': cutoff_iso}
            })
            
            # Clean up journey data
            journey_result = self.journey_collection.delete_many({
                'timestamp': {'$lt': cutoff_iso}
            })
            
            return {
                'events_deleted': events_result.deleted_count,
                'performance_deleted': performance_result.deleted_count,
                'journey_deleted': journey_result.deleted_count,
                'cutoff_date': cutoff_iso
            }
        except Exception as e:
            print(f"Error cleaning up analytics data: {e}")
            raise


# Global analytics repository instance
analytics_repo = None

def get_analytics_repo():
    """Get or create the analytics repository instance."""
    global analytics_repo
    if analytics_repo is None:
        analytics_repo = AnalyticsRepository()
    return analytics_repo