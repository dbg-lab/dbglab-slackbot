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
    
    def post_message(self, channel: str, text: str, thread_ts: Optional[str] = None) -> bool:
        """
        Post a message to a Slack channel.
        
        Args:
            channel: Channel ID (e.g., 'C1234567890') or channel name (e.g., 'general')
            text: Message text to post
            thread_ts: Optional thread timestamp for thread replies
            
        Returns:
            bool: True if message was posted successfully, False otherwise
            
        Raises:
            ValueError: If channel or text is empty
            RuntimeError: If API call fails with specific error details
        """
        if not channel or not channel.strip():
            raise ValueError("Channel cannot be empty or None")
        
        if not text or not text.strip():
            raise ValueError("Message text cannot be empty or None")
        
        try:
            # Prepare the message parameters
            message_params = {
                "channel": channel.strip(),
                "text": text.strip()
            }
            
            # Add thread timestamp if provided
            if thread_ts:
                message_params["thread_ts"] = thread_ts
            
            # Call Slack Web API to post the message
            response = self.client.chat_postMessage(**message_params)
            
            # Check if the message was posted successfully
            if response.get("ok"):
                return True
            else:
                raise RuntimeError(f"Slack API returned error: {response.get('error', 'Unknown error')}")
                
        except SlackApiError as e:
            error_code = e.response.get("error", "unknown")
            
            if error_code == "channel_not_found":
                raise RuntimeError(f"Channel not found: {channel}")
            elif error_code == "not_in_channel":
                raise RuntimeError(f"Bot is not in channel: {channel}")
            elif error_code == "is_archived":
                raise RuntimeError(f"Channel is archived: {channel}")
            elif error_code == "msg_too_long":
                raise RuntimeError("Message text is too long")
            elif error_code == "rate_limited":
                raise RuntimeError("Rate limit exceeded - please try again later")
            elif error_code == "invalid_auth":
                raise RuntimeError("Invalid authentication token")
            elif error_code == "thread_not_found":
                raise RuntimeError("Thread not found for the provided thread_ts")
            else:
                raise RuntimeError(f"Slack API error: {error_code}")
        
        except Exception as e:
            raise RuntimeError(f"Failed to post message to Slack: {e}") 