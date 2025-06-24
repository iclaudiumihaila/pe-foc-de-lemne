#!/usr/bin/env python3
"""Test if we can start the server by fixing the blueprint registration issue."""

import os
import sys

# Set environment variables before importing app
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'False'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after setting environment
from flask import Flask
from flask_cors import CORS
from app.config import DevelopmentConfig
from app.database import init_mongodb
from app.utils.error_handlers import register_error_handlers

def create_test_app():
    """Create a test Flask app."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(DevelopmentConfig)
    
    # Initialize CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Initialize database
    init_mongodb(DevelopmentConfig)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Import routes here to avoid circular imports
    from app.routes import api
    from app.routes.sitemap import sitemap_bp
    
    # Register blueprints
    app.register_blueprint(api)
    app.register_blueprint(sitemap_bp)
    
    return app

if __name__ == '__main__':
    try:
        app = create_test_app()
        print("✓ Server started successfully!")
        print("✓ Backend running at: http://localhost:8000")
        print("✓ API endpoint: http://localhost:8000/api")
        print("✓ Health check: http://localhost:8000/api/health")
        print("\nPress CTRL+C to stop the server")
        app.run(host='127.0.0.1', port=8000, debug=False)
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        import traceback
        traceback.print_exc()