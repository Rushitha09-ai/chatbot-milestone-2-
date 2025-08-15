import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing environment variables and app settings."""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # App Configuration
    APP_TITLE: str = "LLM Chatbot"
    MAX_MESSAGE_LENGTH: int = 4000
    API_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.OPENAI_API_KEY:
            return False
        return True
    
    @classmethod
    def get_missing_config(cls) -> list:
        """Return list of missing configuration items."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing
