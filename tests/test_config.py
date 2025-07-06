import os
import pytest
from unittest.mock import patch
from app.utils.config import Config


class TestConfig:
    """Test suite for the Config class."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        env_vars = [
            'SLACK_BOT_TOKEN', 'SLACK_SIGNING_SECRET', 'OPENAI_API_KEY',
            'OPENAI_MODEL', 'FLASK_ENV', 'FLASK_PORT', 'LOG_LEVEL'
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_missing_required_vars_raises_error(self):
        """Test that missing required environment variables raise ValueError."""
        with pytest.raises(ValueError, match="Missing required environment variable: SLACK_BOT_TOKEN"):
            Config()
    
    def test_missing_slack_signing_secret_raises_error(self):
        """Test that missing SLACK_SIGNING_SECRET raises ValueError."""
        os.environ['SLACK_BOT_TOKEN'] = 'test-token'
        
        with pytest.raises(ValueError, match="Missing required environment variable: SLACK_SIGNING_SECRET"):
            Config()
    
    def test_missing_openai_api_key_raises_error(self):
        """Test that missing OPENAI_API_KEY raises ValueError."""
        os.environ['SLACK_BOT_TOKEN'] = 'test-token'
        os.environ['SLACK_SIGNING_SECRET'] = 'test-secret'
        
        with pytest.raises(ValueError, match="Missing required environment variable: OPENAI_API_KEY"):
            Config()
    
    def test_all_required_vars_success(self):
        """Test that config loads successfully when all required vars are provided."""
        os.environ['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
        os.environ['SLACK_SIGNING_SECRET'] = 'test-signing-secret'
        os.environ['OPENAI_API_KEY'] = 'sk-test-api-key'
        
        config = Config()
        
        assert config.slack_bot_token == 'xoxb-test-token'
        assert config.slack_signing_secret == 'test-signing-secret'
        assert config.openai_api_key == 'sk-test-api-key'
    
    def test_default_values_for_optional_vars(self):
        """Test that default values are used for optional variables."""
        os.environ['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
        os.environ['SLACK_SIGNING_SECRET'] = 'test-signing-secret'
        os.environ['OPENAI_API_KEY'] = 'sk-test-api-key'
        
        config = Config()
        
        assert config.openai_model == 'gpt-4'
        assert config.flask_env == 'development'
        assert config.flask_port == 3000
        assert config.log_level == 'INFO'
    
    def test_custom_values_for_optional_vars(self):
        """Test that custom values override defaults for optional variables."""
        os.environ['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
        os.environ['SLACK_SIGNING_SECRET'] = 'test-signing-secret'
        os.environ['OPENAI_API_KEY'] = 'sk-test-api-key'
        os.environ['OPENAI_MODEL'] = 'gpt-3.5-turbo'
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_PORT'] = '8080'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        config = Config()
        
        assert config.openai_model == 'gpt-3.5-turbo'
        assert config.flask_env == 'production'
        assert config.flask_port == 8080
        assert config.log_level == 'DEBUG'
    
    @patch('app.utils.config.load_dotenv')
    def test_dotenv_is_called(self, mock_load_dotenv):
        """Test that load_dotenv is called during config initialization."""
        os.environ['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
        os.environ['SLACK_SIGNING_SECRET'] = 'test-signing-secret'
        os.environ['OPENAI_API_KEY'] = 'sk-test-api-key'
        
        Config()
        
        mock_load_dotenv.assert_called_once()
    
    def teardown_method(self):
        """Clean up environment variables after each test."""
        env_vars = [
            'SLACK_BOT_TOKEN', 'SLACK_SIGNING_SECRET', 'OPENAI_API_KEY',
            'OPENAI_MODEL', 'FLASK_ENV', 'FLASK_PORT', 'LOG_LEVEL'
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var] 