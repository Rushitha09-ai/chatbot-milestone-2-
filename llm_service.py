import openai
from typing import Dict, Any, Optional
import logging
import time
from config import Config

class LLMService:
    """Enhanced service class for handling multiple LLM models."""
    
    def __init__(self):
        """Initialize the LLM service with API configuration."""
        if not Config.validate_config():
            missing = Config.get_missing_config()
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
        
        # Available models with their configurations
        self.models = {
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "description": "Fast and efficient for most tasks",
                "cost_per_1k": 0.0015,
                "max_tokens": 4096,
                "supports_functions": True
            },
            "gpt-4": {
                "name": "GPT-4",
                "description": "Most capable model for complex tasks",
                "cost_per_1k": 0.03,
                "max_tokens": 8192,
                "supports_functions": True
            },
            "gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "description": "Latest GPT-4 with improved speed",
                "cost_per_1k": 0.01,
                "max_tokens": 128000,
                "supports_functions": True
            }
        }
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Return available models and their configurations."""
        return self.models
    
    def estimate_cost(self, message: str, model: str = "gpt-3.5-turbo") -> float:
        """Estimate the cost of a message for a given model."""
        if model not in self.models:
            return 0.0
        
        # Rough token estimation (1 token  4 characters)
        estimated_tokens = len(message) / 4
        cost_per_1k = self.models[model]["cost_per_1k"]
        return (estimated_tokens / 1000) * cost_per_1k
    
    def send_message(self, message: str, model: str = "gpt-3.5-turbo", 
                    temperature: float = 0.7, max_tokens: int = 1000,
                    system_prompt: str = None) -> Dict[str, Any]:
        """
        Send a message to the LLM and return the response.
        
        Args:
            message (str): The user's message
            model (str): The OpenAI model to use
            temperature (float): Response creativity (0.0-2.0)
            max_tokens (int): Maximum response length
            system_prompt (str): Optional system prompt for behavior
            
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
        
        # Validate model
        if model not in self.models:
            model = "gpt-3.5-turbo"  # Fallback to default
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        start_time = time.time()
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=min(max_tokens, self.models[model]["max_tokens"]),
                    temperature=max(0.0, min(2.0, temperature)),  # Clamp temperature
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
                        "tokens_used": response.usage.total_tokens if response.usage else None,
                        "estimated_cost": self.estimate_cost(message, model)
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
    
    def test_connection(self, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Test the API connection with a simple message."""
        return self.send_message("Hello! This is a connection test.", model=model)
