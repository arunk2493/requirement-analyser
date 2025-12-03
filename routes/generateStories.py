from fastapi import APIRouter, HTTPException, Depends
from models.file_model import Epic, Story
from config.gemini import generate_json
from config.db import get_db
from config.dependencies import get_current_user
from config.auth import TokenData

router = APIRouter()

@router.post("/generate-stories/{epic_id}")
def generate_stories(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    with get_db() as db:
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
