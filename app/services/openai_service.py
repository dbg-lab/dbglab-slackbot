from typing import Optional
import openai
from openai import OpenAI


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