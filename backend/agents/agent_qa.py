from config.gemini import generate_text

def load_prompt():
    return open("prompts/prompt_qa.txt").read()

def generate_qa(stories, epics, framework):
    prompt = load_prompt()
    prompt = prompt.replace("{{stories}}", stories)
    prompt = prompt.replace("{{epics}}", epics)
    prompt = prompt.replace("{{framework}}", framework)
    return generate_text(prompt)
