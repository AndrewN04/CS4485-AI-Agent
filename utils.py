import os
import logging
import re
import time
import json
from functools import wraps

logger = logging.getLogger(__name__)

def timeit(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute")
        return result
    return wrapper

def retry(max_attempts=3, delay=1):
    """
    Decorator to retry a function on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (doubles after each failure)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempts} failed for function {func.__name__}. Retrying in {current_delay}s. Error: {e}")
                    time.sleep(current_delay)
                    current_delay *= 2
                    
            return func(*args, **kwargs)  # Final attempt
        return wrapper
    return decorator

def safe_json_loads(json_str, default=None):
    """
    Safely parse JSON string with error handling.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    try:
        # Clean up the JSON string
        cleaned_json = json_str.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_json)
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return default

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")

def normalize_item_name(name):
    """
    Normalize item name for better matching.
    
    Args:
        name: Item name to normalize
        
    Returns:
        Normalized item name
    """
    if not name:
        return ""
        
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove articles and common words
    for word in ["a", "an", "the", "of", "with", "and"]:
        normalized = re.sub(r'\b' + word + r'\b', '', normalized)
    
    # Remove extra spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def format_price(price):
    """Format price with dollar sign and two decimal places."""
    return f"${price:.2f}"

def format_currency(amount):
    """Format currency amount with commas for thousands separator."""
    return "${:,.2f}".format(amount)

def truncate_text(text, max_length=100):
    """Truncate text to specified maximum length and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."