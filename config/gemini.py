import google.generativeai as genai
from config.config import GEMINI_API_KEY
import json
import re

# Configure API key
genai.configure(api_key=GEMINI_API_KEY)

# Default model
DEFAULT_MODEL = "models/gemini-2.5-flash"  # safer than gemini-1.5-pro if unavailable


def generate_text(prompt: str) -> str:
    """
    Call Gemini to generate text
    """
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Error generating text:", e)
        return ""

def extract_json_from_text(text: str) -> dict:
    """
    Extract the first valid JSON object from text by counting braces.
    Handles nested JSON and ignores extra text before/after.
    """
    stack = []
    start_idx = None
    for idx, char in enumerate(text):
        if char == '{':
            if not stack:
                start_idx = idx
            stack.append('{')
        elif char == '}':
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    json_str = text[start_idx:idx+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        raise ValueError(f"Cannot parse JSON: {json_str}")
    raise ValueError(f"No valid JSON found in response:\n{text}")

def generate_json(prompt: str) -> dict:
    """
    Call Gemini and safely extract the first JSON object
    """
    response = generate_text(prompt)
    if not response:
        raise ValueError("Empty response from Gemini")
    return extract_json_from_text(response)