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

        prompt = f"""
Break down the following requirement into epics strictly in JSON format.
Each epic should have:
- description
- acceptanceCriteria
No extra text, only JSON.

Requirement:
{upload_obj.content['requirement']}
"""

        try:
            epics_json = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        for epic_name, epic_content in epics_json.items():
            epic = Epic(upload_id=upload_obj.id, name=epic_name, content=epic_content)
            db.add(epic)

    return {
        "message": "Epics generated",
        "upload_id": upload_id,
        "epics": epics_json
    }
