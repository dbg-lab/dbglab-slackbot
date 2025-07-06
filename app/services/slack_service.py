from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackService:
    """Service for interacting with Slack Web API."""
    
    def __init__(self, bot_token: str):
        """
        Initialize Slack service.
        
        Args:
            bot_token: Slack bot token (starts with xoxb-)
            
        Raises:
            ValueError: If bot token is empty or None
            RuntimeError: If bot token is invalid or API test fails
        """
        if not bot_token:
            raise ValueError("Slack bot token cannot be empty or None")
        
        if not bot_token.startswith('xoxb-'):
            raise ValueError("Invalid Slack bot token format - must start with 'xoxb-'")
        
        self.bot_token = bot_token
        
        try:
            # Initialize Slack WebClient with bot token
            self.client = WebClient(token=bot_token)
            
            # Test the bot token by calling auth.test
            self._validate_bot_token()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Slack client: {e}")
    
    def _validate_bot_token(self):
        """Validate the bot token by calling auth.test API."""
        try:
            # Test the token with auth.test API call
            response = self.client.auth_test()
            
            if not response.get("ok"):
                raise RuntimeError("Slack auth test failed")
            
            # Store bot info for later use
            self.bot_user_id = response.get("user_id")
            self.team_id = response.get("team_id")
            
        except SlackApiError as e:
            if e.response["error"] == "invalid_auth":
                raise RuntimeError("Invalid Slack bot token")
            elif e.response["error"] == "account_inactive":
                raise RuntimeError("Slack account is inactive")
            else:
                raise RuntimeError(f"Slack API error during validation: {e.response['error']}")
        except Exception as e:
            raise RuntimeError(f"Failed to validate Slack bot token: {e}") 