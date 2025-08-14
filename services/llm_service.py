import openai
from typing import Dict, Any, Optional
import logging
import time
from config import Config

class LLMService:
    """Service class for handling LLM API communications."""
    
    def __init__(self):
        """Initialize the LLM service with API configuration."""
        if not Config.validate_config():
            missing = Config.get_missing_config()
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        Send a message to the LLM and return the response.
        
        Args:
            message (str): The user's message
            model (str): The OpenAI model to use
            
        Returns:
            Dict containing 'success', 'response', 'error', 'response_time'
        """
        if not message or not message.strip():
            return {
                "success": False,
                "response": None,
                "error": "Empty message provided",
                "response_time": 0
            }
        
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            return {
                "success": False,
                "response": None,
                "error": f"Message too long. Maximum {Config.MAX_MESSAGE_LENGTH} characters allowed.",
                "response_time": 0
            }
        
        start_time = time.time()
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": message}
                    ],
                    max_tokens=1000,
                    timeout=Config.API_TIMEOUT
                )
                
                response_time = time.time() - start_time
                
                if response.choices and response.choices[0].message:
                    return {
                        "success": True,
                        "response": response.choices[0].message.content,
                        "error": None,
                        "response_time": response_time,
                        "model_used": model,
                        "tokens_used": response.usage.total_tokens if response.usage else None
                    }
                else:
                    return {
                        "success": False,
                        "response": None,
                        "error": "Empty response from API",
                        "response_time": response_time
                    }
                    
            except openai.APIError as e:
                self.logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt == Config.MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "response": None,
                        "error": f"API Error: {str(e)}",
                        "response_time": time.time() - start_time
                    }
                time.sleep(1)
                
            except openai.RateLimitError as e:
                self.logger.error(f"Rate limit exceeded (attempt {attempt + 1}): {e}")
                if attempt == Config.MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "response": None,
                        "error": "Rate limit exceeded. Please try again later.",
                        "response_time": time.time() - start_time
                    }
                time.sleep(2)
                
            except openai.AuthenticationError as e:
                return {
                    "success": False,
                    "response": None,
                    "error": "Invalid API key. Please check your configuration.",
                    "response_time": time.time() - start_time
                }
                
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == Config.MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "response": None,
                        "error": f"Unexpected error: {str(e)}",
                        "response_time": time.time() - start_time
                    }
                time.sleep(1)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection with a simple message."""
        return self.send_message("Hello! This is a connection test.")
