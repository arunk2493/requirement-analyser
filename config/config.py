import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CONFLUENCE_URL = os.getenv("confluence_url")
CONFLUENCE_USERNAME = os.getenv("confluence_username")
CONFLUENCE_PASSWORD = os.getenv("confluence_password")
CONFLUENCE_SPACE_KEY = os.getenv("confluence_space_key")
CONFLUENCE_ROOT_FOLDER_ID = os.getenv("confluence_root_folder_id")