"""
Customer Phone Model for Simplified Checkout
Task ID: 05

This model manages customer phone numbers and their associated addresses
for the simplified checkout flow.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import get_database
from app.utils.validators import sanitize_string

logger = logging.getLogger(__name__)


class CustomerPhone:
    """Model for managing customer phones and addresses"""
    
    COLLECTION_NAME = 'customer_phones'
    
    # Validation constants
    PHONE_PATTERN = re.compile(r'^(\+40|0)7[0-9]{8}$')
    NAME_PATTERN = re.compile(r'^[a-zA-ZăîâșțĂÎÂȘȚ\s\-\']+$')
    NAME_MIN_LENGTH = 3
    NAME_MAX_LENGTH = 100
    STREET_MIN_LENGTH = 5
    STREET_MAX_LENGTH = 200
    CITY_MIN_LENGTH = 2
    CITY_MAX_LENGTH = 50
    POSTAL_CODE_PATTERN = re.compile(r'^[0-9]{6}$')
    MAX_ADDRESSES = 50
    
    # Romanian counties
    VALID_COUNTIES = [
        'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani',
        'Brașov', 'Brăila', 'București', 'Buzău', 'Caraș-Severin', 'Călărași',
        'Cluj', 'Constanța', 'Covasna', 'Dâmbovița', 'Dolj', 'Galați', 'Giurgiu',
        'Gorj', 'Harghita', 'Hunedoara', 'Ialomița', 'Iași', 'Ilfov', 'Maramureș',
        'Mehedinți', 'Mureș', 'Neamț', 'Olt', 'Prahova', 'Satu Mare', 'Sălaj',
        'Sibiu', 'Suceava', 'Teleorman', 'Timiș', 'Tulcea', 'Vaslui', 'Vâlcea', 'Vrancea'
    ]
    
    def __init__(self, data: Dict[str, Any] = None):
        """Initialize CustomerPhone from dictionary data"""
        if data is None:
            data = {}
            
        self._id = data.get('_id')
        self.phone = data.get('phone', '')
        self.name = data.get('name', '')
        self.addresses = data.get('addresses', [])
        self.verification = data.get('verification', {
            'last_code_sent': None,
            'attempts_today': 0,
            'blocked_until': None
        })
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.total_orders = data.get('total_orders', 0)
        self.last_order_date = data.get('last_order_date')
        self.__v = data.get('__v', 0)  # Version for optimistic locking
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone to international format"""
        phone = re.sub(r'\s+', '', phone)  # Remove spaces
        if phone.startswith('0'):
            phone = '+4' + phone  # Convert to international
        return phone
    
    def validate_phone(self, phone: str) -> Optional[str]:
        """Validate phone number format"""
        if not phone:
            return "Numărul de telefon este obligatoriu"
        
        if not self.PHONE_PATTERN.match(phone):
            return "Format invalid. Exemplu: 0712345678"
        
        return None
    
    def validate_name(self, name: str) -> Optional[str]:
        """Validate customer name"""
        if not name:
            return "Numele este obligatoriu"
        
        name = name.strip()
        if len(name) < self.NAME_MIN_LENGTH:
            return f"Numele trebuie să aibă minim {self.NAME_MIN_LENGTH} caractere"
        
        if len(name) > self.NAME_MAX_LENGTH:
            return f"Numele trebuie să aibă maxim {self.NAME_MAX_LENGTH} caractere"
        
        if not self.NAME_PATTERN.match(name):
            return "Numele conține caractere invalide"
        
        return None
    
    def validate_address(self, address: Dict[str, Any]) -> Dict[str, str]:
        """Validate address fields"""
        errors = {}
        
        # Street validation
        street = address.get('street', '').strip()
        if not street:
            errors['street'] = "Strada este obligatorie"
        elif len(street) < self.STREET_MIN_LENGTH:
            errors['street'] = f"Minim {self.STREET_MIN_LENGTH} caractere"
        elif len(street) > self.STREET_MAX_LENGTH:
            errors['street'] = f"Maxim {self.STREET_MAX_LENGTH} caractere"
        
        # City validation
        city = address.get('city', '').strip()
        if not city:
            errors['city'] = "Orașul este obligatoriu"
        elif len(city) < self.CITY_MIN_LENGTH:
            errors['city'] = f"Minim {self.CITY_MIN_LENGTH} caractere"
        elif len(city) > self.CITY_MAX_LENGTH:
            errors['city'] = f"Maxim {self.CITY_MAX_LENGTH} caractere"
        
        # County validation
        county = address.get('county', '')
        if not county:
            errors['county'] = "Județul este obligatoriu"
        elif county not in self.VALID_COUNTIES:
            errors['county'] = "Județ invalid"
        
        # Postal code validation
        postal_code = address.get('postal_code', '').strip()
        if not postal_code:
            errors['postal_code'] = "Codul poștal este obligatoriu"
        elif not self.POSTAL_CODE_PATTERN.match(postal_code):
            errors['postal_code'] = "Format invalid (6 cifre)"
        
        return errors
    
    def can_send_verification_code(self) -> bool:
        """Check if phone can receive verification code"""
        # Check if blocked
        if self.verification.get('blocked_until'):
            if self.verification['blocked_until'] > datetime.utcnow():
                return False
        
        # Check daily limit (3 per day)
        last_sent = self.verification.get('last_code_sent')
        if last_sent and last_sent.date() == datetime.utcnow().date():
            if self.verification.get('attempts_today', 0) >= 3:
                return False
        
        return True
    
    def record_verification_attempt(self):
        """Record that a verification code was sent"""
        now = datetime.utcnow()
        last_sent = self.verification.get('last_code_sent')
        
        # Reset counter if new day
        if not last_sent or last_sent.date() != now.date():
            self.verification['attempts_today'] = 0
        
        self.verification['attempts_today'] += 1
        self.verification['last_code_sent'] = now
        
        # Block if too many attempts
        if self.verification['attempts_today'] >= 3:
            self.verification['blocked_until'] = now + timedelta(hours=24)
    
    def add_address(self, address: Dict[str, Any]) -> Optional[ObjectId]:
        """Add new address to customer"""
        # Check limit
        if len(self.addresses) >= self.MAX_ADDRESSES:
            raise ValueError(f"Maximum {self.MAX_ADDRESSES} addresses allowed")
        
        # Create address with metadata
        address_id = ObjectId()
        new_address = {
            '_id': address_id,
            'street': sanitize_string(address['street']),
            'city': sanitize_string(address['city']),
            'county': address['county'],
            'postal_code': address['postal_code'],
            'notes': sanitize_string(address.get('notes', '')),
            'is_default': address.get('is_default', len(self.addresses) == 0),
            'usage_count': 0,
            'created_at': datetime.utcnow(),
            'last_used': None
        }
        
        # If setting as default, unset others
        if new_address['is_default']:
            for addr in self.addresses:
                addr['is_default'] = False
        
        self.addresses.append(new_address)
        return address_id
    
    def update_address(self, address_id: str, updates: Dict[str, Any]):
        """Update existing address"""
        address_id = ObjectId(address_id)
        
        for address in self.addresses:
            if address['_id'] == address_id:
                # Update allowed fields
                if 'street' in updates:
                    address['street'] = sanitize_string(updates['street'])
                if 'city' in updates:
                    address['city'] = sanitize_string(updates['city'])
                if 'county' in updates and updates['county'] in self.VALID_COUNTIES:
                    address['county'] = updates['county']
                if 'postal_code' in updates:
                    address['postal_code'] = updates['postal_code']
                if 'notes' in updates:
                    address['notes'] = sanitize_string(updates['notes'])
                if 'is_default' in updates and updates['is_default']:
                    # Unset other defaults
                    for addr in self.addresses:
                        addr['is_default'] = False
                    address['is_default'] = True
                
                return True
        
        return False
    
    def delete_address(self, address_id: str) -> bool:
        """Delete address by ID"""
        address_id = ObjectId(address_id)
        initial_count = len(self.addresses)
        
        self.addresses = [
            addr for addr in self.addresses 
            if addr['_id'] != address_id
        ]
        
        # If deleted default, set first as default
        if len(self.addresses) > 0 and not any(addr['is_default'] for addr in self.addresses):
            self.addresses[0]['is_default'] = True
        
        return len(self.addresses) < initial_count
    
    def mark_address_used(self, address_id: str):
        """Mark address as used for order"""
        address_id = ObjectId(address_id)
        
        for address in self.addresses:
            if address['_id'] == address_id:
                address['usage_count'] = address.get('usage_count', 0) + 1
                address['last_used'] = datetime.utcnow()
                break
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        data = {
            'id': str(self._id) if self._id else None,
            'name': self.name,
            'phone': self.phone if include_sensitive else self.phone[-4:],  # Show last 4 digits
            'addresses': [
                {
                    'id': str(addr['_id']),
                    'street': addr['street'],
                    'city': addr['city'],
                    'county': addr['county'],
                    'postal_code': addr['postal_code'],
                    'notes': addr.get('notes', ''),
                    'is_default': addr.get('is_default', False),
                    'usage_count': addr.get('usage_count', 0)
                }
                for addr in self.addresses
            ],
            'total_orders': self.total_orders,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data['verification'] = self.verification
            data['__v'] = self.__v
        
        return data
    
    def save(self) -> bool:
        """Save or update customer phone record"""
        try:
            db = get_database()
            collection = db[self.COLLECTION_NAME]
            
            # Normalize phone before saving
            self.phone = self.normalize_phone(self.phone)
            
            # Update timestamp
            self.updated_at = datetime.utcnow()
            
            # Prepare document
            doc = {
                'phone': self.phone,
                'name': self.name,
                'addresses': self.addresses,
                'verification': self.verification,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'total_orders': self.total_orders,
                'last_order_date': self.last_order_date,
                '__v': self.__v
            }
            
            if self._id:
                # Update with optimistic locking
                result = collection.replace_one(
                    {'_id': self._id, '__v': self.__v},
                    doc
                )
                if result.matched_count == 0:
                    raise ValueError("Concurrent update detected")
                self.__v += 1
            else:
                # Insert new
                result = collection.insert_one(doc)
                self._id = result.inserted_id
            
            return True
            
        except DuplicateKeyError:
            logger.error(f"Phone number already exists: {self.phone}")
            raise ValueError("Numărul de telefon există deja")
        except Exception as e:
            logger.error(f"Error saving customer phone: {str(e)}")
            raise
    
    @classmethod
    def find_by_phone(cls, phone: str) -> Optional['CustomerPhone']:
        """Find customer by phone number"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            # Normalize phone for search
            normalized_phone = cls().normalize_phone(phone)
            
            doc = collection.find_one({'phone': normalized_phone})
            if doc:
                return cls(doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding customer phone: {str(e)}")
            return None
    
    @classmethod
    def create_or_update(cls, phone: str, name: str) -> 'CustomerPhone':
        """Create new or update existing customer"""
        customer = cls.find_by_phone(phone)
        
        if customer:
            # Update name if different
            if customer.name != name:
                customer.name = name
                customer.save()
        else:
            # Create new
            customer = cls({
                'phone': phone,
                'name': name
            })
            customer.save()
        
        return customer