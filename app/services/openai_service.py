from typing import Optional
import openai
from openai import OpenAI
import re


class OpenAIService:
    """Service for interacting with OpenAI Chat Completions API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
        
        Raises:
            ValueError: If API key is empty or None
        """
        if not api_key:
            raise ValueError("OpenAI API key cannot be empty or None")
        
        self.model = model
        
        try:
            # Initialize OpenAI client with API key
            self.client = OpenAI(api_key=api_key)
            
            # Test the API key by making a simple request
            # This will raise an exception if the API key is invalid
            self._validate_api_key()
            
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    
    def _validate_api_key(self):
        """Validate the API key by making a test request."""
        try:
            # Make a minimal test request to validate the API key
            # This will throw an exception if the key is invalid
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            # If we get here, the API key is valid
            
        except openai.AuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except openai.RateLimitError:
            # Rate limit is fine - means API key is valid
            pass
        except Exception as e:
            # Other errors during validation
            raise ValueError(f"OpenAI API key validation failed: {e}")
    
    def format_slack_message(self, message: str) -> str:
        """
        Format Slack message by cleaning up Slack-specific formatting.
        
        Args:
            message: Raw message from Slack
            
        Returns:
            Cleaned message with Slack formatting removed
        """
        if not message:
            return ""
        
        # Remove user mentions like <@U123456> or <@U123456|username>
        message = re.sub(r'<@U[A-Z0-9]+(?:\|[^>]+)?>', '', message)
        
        # Remove channel mentions like <#C123456> or <#C123456|channel-name>
        message = re.sub(r'<#C[A-Z0-9]+(?:\|[^>]+)?>', '', message)
        
        # Remove link formatting like <https://example.com|Link Text> -> Link Text
        # or <https://example.com> -> https://example.com
        message = re.sub(r'<(https?://[^|>]+)\|([^>]+)>', r'\2', message)  # Link with text
        message = re.sub(r'<(https?://[^>]+)>', r'\1', message)  # Link without text
        
        # Remove special formatting characters
        # Bold: *text* -> text
        message = re.sub(r'\*([^*]+)\*', r'\1', message)
        
        # Italic: _text_ -> text  
        message = re.sub(r'_([^_]+)_', r'\1', message)
        
        # Code: `text` -> text
        message = re.sub(r'`([^`]+)`', r'\1', message)
        
        # Strikethrough: ~text~ -> text
        message = re.sub(r'~([^~]+)~', r'\1', message)
        
        # Clean up multiple spaces and strip
        message = re.sub(r'\s+', ' ', message).strip()
        
        return message
    
    def get_chat_completion(self, message: str) -> str:
        """
        Get chat completion response from OpenAI.
        
        Args:
            message: User message text to send to OpenAI
            
        Returns:
            Response text from OpenAI
            
        Raises:
            ValueError: If message is empty or None
            RuntimeError: If OpenAI API call fails
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty or None")
        
        # Format the message to remove Slack-specific formatting
        formatted_message = self.format_slack_message(message)
        
        # Check again after formatting
        if not formatted_message.strip():
            raise ValueError("Message cannot be empty after formatting")
        
        try:
            # Call OpenAI Chat Completions API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": formatted_message.strip()}
                ],
                max_tokens=1000,  # Reasonable limit for responses
                temperature=0.7   # Balanced creativity
            )
            
            # Extract response text from API response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                raise RuntimeError("OpenAI API returned empty response")
                
        except openai.AuthenticationError:
            raise RuntimeError("OpenAI API authentication failed")
        except openai.RateLimitError:
            raise RuntimeError("OpenAI API rate limit exceeded - please try again later")
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to get OpenAI response: {e}") 