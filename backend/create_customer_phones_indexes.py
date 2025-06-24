#!/usr/bin/env python3
"""
Create indexes for customer_phones collection
Task ID: 04
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database, init_mongodb
from app.config import DevelopmentConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_customer_phones_indexes():
    """Create all required indexes for customer_phones collection"""
    try:
        # Initialize database connection
        init_mongodb(DevelopmentConfig)
        db = get_database()
        
        # Get or create collection
        collection = db.customer_phones
        
        logger.info("Creating indexes for customer_phones collection...")
        
        # 1. Unique index on phone field
        collection.create_index(
            "phone",
            unique=True,
            name="phone_unique"
        )
        logger.info("✓ Created unique index on phone")
        
        # 2. Compound index for rate limiting checks
        collection.create_index(
            [("phone", 1), ("verification.last_code_sent", -1)],
            name="phone_verification_compound"
        )
        logger.info("✓ Created compound index on phone + verification.last_code_sent")
        
        # 3. TTL index for auto-cleanup of blocked records
        # Documents expire 24 hours after blocked_until date
        collection.create_index(
            "verification.blocked_until",
            expireAfterSeconds=86400,  # 24 hours
            name="blocked_until_ttl"
        )
        logger.info("✓ Created TTL index on verification.blocked_until")
        
        # 4. Index for faster address lookups
        collection.create_index(
            [("phone", 1), ("addresses._id", 1)],
            name="phone_address_lookup"
        )
        logger.info("✓ Created index for address lookups")
        
        # Verify all indexes
        indexes = collection.list_indexes()
        logger.info("\nAll indexes on customer_phones collection:")
        for index in indexes:
            logger.info(f"  - {index['name']}: {index['key']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_customer_phones_indexes()
    if success:
        print("\n✅ All indexes created successfully!")
    else:
        print("\n❌ Failed to create indexes")
        sys.exit(1)