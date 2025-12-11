import os
from config.gemini import generate_text

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "epics_prompt.txt")
    return open(prompt_path).read()

def generate_epics(stories):
    prompt = load_prompt().replace("{{stories}}", stories)
    return generate_text(prompt)
