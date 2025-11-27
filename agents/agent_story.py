from config.gemini import generate_text

def load_prompt():
    return open("prompts/prompt_stories.txt").read()

def generate_stories(requirement):
    prompt = load_prompt().replace("{{requirement}}", requirement)
    return generate_text(prompt)
