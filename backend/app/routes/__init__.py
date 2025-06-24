"""
API Routes Blueprint for Local Producer Web Application

This module provides the main API blueprint with health check endpoint
and registration utilities for Flask application.
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify
from app.database import get_database
from app.utils.error_handlers import success_response, create_error_response
from pymongo.errors import ConnectionFailure
from .auth import auth_bp
from .products import products_bp
from .categories import categories_bp
from .orders import orders_bp
from .cart import cart_bp
from .sms import sms_bp
from .sitemap import sitemap_bp
from .analytics import analytics_bp
from .checkout import checkout_bp
from .admin import admin_bp

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    
    Returns:
        JSON response with health status, database connectivity,
        application version, and timestamp.
        
    Response Format:
        - 200: API healthy with database connection
        - 503: API unhealthy - database connection failed
    """
    try:
        # Log health check request
        logging.info("Health check requested")
        
        # Test database connectivity
        db = get_database()
        
        # Simple ping to verify database connection
        # Use a lightweight operation to test connectivity
        db.command('ping')
        
        database_status = "connected"
        status = "healthy"
        
        # Create success response with health data
        health_data = {
            "status": status,
            "database": database_status,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        response = success_response(health_data, "API is healthy")
        
        logging.info(f"Health check successful - database: {database_status}")
        return jsonify(response), 200
        
    except ConnectionFailure as e:
        # Database connection failed
        logging.error(f"Health check failed - database connection error: {str(e)}")
        
        error_response, status_code = create_error_response(
            "DB_001",
            "Database connection failed",
            503,
            {"database": "disconnected", "error": "Connection failure"}
        )
        
        return jsonify(error_response), status_code
        
    except Exception as e:
        # Unexpected error during health check
        logging.error(f"Health check failed - unexpected error: {str(e)}")
        
        error_response, status_code = create_error_response(
            "DB_001",
            "Health check failed",
            503,
            {"error": "Unexpected error during health check"}
        )
        
        return jsonify(error_response), status_code


def register_routes(app):
    """
    Register API blueprint with Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    # Register sub-blueprints to api blueprint BEFORE registering api to app
    api.register_blueprint(auth_bp, url_prefix='/auth')
    api.register_blueprint(products_bp, url_prefix='/products')
    api.register_blueprint(categories_bp, url_prefix='/categories')
    api.register_blueprint(orders_bp, url_prefix='/orders')
    api.register_blueprint(cart_bp, url_prefix='/cart')
    api.register_blueprint(sms_bp, url_prefix='/sms')
    api.register_blueprint(analytics_bp, url_prefix='/analytics')
    api.register_blueprint(checkout_bp, url_prefix='/checkout')
    
    # Now register the api blueprint with all its sub-blueprints
    app.register_blueprint(api)
    
    # Register admin blueprint separately (it already has /api/admin prefix)
    app.register_blueprint(admin_bp)
    
    # Register sitemap routes at root level (not under /api)
    app.register_blueprint(sitemap_bp)
    
    logging.info("API routes registered successfully")