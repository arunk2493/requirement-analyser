import os
from config.gemini import generate_text

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "stories_prompt.txt")
    return open(prompt_path).read()

def generate_stories(requirement):
    prompt = load_prompt().replace("{{requirement}}", requirement)
    return generate_text(prompt)
