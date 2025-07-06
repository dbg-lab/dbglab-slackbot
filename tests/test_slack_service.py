import pytest
from unittest.mock import Mock, patch
from slack_sdk.errors import SlackApiError
from app.services.slack_service import SlackService


class TestSlackService:
    """Test suite for the Slack service."""
    
    def test_empty_bot_token_raises_error(self):
        """Test that empty bot token raises ValueError."""
        with pytest.raises(ValueError, match="Slack bot token cannot be empty or None"):
            SlackService("")
    
    def test_none_bot_token_raises_error(self):
        """Test that None bot token raises ValueError."""
        with pytest.raises(ValueError, match="Slack bot token cannot be empty or None"):
            SlackService(None)
    
    def test_invalid_token_format_raises_error(self):
        """Test that invalid token format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Slack bot token format - must start with 'xoxb-'"):
            SlackService("invalid-token")
        
        with pytest.raises(ValueError, match="Invalid Slack bot token format - must start with 'xoxb-'"):
            SlackService("xoxa-1234567890")  # Wrong prefix
    
    @patch('app.services.slack_service.WebClient')
    def test_webclient_initialization(self, mock_webclient_class):
        """Test that WebClient is initialized with the correct bot token."""
        # Mock the WebClient and its methods
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock successful auth test
        mock_response = {
            "ok": True,
            "user_id": "U123456",
            "team_id": "T123456"
        }
        mock_client.auth_test.return_value = mock_response
        
        # Test service initialization
        service = SlackService("xoxb-test-token")
        
        # Verify WebClient was initialized with correct token
        mock_webclient_class.assert_called_once_with(token="xoxb-test-token")
        
        # Verify bot info is stored
        assert service.bot_user_id == "U123456"
        assert service.team_id == "T123456"
        assert service.client == mock_client
    
    @patch('app.services.slack_service.WebClient')
    def test_auth_test_called_during_validation(self, mock_webclient_class):
        """Test that auth.test is called during token validation."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock successful auth test
        mock_response = {
            "ok": True,
            "user_id": "U123456",
            "team_id": "T123456"
        }
        mock_client.auth_test.return_value = mock_response
        
        # Initialize service
        service = SlackService("xoxb-test-token")
        
        # Verify auth.test was called
        mock_client.auth_test.assert_called_once()
    
    @patch('app.services.slack_service.WebClient')
    def test_invalid_auth_error_handling(self, mock_webclient_class):
        """Test that invalid auth errors are properly handled."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock auth error
        error_response = {"error": "invalid_auth"}
        mock_client.auth_test.side_effect = SlackApiError(
            message="Invalid auth",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to initialize Slack client: Invalid Slack bot token"):
            SlackService("xoxb-invalid-token")
    
    @patch('app.services.slack_service.WebClient')
    def test_account_inactive_error_handling(self, mock_webclient_class):
        """Test that account inactive errors are properly handled."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock account inactive error
        error_response = {"error": "account_inactive"}
        mock_client.auth_test.side_effect = SlackApiError(
            message="Account inactive",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to initialize Slack client: Slack account is inactive"):
            SlackService("xoxb-test-token")
    
    @patch('app.services.slack_service.WebClient')
    def test_other_slack_api_error_handling(self, mock_webclient_class):
        """Test that other Slack API errors are properly handled."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock other API error
        error_response = {"error": "rate_limited"}
        mock_client.auth_test.side_effect = SlackApiError(
            message="Rate limited",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to initialize Slack client: Slack API error during validation: rate_limited"):
            SlackService("xoxb-test-token")
    
    @patch('app.services.slack_service.WebClient')
    def test_auth_test_not_ok_handling(self, mock_webclient_class):
        """Test that auth test failure is properly handled."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock auth test with ok=False
        mock_response = {"ok": False}
        mock_client.auth_test.return_value = mock_response
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to initialize Slack client: Failed to validate Slack bot token: Slack auth test failed"):
            SlackService("xoxb-test-token")
    
    @patch('app.services.slack_service.WebClient')
    def test_generic_error_handling(self, mock_webclient_class):
        """Test that generic errors during validation are handled."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock generic error during auth test
        mock_client.auth_test.side_effect = Exception("Network error")
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to initialize Slack client: Failed to validate Slack bot token: Network error"):
            SlackService("xoxb-test-token")
    
    @patch('app.services.slack_service.WebClient')
    def test_bot_token_stored(self, mock_webclient_class):
        """Test that bot token is stored correctly."""
        # Mock the WebClient
        mock_client = Mock()
        mock_webclient_class.return_value = mock_client
        
        # Mock successful auth test
        mock_response = {
            "ok": True,
            "user_id": "U123456",
            "team_id": "T123456"
        }
        mock_client.auth_test.return_value = mock_response
        
        # Test service initialization
        service = SlackService("xoxb-test-token-12345")
        
        # Verify token is stored
        assert service.bot_token == "xoxb-test-token-12345"


class TestSlackServicePostMessage:
    """Test suite for the post_message functionality."""
    
    def _create_mock_service(self):
        """Helper method to create a mock SlackService."""
        with patch('app.services.slack_service.WebClient') as mock_webclient_class:
            mock_client = Mock()
            mock_webclient_class.return_value = mock_client
            
            # Mock successful auth test
            mock_response = {
                "ok": True,
                "user_id": "U123456",
                "team_id": "T123456"
            }
            mock_client.auth_test.return_value = mock_response
            
            service = SlackService("xoxb-test-token")
            return service, mock_client
    
    def test_post_message_success(self):
        """Test successful message posting."""
        service, mock_client = self._create_mock_service()
        
        # Mock successful message posting
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        # Test posting a message
        result = service.post_message("C123456", "Hello world!")
        
        # Verify the result
        assert result is True
        
        # Verify the API was called correctly
        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            text="Hello world!"
        )
    
    def test_post_message_with_thread_ts(self):
        """Test posting a message with thread timestamp."""
        service, mock_client = self._create_mock_service()
        
        # Mock successful message posting
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        # Test posting a message with thread_ts
        result = service.post_message("C123456", "Reply in thread", thread_ts="1234567890.123456")
        
        # Verify the result
        assert result is True
        
        # Verify the API was called correctly
        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            text="Reply in thread",
            thread_ts="1234567890.123456"
        )
    
    def test_post_message_empty_channel_raises_error(self):
        """Test that empty channel raises ValueError."""
        service, mock_client = self._create_mock_service()
        
        with pytest.raises(ValueError, match="Channel cannot be empty or None"):
            service.post_message("", "Hello world!")
    
    def test_post_message_none_channel_raises_error(self):
        """Test that None channel raises ValueError."""
        service, mock_client = self._create_mock_service()
        
        with pytest.raises(ValueError, match="Channel cannot be empty or None"):
            service.post_message(None, "Hello world!")
    
    def test_post_message_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        service, mock_client = self._create_mock_service()
        
        with pytest.raises(ValueError, match="Message text cannot be empty or None"):
            service.post_message("C123456", "")
    
    def test_post_message_none_text_raises_error(self):
        """Test that None text raises ValueError."""
        service, mock_client = self._create_mock_service()
        
        with pytest.raises(ValueError, match="Message text cannot be empty or None"):
            service.post_message("C123456", None)
    
    def test_post_message_whitespace_handling(self):
        """Test that whitespace in channel and text is handled correctly."""
        service, mock_client = self._create_mock_service()
        
        # Mock successful message posting
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        # Test posting with whitespace
        result = service.post_message("  C123456  ", "  Hello world!  ")
        
        # Verify the result
        assert result is True
        
        # Verify whitespace was stripped
        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            text="Hello world!"
        )
    
    def test_post_message_channel_not_found_error(self):
        """Test channel not found error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock channel not found error
        error_response = {"error": "channel_not_found"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Channel not found",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Channel not found: C123456"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_not_in_channel_error(self):
        """Test not in channel error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock not in channel error
        error_response = {"error": "not_in_channel"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Not in channel",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Bot is not in channel: C123456"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_is_archived_error(self):
        """Test archived channel error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock archived channel error
        error_response = {"error": "is_archived"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Channel is archived",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Channel is archived: C123456"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_msg_too_long_error(self):
        """Test message too long error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock message too long error
        error_response = {"error": "msg_too_long"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Message too long",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Message text is too long"):
            service.post_message("C123456", "Very long message...")
    
    def test_post_message_rate_limited_error(self):
        """Test rate limited error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock rate limited error
        error_response = {"error": "rate_limited"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Rate limited",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Rate limit exceeded - please try again later"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_thread_not_found_error(self):
        """Test thread not found error handling."""
        service, mock_client = self._create_mock_service()
        
        # Mock thread not found error
        error_response = {"error": "thread_not_found"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Thread not found",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Thread not found for the provided thread_ts"):
            service.post_message("C123456", "Hello world!", thread_ts="invalid_thread_ts")
    
    def test_post_message_other_slack_api_error(self):
        """Test other Slack API errors."""
        service, mock_client = self._create_mock_service()
        
        # Mock other API error
        error_response = {"error": "some_other_error"}
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="Some other error",
            response=error_response
        )
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Slack API error: some_other_error"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_api_response_not_ok(self):
        """Test when API response is not ok."""
        service, mock_client = self._create_mock_service()
        
        # Mock API response with ok=False
        mock_client.chat_postMessage.return_value = {"ok": False, "error": "some_error"}
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Slack API returned error: some_error"):
            service.post_message("C123456", "Hello world!")
    
    def test_post_message_generic_error_handling(self):
        """Test generic error handling in post_message."""
        service, mock_client = self._create_mock_service()
        
        # Mock generic error
        mock_client.chat_postMessage.side_effect = Exception("Network error")
        
        # Test that proper error is raised
        with pytest.raises(RuntimeError, match="Failed to post message to Slack: Network error"):
            service.post_message("C123456", "Hello world!")


class TestSlackServiceIntegration:
    """Integration tests for Slack service with real API (if available)."""
    
    def test_real_bot_token_integration(self):
        """Test with real bot token if available in environment."""
        import os
        
        # Only run this test if we have a real bot token
        bot_token = os.getenv('SLACK_BOT_TOKEN')
        if not bot_token:
            pytest.skip("No real Slack bot token available")
        
        # Test that service initializes with real bot token
        service = SlackService(bot_token)
        assert service.bot_user_id is not None
        assert service.team_id is not None
        assert service.client is not None
        assert service.bot_token == bot_token 