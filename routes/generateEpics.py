from fastapi import APIRouter, HTTPException
from models.file_model import Upload, Epic
from config.gemini import generate_json
from config.db import get_db

router = APIRouter()

@router.post("/generate-epics/{upload_id}")
def generate_epics(upload_id: int):
    with get_db() as db:
        upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload_obj:
            raise HTTPException(status_code=404, detail="Upload not found")

        requirement_text = upload_obj.content

        prompt = f"""
You MUST return JSON ONLY.

FORMAT:
[
  {{
    "name": "Epic title",
    "description": "Detailed description",
    "acceptanceCriteria": ["item1", "item2"]
  }}
]

RULES:
- Only return JSON. No explanations.
- Always return an ARRAY.
- No backticks, no comments, no labels like 'Epic 1'.

Requirement:
{requirement_text}
"""

        try:
            epics = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        if not isinstance(epics, list):
            raise HTTPException(status_code=400, detail="Expected an array of epic objects")

        result = []

        for epic_data in epics:
            epic = Epic(
                upload_id=upload_id,
                content=epic_data,
                name=epic_data.get("name")
            )
            db.add(epic)
            db.flush()

            result.append({
                "id": epic.id,
                "name": epic.name
            })

        db.commit()

        return {
            "message": "Epics generated",
            "upload_id": upload_id,
            "epics": result
        }