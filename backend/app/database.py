"""
Database Connection Management for Local Producer Web Application

This module handles MongoDB connection initialization, configuration,
and database operations using PyMongo.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import Config


# Global MongoDB client instance
_mongo_client = None
_database = None


def init_mongodb(config_class=None):
    """
    Initialize MongoDB connection with configuration settings.
    
    Args:
        config_class: Configuration class to use (defaults to Config)
        
    Returns:
        tuple: (client, database) instances
        
    Raises:
        ConnectionFailure: If unable to connect to MongoDB
    """
    global _mongo_client, _database
    
    if config_class is None:
        config_class = Config
    
    try:
        # Create MongoDB client with connection pooling
        _mongo_client = MongoClient(
            config_class.MONGODB_URI,
            maxPoolSize=config_class.MONGODB_MAX_POOL_SIZE,
            minPoolSize=config_class.MONGODB_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second connection timeout
            socketTimeoutMS=10000,   # 10 second socket timeout
        )
        
        # Get database instance
        _database = _mongo_client[config_class.MONGODB_DB_NAME]
        
        # Test the connection
        test_connection()
        
        logging.info(f"MongoDB connected successfully to database: {config_class.MONGODB_DB_NAME}")
        return _mongo_client, _database
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionFailure(f"MongoDB connection failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during MongoDB initialization: {e}")
        raise


def get_database():
    """
    Get the current database instance.
    
    Returns:
        Database: MongoDB database instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_mongodb() first.")
    return _database


def get_client():
    """
    Get the current MongoDB client instance.
    
    Returns:
        MongoClient: MongoDB client instance
        
    Raises:
        RuntimeError: If client not initialized
    """
    if _mongo_client is None:
        raise RuntimeError("MongoDB client not initialized. Call init_mongodb() first.")
    return _mongo_client


