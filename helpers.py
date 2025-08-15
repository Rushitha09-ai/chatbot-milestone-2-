import re
import html

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other security issues.
    
    Args:
        text (str): Raw user input
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # HTML escape
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > 4000:
        text = text[:4000] + "..."
    
    return text.strip()

def format_response_time(response_time: float) -> str:
    """Format response time for display."""
    if response_time < 1:
        return f"{response_time * 1000:.0f}ms"
    else:
        return f"{response_time:.2f}s"
