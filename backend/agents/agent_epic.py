from config.gemini import generate_text

def load_prompt():
    return open("prompts/prompt_epics.txt").read()

def generate_epics(stories):
    prompt = load_prompt().replace("{{stories}}", stories)
    return generate_text(prompt)
