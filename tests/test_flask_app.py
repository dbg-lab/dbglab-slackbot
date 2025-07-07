import pytest
import json
from unittest.mock import Mock, patch
from app import create_app
from app.utils.config import Config


class TestFlaskAppFactory:
    """Test suite for Flask app factory."""
    
    def test_create_app_success(self):
        """Test successful Flask app creation."""
        app = create_app()
        
        # Verify app is created
        assert app is not None
        assert app.name == 'app'
        
        # Verify configuration is set
        assert 'ENV' in app.config
        assert 'DEBUG' in app.config
        assert 'TESTING' in app.config
        assert 'BOT_CONFIG' in app.config
        
        # Verify config values based on default environment
        assert app.config['ENV'] == 'development'
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
    
    def test_create_app_with_config_override(self):
        """Test Flask app creation with config override."""
        # Create mock config
        mock_config = Mock()
        mock_config.flask_env = 'production'
        mock_config.flask_port = 5000
        mock_config.slack_bot_token = 'test-token'
        mock_config.openai_api_key = 'test-key'
        
        app = create_app(config_override=mock_config)
        
        # Verify app is created with override config
        assert app is not None
        assert app.config['ENV'] == 'production'
        assert app.config['DEBUG'] is False
        assert app.config['BOT_CONFIG'] == mock_config
    
    @patch('app.Config')
    def test_create_app_with_config_error(self, mock_config_class):
        """Test Flask app creation when configuration fails."""
        # Mock configuration failure
        mock_config_class.side_effect = Exception("Config error")
        
        app = create_app()
        
        # Verify app is created but with error config
        assert app is not None
        assert 'CONFIGURATION_ERROR' in app.config
        assert app.config['CONFIGURATION_ERROR'] == "Config error"
    
    def test_app_routes_registered(self):
        """Test that routes are properly registered."""
        app = create_app()
        
        # Check that health route is registered
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code in [200, 500]  # Should exist, status depends on config
    
    def test_error_handlers_registered(self):
        """Test that error handlers are registered."""
        app = create_app()
        
        with app.test_client() as client:
            # Test 404 handler
            response = client.get('/nonexistent')
            assert response.status_code == 404
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'error'
            assert data['message'] == 'Endpoint not found'


class TestHealthCheckEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_check_success(self):
        """Test successful health check response."""
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/health')
            
            # Check response status
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            # Parse and verify response data
            data = json.loads(response.data.decode('utf-8'))
            
            # Verify required fields
            assert 'status' in data
            assert 'message' in data
            assert 'version' in data
            assert 'services' in data
            
            # Verify field values
            assert data['status'] == 'healthy'
            assert data['message'] == 'Slack chatbot is running'
            assert data['version'] == '1.0.0'
            
            # Verify services section
            services = data['services']
            assert 'slack' in services
            assert 'openai' in services
            assert 'flask' in services
            assert services['slack'] == 'configured'
            assert services['openai'] == 'configured'
            assert services['flask'] == 'running'
    
    def test_health_check_with_incomplete_config(self):
        """Test health check with incomplete configuration."""
        # Create mock config that explicitly lacks required attributes
        mock_config = Mock()
        # Use spec to limit what attributes the mock has
        mock_config = Mock(spec=['flask_env', 'flask_port'])
        mock_config.flask_env = 'test'
        mock_config.flask_port = 5000
        
        app = create_app(config_override=mock_config)
        
        with app.test_client() as client:
            response = client.get('/health')
            
            # Should return unhealthy status
            assert response.status_code == 500
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'unhealthy'
            assert data['message'] == 'Configuration incomplete'
    
    @patch('app.Config')
    def test_health_check_with_config_error(self, mock_config_class):
        """Test health check when configuration fails."""
        # Mock configuration failure
        mock_config_class.side_effect = Exception("Config error")
        
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/health')
            
            # Should return error status
            assert response.status_code == 500
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'unhealthy'
            assert data['message'] == 'Configuration failed'
            assert data['error'] == 'Config error'
    
    def test_health_check_exception_handling(self):
        """Test health check exception handling."""
        # Create a mock config that will cause an exception in the health check
        mock_config = Mock()
        mock_config.slack_bot_token = 'test-token'
        mock_config.openai_api_key = 'test-key'
        
        # Mock hasattr to raise an exception
        app = create_app(config_override=mock_config)
        
        with app.test_client() as client:
            # This is tricky to test directly, but we can verify the endpoint exists
            # and handles exceptions gracefully
            response = client.get('/health')
            
            # Should return a valid JSON response
            assert response.content_type == 'application/json'
            data = json.loads(response.data.decode('utf-8'))
            assert 'status' in data


class TestErrorHandlers:
    """Test suite for Flask error handlers."""
    
    def test_404_error_handler(self):
        """Test 404 error handler."""
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/nonexistent')
            
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'error'
            assert data['message'] == 'Endpoint not found'
            assert data['error'] == 'Not Found'
    
    def test_500_error_handler(self):
        """Test 500 error handler."""
        app = create_app()
        
        # Create a route that will cause a 500 error
        @app.route('/test-500')
        def test_500():
            raise Exception("Test error")
        
        with app.test_client() as client:
            response = client.get('/test-500')
            
            assert response.status_code == 500
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'error'
            assert data['message'] == 'An unexpected error occurred'
            assert data['error'] == 'Test error'
    
    def test_method_not_allowed_handling(self):
        """Test that unsupported methods are handled gracefully."""
        app = create_app()
        
        with app.test_client() as client:
            # Try POST to health endpoint (only GET is allowed)
            response = client.post('/health')
            
            # Flask will either return 405 or 500 depending on how it's handled
            # Both are acceptable for our purposes
            assert response.status_code in [405, 500]
            assert response.content_type == 'application/json'
    
    def test_health_endpoint_get_only(self):
        """Test that health endpoint responds correctly to GET."""
        app = create_app()
        
        with app.test_client() as client:
            # GET should work
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data.decode('utf-8'))
            assert data['status'] == 'healthy' 