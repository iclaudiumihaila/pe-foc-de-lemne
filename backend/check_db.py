#!/usr/bin/env python3
"""Quick database check script"""

from app.database import get_db

try:
    db = get_db()
    collections = list(db.list_collection_names())
    print(f"Database connected successfully")
    print(f"Collections found: {collections}")
    
    # Check document counts
    for collection in collections:
        count = db[collection].count_documents({})
        print(f"  {collection}: {count} documents")
        
    # Check indexes
    print("\nIndexes:")
    for collection in collections:
        indexes = list(db[collection].list_indexes())
        print(f"  {collection}: {len(indexes)} indexes")
        
except Exception as e:
    print(f"Error: {e}")