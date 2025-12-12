"""Unified JSON parsing utilities to eliminate code duplication"""
import json
import re
import logging
from typing import Any, Union, List, Dict

logger = logging.getLogger(__name__)


def extract_valid_json(text: str) -> Union[dict, list]:
    """
    Extract valid JSON from text with multiple fallback strategies.
    Handles code fences, single quotes, trailing commas, and malformed JSON.
    
    Args:
        text: Raw text potentially containing JSON
        
    Returns:
        Parsed JSON object or list
        
    Raises:
        ValueError: If no valid JSON could be extracted
    """
    if not text or not isinstance(text, str):
        raise ValueError(f"Invalid input type: {type(text)}")
    
    text = text.strip()
    
    # Strategy 1: Remove code fences (```json, ```python, etc.)
    text = re.sub(r"^```(?:json|python|javascript)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    # Strategy 2: Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Replace single quotes with double quotes (common in AI outputs)
    normalized = text.replace("'", '"')
    try:
        return json.loads(normalized)
    except json.JSONDecodeError:
        pass
    
    # Strategy 4: Remove trailing commas before closing brackets
    cleaned = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Strategy 5: Extract first {...} or [...]
    for pattern in [r"(\[.*\])", r"(\{.*\})"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted = match.group(1)
            # Try with cleaned version
            cleaned = re.sub(r",(\s*[}\]])", r"\1", extracted)
            cleaned = cleaned.replace("'", '"')
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue
    
    # Strategy 6: Try to convert dict response to array format
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            # If it's a dict with numeric keys, convert to list
            if all(key.isdigit() or key.startswith('item') for key in obj.keys()):
                return list(obj.values())
            return obj
        return obj
    except json.JSONDecodeError:
        pass
    
    logger.error(f"Failed to extract JSON from text: {text[:200]}...")
    raise ValueError("Could not extract valid JSON from model output after all strategies.")


def parse_model_json(raw_output: Any) -> Union[dict, list]:
    """
    Parse JSON from model output, handling both direct objects and strings.
    
    Args:
        raw_output: Raw output from model (could be string or already parsed)
        
    Returns:
        Parsed JSON object or list
        
    Raises:
        ValueError: If parsing fails
    """
    if isinstance(raw_output, (dict, list)):
        return raw_output
    
    if isinstance(raw_output, str):
        return extract_valid_json(raw_output)
    
    raise ValueError(f"Unexpected output type: {type(raw_output)}")


def ensure_list(data: Any) -> List:
    """
    Ensure data is a list, converting single objects to single-item lists.
    
    Args:
        data: Data to ensure is a list
        
    Returns:
        List version of data
        
    Raises:
        ValueError: If data cannot be converted to list
    """
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        raise ValueError(f"Cannot convert {type(data)} to list")


def ensure_dict_list(data: Any) -> List[Dict]:
    """
    Ensure data is a list of dictionaries.
    
    Args:
        data: Data to ensure is list of dicts
        
    Returns:
        List of dictionaries
        
    Raises:
        ValueError: If conversion fails
    """
    data_list = ensure_list(data)
    if not all(isinstance(item, dict) for item in data_list):
        raise ValueError("Not all items in list are dictionaries")
    return data_list
