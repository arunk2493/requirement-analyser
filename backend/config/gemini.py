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

def extract_valid_json(text: str):
    # Remove code fences
    text = re.sub(r"```json|```", "", text).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # Extract first {...} or [...]
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        extracted = match.group(1)
        try:
            return json.loads(extracted)
        except:
            pass

    # Convert object → array
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return [v for v in obj.values()]
    except:
        pass

    raise ValueError("Could not extract valid JSON from model output.")


def generate_json(prompt: str):
    model = genai.GenerativeModel(DEFAULT_MODEL)
    response = model.generate_content(prompt)

    text = response.text
    return extract_valid_json(text)