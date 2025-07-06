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
            "Invalid API key", response=Mock(), body=Mock()
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
            "Rate limit exceeded", response=Mock(), body=Mock()
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


class TestMessageFormatting:
    """Test suite for Slack message formatting functionality."""
    
    @patch('app.services.openai_service.OpenAI')
    def setup_service(self, mock_openai_class):
        """Helper to set up service for testing."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()
        return OpenAIService("test-api-key")
    
    def test_format_slack_message_user_mentions(self):
        """Test removal of user mentions."""
        service = self.setup_service()
        
        # Test basic user mention
        result = service.format_slack_message("Hello <@U123456> how are you?")
        assert result == "Hello how are you?"
        
        # Test user mention with username
        result = service.format_slack_message("Hi <@U123456|john> welcome!")
        assert result == "Hi welcome!"
        
        # Test multiple user mentions
        result = service.format_slack_message("<@U123456> and <@U789012|jane> are here")
        assert result == "and are here"
    
    def test_format_slack_message_channel_mentions(self):
        """Test removal of channel mentions."""
        service = self.setup_service()
        
        # Test basic channel mention
        result = service.format_slack_message("Check <#C123456> channel")
        assert result == "Check channel"
        
        # Test channel mention with name
        result = service.format_slack_message("Visit <#C123456|general> please")
        assert result == "Visit please"
    
    def test_format_slack_message_links(self):
        """Test formatting of links."""
        service = self.setup_service()
        
        # Test link with text
        result = service.format_slack_message("Visit <https://example.com|this site>")
        assert result == "Visit this site"
        
        # Test link without text
        result = service.format_slack_message("Go to <https://example.com>")
        assert result == "Go to https://example.com"
        
        # Test multiple links
        result = service.format_slack_message("Check <https://example.com|site> and <https://test.com>")
        assert result == "Check site and https://test.com"
    
    def test_format_slack_message_text_formatting(self):
        """Test removal of text formatting."""
        service = self.setup_service()
        
        # Test bold
        result = service.format_slack_message("This is *bold* text")
        assert result == "This is bold text"
        
        # Test italic
        result = service.format_slack_message("This is _italic_ text")
        assert result == "This is italic text"
        
        # Test code
        result = service.format_slack_message("This is `code` text")
        assert result == "This is code text"
        
        # Test strikethrough
        result = service.format_slack_message("This is ~strikethrough~ text")
        assert result == "This is strikethrough text"
    
    def test_format_slack_message_combined_formatting(self):
        """Test complex message with multiple formatting types."""
        service = self.setup_service()
        
        message = "<@U123456> check *bold* _italic_ `code` in <#C123456|general> and visit <https://example.com|site>"
        result = service.format_slack_message(message)
        assert result == "check bold italic code in and visit site"
    
    def test_format_slack_message_whitespace_cleanup(self):
        """Test that extra whitespace is cleaned up."""
        service = self.setup_service()
        
        # Test multiple spaces
        result = service.format_slack_message("Hello    world   with   spaces")
        assert result == "Hello world with spaces"
        
        # Test leading/trailing whitespace
        result = service.format_slack_message("   Hello world   ")
        assert result == "Hello world"
        
        # Test whitespace from removed formatting
        result = service.format_slack_message("<@U123456>   <@U789012>   hello")
        assert result == "hello"
    
    def test_format_slack_message_empty_input(self):
        """Test handling of empty input."""
        service = self.setup_service()
        
        assert service.format_slack_message("") == ""
        assert service.format_slack_message(None) == ""
    
    def test_format_slack_message_only_formatting(self):
        """Test message that becomes empty after formatting."""
        service = self.setup_service()
        
        # Message with only mentions
        result = service.format_slack_message("<@U123456> <@U789012>")
        assert result == ""
        
        # Message with only formatting
        result = service.format_slack_message("*bold* _italic_ `code`")
        assert result == "bold italic code"


class TestChatCompletion:
    """Test suite for the chat completion functionality."""
    
    @patch('app.services.openai_service.OpenAI')
    def test_get_chat_completion_success(self, mock_openai_class):
        """Test successful chat completion."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock successful responses
        mock_validation_response = Mock()
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = "Hello! How can I help you?"
        
        # First call is validation, second is actual chat
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            mock_chat_response
        ]
        
        # Test chat completion
        service = OpenAIService("test-api-key")
        result = service.get_chat_completion("Hello!")
        
        assert result == "Hello! How can I help you?"
    
    @patch('app.services.openai_service.OpenAI')
    def test_get_chat_completion_with_slack_formatting(self, mock_openai_class):
        """Test that Slack formatting is removed before sending to OpenAI."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock responses
        mock_validation_response = Mock()
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = "Response"
        
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            mock_chat_response
        ]
        
        # Test with Slack formatting
        service = OpenAIService("test-api-key")
        service.get_chat_completion("<@U123456> *Hello* there!")
        
        # Verify the formatted message was sent to OpenAI
        calls = mock_client.chat.completions.create.call_args_list
        chat_call = calls[1]  # Second call is the actual chat
        assert chat_call[1]['messages'][0]['content'] == "Hello there!"
    
    @patch('app.services.openai_service.OpenAI')
    def test_get_chat_completion_with_whitespace(self, mock_openai_class):
        """Test that whitespace is properly handled in messages."""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock responses
        mock_validation_response = Mock()
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = "  Response with whitespace  "
        
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            mock_chat_response
        ]
        
        # Test with whitespace
        service = OpenAIService("test-api-key")
        result = service.get_chat_completion("  Hello with whitespace  ")
        
        # Should strip whitespace from response
        assert result == "Response with whitespace"
        
        # Verify the message was stripped before sending
        calls = mock_client.chat.completions.create.call_args_list
        chat_call = calls[1]  # Second call is the actual chat
        assert chat_call[1]['messages'][0]['content'] == "Hello with whitespace"
    
    @patch('app.services.openai_service.OpenAI')
    def test_empty_message_raises_error(self, mock_openai_class):
        """Test that empty messages raise ValueError."""
        # Mock the client for initialization
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(ValueError, match="Message cannot be empty or None"):
            service.get_chat_completion("")
    
    @patch('app.services.openai_service.OpenAI')
    def test_none_message_raises_error(self, mock_openai_class):
        """Test that None message raises ValueError."""
        # Mock the client for initialization
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(ValueError, match="Message cannot be empty or None"):
            service.get_chat_completion(None)
    
    @patch('app.services.openai_service.OpenAI')
    def test_whitespace_only_message_raises_error(self, mock_openai_class):
        """Test that whitespace-only messages raise ValueError."""
        # Mock the client for initialization
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(ValueError, match="Message cannot be empty or None"):
            service.get_chat_completion("   ")
    
    @patch('app.services.openai_service.OpenAI')
    def test_message_empty_after_formatting_raises_error(self, mock_openai_class):
        """Test that message empty after formatting raises ValueError."""
        # Mock the client for initialization
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock()
        
        service = OpenAIService("test-api-key")
        
        # Message with only Slack formatting that becomes empty
        with pytest.raises(ValueError, match="Message cannot be empty after formatting"):
            service.get_chat_completion("<@U123456> <@U789012>   ")
    
    @patch('app.services.openai_service.OpenAI')
    def test_authentication_error_in_chat(self, mock_openai_class):
        """Test authentication error during chat completion."""
        # Mock the client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock validation success, chat failure
        mock_validation_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            openai.AuthenticationError("Invalid API key", response=Mock(), body=Mock())
        ]
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(RuntimeError, match="OpenAI API authentication failed"):
            service.get_chat_completion("Hello!")
    
    @patch('app.services.openai_service.OpenAI')
    def test_rate_limit_error_in_chat(self, mock_openai_class):
        """Test rate limit error during chat completion."""
        # Mock the client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock validation success, chat rate limit
        mock_validation_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            openai.RateLimitError("Rate limit exceeded", response=Mock(), body=Mock())
        ]
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(RuntimeError, match="OpenAI API rate limit exceeded - please try again later"):
            service.get_chat_completion("Hello!")
    
    @patch('app.services.openai_service.OpenAI')
    def test_api_error_in_chat(self, mock_openai_class):
        """Test API error during chat completion."""
        # Mock the client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock validation success, chat API error
        mock_validation_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            openai.APIError("Service unavailable", request=Mock(), body=Mock())
        ]
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(RuntimeError, match="OpenAI API error:"):
            service.get_chat_completion("Hello!")
    
    @patch('app.services.openai_service.OpenAI')
    def test_empty_response_handling(self, mock_openai_class):
        """Test handling of empty responses from OpenAI."""
        # Mock the client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock validation success, empty chat response
        mock_validation_response = Mock()
        mock_empty_response = Mock()
        mock_empty_response.choices = []
        
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            mock_empty_response
        ]
        
        service = OpenAIService("test-api-key")
        
        with pytest.raises(RuntimeError, match="OpenAI API returned empty response"):
            service.get_chat_completion("Hello!")
    
    @patch('app.services.openai_service.OpenAI')
    def test_chat_completion_parameters(self, mock_openai_class):
        """Test that chat completion is called with correct parameters."""
        # Mock the client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock responses
        mock_validation_response = Mock()
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = "Response"
        
        mock_client.chat.completions.create.side_effect = [
            mock_validation_response,
            mock_chat_response
        ]
        
        service = OpenAIService("test-api-key", "gpt-3.5-turbo")
        service.get_chat_completion("Test message")
        
        # Verify chat completion call parameters
        calls = mock_client.chat.completions.create.call_args_list
        chat_call = calls[1]  # Second call is the actual chat
        
        assert chat_call[1]['model'] == "gpt-3.5-turbo"
        assert chat_call[1]['messages'] == [{"role": "user", "content": "Test message"}]
        assert chat_call[1]['max_tokens'] == 1000
        assert chat_call[1]['temperature'] == 0.7


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
    
    def test_real_chat_completion_integration(self):
        """Test chat completion with real API if available."""
        import os
        
        # Only run this test if we have a real API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("No real OpenAI API key available")
        
        # Test chat completion with real API
        service = OpenAIService(api_key)
        response = service.get_chat_completion("Say 'test successful' if you can read this.")
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    def test_real_message_formatting_integration(self):
        """Test message formatting with real API if available."""
        import os
        
        # Only run this test if we have a real API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("No real OpenAI API key available")
        
        # Test that Slack formatting is properly removed before sending to OpenAI
        service = OpenAIService(api_key)
        slack_message = '<@U123456> *Hello* there! Say "formatting test complete".'
        response = service.get_chat_completion(slack_message)
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
        # The response should not contain Slack formatting since it was cleaned 