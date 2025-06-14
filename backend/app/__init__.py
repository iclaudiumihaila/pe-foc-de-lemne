"""
Local Producer Web Application - Flask App Factory

This module implements the Flask application factory pattern for the
local producer web application backend.
"""

import logging
from flask import Flask
from app.config import Config
from app.database import init_mongodb
from app.utils.error_handlers import register_error_handlers
from app.routes import register_routes


def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    This factory creates a Flask application with configuration,
    database initialization, error handling, and API routes.
    
    Args:
        config_class: Configuration class to use (default: Config)
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize database
    init_mongodb(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register API routes
    register_routes(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    
    logging.info("Flask application created successfully")
    
    # Return the configured app
    return app