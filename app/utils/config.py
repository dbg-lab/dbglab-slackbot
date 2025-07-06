# Empty file - Configuration management will be implemented later 

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration management for the Slack chatbot application."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Load and validate required environment variables
        self._load_required_vars()
        
        # Load optional environment variables with defaults
        self._load_optional_vars()
    
    def _load_required_vars(self):
        """Load required environment variables and validate they exist."""
        required_vars = {
            'SLACK_BOT_TOKEN': 'Slack bot token is required',
            'SLACK_SIGNING_SECRET': 'Slack signing secret is required',
            'OPENAI_API_KEY': 'OpenAI API key is required'
        }
        
        for var_name, error_msg in required_vars.items():
            value = os.getenv(var_name)
            if not value:
                raise ValueError(f"Missing required environment variable: {var_name}. {error_msg}")
            setattr(self, var_name.lower(), value)
    
    def _load_optional_vars(self):
        """Load optional environment variables with default values."""
        # OpenAI model (default to gpt-4)
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Flask configuration
        self.flask_env = os.getenv('FLASK_ENV', 'development')
        self.flask_port = int(os.getenv('FLASK_PORT', '3000'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO') 