import os
from config.gemini import generate_text

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "qa_prompt.txt")
    return open(prompt_path).read()

def generate_qa(stories, epics, framework):
    prompt = load_prompt()
    prompt = prompt.replace("{{stories}}", stories)
    prompt = prompt.replace("{{epics}}", epics)
    prompt = prompt.replace("{{framework}}", framework)
    return generate_text(prompt)
