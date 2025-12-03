import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

models = genai.list_models()
for m in models:
    print("Name:", m.name)
    print("ID:", getattr(m, 'id', None))
    print("Description:", getattr(m, 'description', None))
    # supported_methods may not exist in this SDK
    print("-" * 50)

