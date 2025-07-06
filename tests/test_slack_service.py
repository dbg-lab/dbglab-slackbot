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