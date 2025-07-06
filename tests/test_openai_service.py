import pytest
from unittest.mock import Mock, patch, MagicMock
import openai
from app.services.openai_service import OpenAIService


class TestOpenAIService:
    """Test suite for the OpenAI service."""
    
    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="OpenAI API key cannot be empty or None"):
            OpenAIService("")
    
    def test_none_api_key_raises_error(self):
        """Test that None API key raises ValueError."""
        with pytest.raises(ValueError, match="OpenAI API key cannot be empty or None"):
            OpenAIService(None)
    
    @patch('app.services.openai_service.OpenAI')
    def test_openai_client_initialization(self, mock_openai_class):
        """Test that OpenAI client is initialized with the correct API key."""
        # Mock the OpenAI client and its methods
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock the chat completions create method
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test service initialization
        service = OpenAIService("test-api-key", "gpt-4")
        
        # Verify OpenAI client was initialized with correct API key
        mock_openai_class.assert_called_once_with(api_key="test-api-key")
        
        # Verify model is set correctly
        assert service.model == "gpt-4"
        assert service.client == mock_client
    
    @patch('app.services.openai_service.OpenAI')
    def test_api_key_validation_called(self, mock_openai_class):
        """Test that API key validation is called during initialization."""
        # Mock the OpenAI client and its methods
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock the chat completions create method
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        # Initialize service
        service = OpenAIService("test-api-key")
        
        # Verify validation API call was made
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
    
    @patch('app.services.openai_service.OpenAI')
    def test_authentication_error_handling(self, mock_openai_class):
        """Test that authentication errors are properly handled."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock authentication error during validation
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            "Invalid API key", response=Mock(), body=None
        )
        
        # Test that proper error is raised
        with pytest.raises(ValueError, match="Failed to initialize OpenAI client: Invalid OpenAI API key"):
            OpenAIService("invalid-key")
    
    @patch('app.services.openai_service.OpenAI')
    def test_rate_limit_error_handling(self, mock_openai_class):
        """Test that rate limit errors are handled gracefully (API key is still valid)."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock rate limit error during validation
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            "Rate limit exceeded", response=Mock(), body=None
        )
        
        # Should not raise error for rate limit (API key is valid)
        service = OpenAIService("test-api-key")
        assert service.model == "gpt-4"
    
    @patch('app.services.openai_service.OpenAI')
    def test_generic_error_handling(self, mock_openai_class):
        """Test that generic errors during validation are handled."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock generic error during validation
        mock_client.chat.completions.create.side_effect = Exception("Network error")
        
        # Test that proper error is raised
        with pytest.raises(ValueError, match="Failed to initialize OpenAI client: OpenAI API key validation failed: Network error"):
            OpenAIService("test-api-key")
    
    def test_default_model(self):
        """Test that default model is gpt-4."""
        with patch('app.services.openai_service.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = Mock()
            
            service = OpenAIService("test-api-key")
            assert service.model == "gpt-4"
    
    def test_custom_model(self):
        """Test that custom model can be set."""
        with patch('app.services.openai_service.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = Mock()
            
            service = OpenAIService("test-api-key", "gpt-3.5-turbo")
            assert service.model == "gpt-3.5-turbo"


class TestOpenAIServiceIntegration:
    """Integration tests for OpenAI service with real API (if available)."""
    
    def test_real_api_key_integration(self):
        """Test with real API key if available in environment."""
        import os
        
        # Only run this test if we have a real API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("No real OpenAI API key available")
        
        # Test that service initializes with real API key
        service = OpenAIService(api_key)
        assert service.model == "gpt-4"
        assert service.client is not None 