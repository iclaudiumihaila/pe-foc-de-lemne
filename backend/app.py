"""
Local Producer Web Application - Main Entry Point

This is the main entry point for the Flask backend application.
It creates and configures the Flask app and runs the development server.
"""

import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from app import create_app
from app.config import Config, DevelopmentConfig, ProductionConfig


def create_application():
    """
    Create and configure the Flask application with environment-specific settings.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Determine environment and configuration
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        config_class = ProductionConfig
        logging.info("Starting application in PRODUCTION mode")
    else:
        config_class = DevelopmentConfig
        logging.info("Starting application in DEVELOPMENT mode")
    
    # Create Flask application using factory pattern
    app = create_app(config_class)
    
    # Configure CORS for frontend integration
    # Use the CORS_ORIGINS from config which already includes multiple origins
    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:3000'])
    
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'])
    
    logging.info(f"CORS configured for origins: {cors_origins}")
    
    # Configure session settings
    app.config.update(
        SESSION_COOKIE_SECURE=env == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 hour
    )
    
    # Add health check endpoint at root
    @app.route('/')
    def health_check():
        """Root health check endpoint."""
        return {
            'status': 'healthy',
            'message': 'Local Producer Web Application API',
            'version': '1.0.0',
            'environment': env
        }
    
    # Serve uploaded images (for development - in production use Nginx)
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serve uploaded files with support for subdirectories."""
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
        return send_from_directory(upload_folder, filename)
    
    
    # Log application startup information
    logging.info("=" * 60)
    logging.info("LOCAL PRODUCER WEB APPLICATION - BACKEND")
    logging.info("=" * 60)
    logging.info(f"Environment: {env}")
    logging.info(f"Debug Mode: {app.debug}")
    logging.info(f"Database URI: {app.config.get('MONGODB_URI', 'Not configured')}")
    logging.info(f"Secret Key: {'Configured' if app.config.get('SECRET_KEY') else 'Not configured'}")
    logging.info(f"CORS Origins: {cors_origins}")
    
    # Log registered routes
    logging.info("Registered Routes:")
    for rule in app.url_map.iter_rules():
        logging.info(f"  {rule.methods} {rule.rule}")
    
    logging.info("=" * 60)
    
    return app


def main():
    """
    Main entry point for running the Flask development server.
    """
    # Configure basic logging for startup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        # Create the Flask application
        app = create_application()
        
        # Get configuration from environment or app config
        host = os.getenv('FLASK_HOST', app.config.get('HOST', '127.0.0.1'))
        port = int(os.getenv('FLASK_PORT', app.config.get('PORT', 8000)))
        debug = os.getenv('FLASK_DEBUG', str(app.config.get('DEBUG', True))).lower() == 'true'
        
        logging.info(f"Starting Flask development server on {host}:{port}")
        logging.info(f"Debug mode: {debug}")
        logging.info("Press CTRL+C to quit")
        
        # Run the development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logging.info("Application shutdown requested by user")
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        raise


if __name__ == '__main__':
    main()