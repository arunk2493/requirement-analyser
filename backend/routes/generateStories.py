import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends
from models.file_model import Epic, Story
from config.gemini import generate_json
from config.db import get_db, get_db_context
from config.auth import get_current_user, TokenData
from rag.vectorstore import VectorStore
import uuid
import json

router = APIRouter()
vectorstore = VectorStore()

@router.post("/generate-stories/{epic_id}")
def generate_stories(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"generate_stories: Authenticated user={current_user.email}, user_id={current_user.user_id}")
    
    with get_db_context() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")

        prompt = f"""
Break down the following epic into multiple user stories strictly in JSON format.
Each story should have:
- name
- type
- description
- acceptanceCriteria
- implementationDetails (if technical)
No extra text, only JSON.

Epic content:
{epic_obj.content}
"""

        try:
            stories_raw = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Normalize response to a list of story objects
        if isinstance(stories_raw, dict):
            stories_list = [
                {"name": k, **v} if isinstance(v, dict) else {"name": k, "content": v}
                for k, v in stories_raw.items()
            ]
        elif isinstance(stories_raw, list):
            stories_list = stories_raw
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format from Gemini")

        response_array = []
        for story_item in stories_list:
            story = Story(
                epic_id=epic_obj.id,
                name=story_item.get("name", "Unnamed Story"),
                content=story_item
            )
            db.add(story)
            db.flush()  # assigns ID
            
            # Index story in vectorstore for RAG
            story_text = f"Story: {story.name}\nType: {story_item.get('type', '')}\nDescription: {story_item.get('description', '')}\nAcceptance Criteria: {', '.join(story_item.get('acceptanceCriteria', []))}"
            doc_id = f"story_{story.id}_{str(uuid.uuid4())[:8]}"
            try:
                vectorstore.store_document(story_text, doc_id, metadata={
                    "type": "story",
                    "story_id": story.id,
                    "epic_id": epic_obj.id,
                    "story_name": story.name
                })
            except Exception as e:
                print(f"Warning: Could not index story in vectorstore: {e}")
            
            response_array.append({
                "id": story.id,
                "story": story_item
            })

        db.commit()

    return {
        "message": "Stories generated",
        "epic_id": epic_id,
        "stories": response_array
    }
