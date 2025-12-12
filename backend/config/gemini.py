import google.generativeai as genai
from config.config import GEMINI_API_KEY
import logging

logger = logging.getLogger(__name__)

# Configure API key
genai.configure(api_key=GEMINI_API_KEY)

# Default model
DEFAULT_MODEL = "models/gemini-2.5-flash"  # safer than gemini-1.5-pro if unavailable


def generate_text(prompt: str) -> str:
    """
    Call Gemini to generate text.
    
    Args:
        prompt: Input prompt for generation
        
    Returns:
        Generated text
    """
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        logger.debug("Text generation completed successfully")
        return response.text
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise


def generate_json(prompt: str):
    """
    Call Gemini to generate JSON content.
    Uses unified JSON parser from utils for consistency.
    
    Args:
        prompt: Input prompt for generation
        
    Returns:
        Parsed JSON object or list
        
    Raises:
        ValueError: If JSON extraction fails
    """
    from utils.json_parser import extract_valid_json
    
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        logger.debug("JSON generation completed, parsing response")
        
        text = response.text
        return extract_valid_json(text)
    except Exception as e:
        logger.error(f"Error generating JSON: {str(e)}")
        raise