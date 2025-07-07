# Empty file - Flask app factory will be implemented later 

from flask import Flask, jsonify
from app.utils.config import Config


def create_app(config_override=None):
    """
    Flask application factory.
    
    Args:
        config_override: Optional configuration override for testing
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    try:
        # Load configuration
        if config_override:
            config = config_override
        else:
            config = Config()
        
        # Configure Flask with settings from config
        app.config['ENV'] = config.flask_env
        app.config['DEBUG'] = config.flask_env == 'development'
        app.config['TESTING'] = False
        
        # Store config for use in routes
        app.config['BOT_CONFIG'] = config
        
        # Register error handlers
        register_error_handlers(app)
        
        # Register routes
        register_routes(app, config)
        
        return app
        
    except Exception as e:
        # If configuration fails, create a minimal app that can report the error
        app.config['CONFIGURATION_ERROR'] = str(e)
        register_error_routes(app)
        return app


def register_routes(app, config):
    """Register application routes."""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            # Check if configuration loaded successfully
            if hasattr(config, 'slack_bot_token') and hasattr(config, 'openai_api_key'):
                return jsonify({
                    'status': 'healthy',
                    'message': 'Slack chatbot is running',
                    'version': '1.0.0',
                    'services': {
                        'slack': 'configured',
                        'openai': 'configured',
                        'flask': 'running'
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'unhealthy',
                    'message': 'Configuration incomplete',
                    'error': 'Missing required configuration'
                }), 500
                
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Health check failed',
                'error': str(e)
            }), 500


def register_error_routes(app):
    """Register error routes for when configuration fails."""
    
    @app.route('/health', methods=['GET'])
    def health_check_error():
        """Health check endpoint when configuration failed."""
        return jsonify({
            'status': 'unhealthy',
            'message': 'Configuration failed',
            'error': app.config.get('CONFIGURATION_ERROR', 'Unknown configuration error')
        }), 500


def register_error_handlers(app):
    """Register application error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': 'Internal Server Error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions."""
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'error': str(error)
        }), 500 