def get_collection(collection_name):
    """
    Get a specific collection from the database.
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    database = get_database()
    return database[collection_name]


def test_connection():
    """
    Test MongoDB connection by performing a simple operation.
    
    Returns:
        bool: True if connection successful
        
    Raises:
        ConnectionFailure: If connection test fails
    """
    try:
        # Ping the database to test connection
        _mongo_client.admin.command('ping')
        return True
    except Exception as e:
        logging.error(f"MongoDB connection test failed: {e}")
        raise ConnectionFailure(f"MongoDB connection test failed: {e}")


def close_connection():
    """
    Close MongoDB connection and cleanup resources.
    """
    global _mongo_client, _database
    
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _database = None
        logging.info("MongoDB connection closed")


def create_indexes():
    """
    Create all necessary database indexes for optimal query performance.
    
    This function is idempotent - safe to run multiple times.
    Indexes are created based on the schema specifications in architecture.md.
    
    Returns:
        dict: Summary of index creation results
        
    Raises:
        RuntimeError: If database not initialized
    """
    database = get_database()
    results = {}
    
    try:
        # Users collection indexes
        users_collection = database[Collections.USERS]
        
        # Unique index on phone_number
        users_collection.create_index("phone_number", unique=True, name="phone_number_unique")
        
        # Non-unique index on role for admin queries
        users_collection.create_index("role", name="role_index")
        
        # TTL index on created_at for customer cleanup (optional feature)
        users_collection.create_index("created_at", name="created_at_ttl")
        
        results['users'] = "Indexes created: phone_number (unique), role, created_at"
        logging.info("Users collection indexes created successfully")
        
        # Products collection indexes
        products_collection = database[Collections.PRODUCTS]
        
        # Index on category_id for filtering by category
        products_collection.create_index("category_id", name="category_id_index")
        
        # Index on active status for filtering active products
        products_collection.create_index("active", name="active_index")
        
        # Index on featured status for featured product queries
        products_collection.create_index("featured", name="featured_index")
        
        # Text index on name for search functionality
        products_collection.create_index([("name", "text"), ("description", "text")], name="search_text_index")
        
        # Index on price for sorting by price
        products_collection.create_index("price", name="price_index")
        
        results['products'] = "Indexes created: category_id, active, featured, text search, price"
        logging.info("Products collection indexes created successfully")
        
        # Categories collection indexes
        categories_collection = database[Collections.CATEGORIES]
        
        # Unique index on category name
        categories_collection.create_index("name", unique=True, name="category_name_unique")
        
        # Index on display_order for sorting categories
        categories_collection.create_index("display_order", name="display_order_index")
        
        # Index on active status
        categories_collection.create_index("active", name="category_active_index")
        
        results['categories'] = "Indexes created: name (unique), display_order, active"
        logging.info("Categories collection indexes created successfully")
        
        # Orders collection indexes
        orders_collection = database[Collections.ORDERS]
        
        # Unique index on order_number
        orders_collection.create_index("order_number", unique=True, name="order_number_unique")
        
        # Index on customer_phone for customer order lookup
        orders_collection.create_index("customer_phone", name="customer_phone_index")
        
        # Index on status for order status filtering
        orders_collection.create_index("status", name="order_status_index")
        
        # Index on created_at for date-based queries
        orders_collection.create_index("created_at", name="order_created_at_index")
        
        # Sparse TTL index on verification_code (expires in 10 minutes)
        orders_collection.create_index("verification_code", 
                                     sparse=True, 
                                     expireAfterSeconds=600,  # 10 minutes
                                     name="verification_code_ttl")
        
        results['orders'] = "Indexes created: order_number (unique), customer_phone, status, created_at, verification_code (TTL)"
        logging.info("Orders collection indexes created successfully")
        
        # Cart sessions collection indexes
        cart_sessions_collection = database[Collections.CART_SESSIONS]
        
        # Unique index on session_id
        cart_sessions_collection.create_index("session_id", unique=True, name="session_id_unique")
        
        # TTL index on created_at (expires after 24 hours)
        cart_sessions_collection.create_index("created_at", 
                                            expireAfterSeconds=86400,  # 24 hours
                                            name="cart_session_ttl")
        
        results['cart_sessions'] = "Indexes created: session_id (unique), created_at (TTL 24h)"
        logging.info("Cart sessions collection indexes created successfully")
        
        logging.info("All database indexes created successfully")
        return results
        
    except Exception as e:
        logging.error(f"Error creating database indexes: {e}")
        raise RuntimeError(f"Failed to create database indexes: {e}")


def drop_all_indexes():
    """
    Drop all custom indexes (excluding _id) from all collections.
    Useful for development and testing.
    
    Warning: This will impact query performance until indexes are recreated.
    
    Returns:
        dict: Summary of dropped indexes
    """
    database = get_database()
    results = {}
    
    collection_names = [Collections.USERS, Collections.PRODUCTS, Collections.CATEGORIES, 
                       Collections.ORDERS, Collections.CART_SESSIONS]
    
    for collection_name in collection_names:
        try:
            collection = database[collection_name]
            # Get all indexes except _id_
            indexes = collection.list_indexes()
            dropped_count = 0
            
            for index in indexes:
                index_name = index['name']
                if index_name != '_id_':  # Never drop the _id index
                    collection.drop_index(index_name)
                    dropped_count += 1
            
            results[collection_name] = f"Dropped {dropped_count} indexes"
            logging.info(f"Dropped {dropped_count} indexes from {collection_name} collection")
            
        except Exception as e:
            results[collection_name] = f"Error: {e}"
            logging.error(f"Error dropping indexes from {collection_name}: {e}")
    
    return results


def list_all_indexes():
    """
    List all indexes across all collections for debugging and verification.
    
    Returns:
        dict: Dictionary with collection names as keys and index lists as values
    """
    database = get_database()
    results = {}
    
    collection_names = [Collections.USERS, Collections.PRODUCTS, Collections.CATEGORIES, 
                       Collections.ORDERS, Collections.CART_SESSIONS]
    
    for collection_name in collection_names:
        try:
            collection = database[collection_name]
            indexes = list(collection.list_indexes())
            results[collection_name] = [
                {
                    'name': idx['name'],
                    'key': idx['key'],
                    'unique': idx.get('unique', False),
                    'sparse': idx.get('sparse', False),
                    'expireAfterSeconds': idx.get('expireAfterSeconds')
                }
                for idx in indexes
            ]
        except Exception as e:
            results[collection_name] = f"Error listing indexes: {e}"
    
    return results


# Collection name constants for consistency
class Collections:
    """MongoDB collection name constants."""
    USERS = 'users'
    PRODUCTS = 'products'
    CATEGORIES = 'categories'
    ORDERS = 'orders'
    CART_SESSIONS = 'cart_sessions'