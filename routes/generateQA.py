from fastapi import APIRouter, HTTPException
from models.file_model import Story, QA, Epic, AggregatedUpload
from config.gemini import generate_json
from config.db import get_db

router = APIRouter()

@router.post("/generate-qa/{story_id}")
def generate_qa(story_id: int):
    with get_db() as db:
        # Fetch the story
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        prompt = f"""
Create QA artifacts for the following story strictly in JSON format.
Include:
- test_plan
- api_tests (with steps, prerequisites, expected/actual)
- automation_scripts (Java RestAssured or Karate DSL)
Output either a JSON array or a dictionary of QA entries. No extra text.

Story content:
{story_obj.content}
"""

        try:
            qa_raw = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Normalize to a list of QA objects
        if isinstance(qa_raw, dict):
            qa_list = [
                {"type": k, **v} if isinstance(v, dict) else {"type": k, "content": v}
                for k, v in qa_raw.items()
            ]
        elif isinstance(qa_raw, list):
            qa_list = qa_raw
        else:
            raise HTTPException(status_code=500, detail="Unexpected QA response format from Gemini")

        response_array = []
        # Store each QA entry with a unique ID
        for qa_item in qa_list:
            qa_obj = QA(
                story_id=story_obj.id,
                type=qa_item.get("type", "general"),
                content=qa_item
            )
            db.add(qa_obj)
            db.flush()  # assign unique ID
            response_array.append({
                "id": qa_obj.id,
                "qa": qa_item
            })

        db.commit()  # commit all QA entries

        # Build aggregated JSON for the upload
        epic_obj = db.query(Epic).filter(Epic.id == story_obj.epic_id).first()
        upload_id = epic_obj.upload_id

        aggregated_json = {}
        epics = db.query(Epic).filter(Epic.upload_id == upload_id).all()
        for e in epics:
            stories_list = []
            for s in db.query(Story).filter(Story.epic_id == e.id).all():
                qa_entries = [
                    {"id": q.id, "qa": q.content} for q in db.query(QA).filter(QA.story_id == s.id).all()
                ]
                stories_list.append({
                    "id": s.id,
                    "name": s.name,
                    "content": s.content,
                    "qa": qa_entries
                })
            aggregated_json[e.name] = {"stories": stories_list}

        agg_obj = AggregatedUpload(upload_id=upload_id, content=aggregated_json)
        db.add(agg_obj)
        db.commit()

    return {
        "message": "QA generated and aggregated",
        "story_id": story_id,
        "upload_id": upload_id,
        "qa": response_array,          # array of {id, qa}
        "aggregated": aggregated_json  # full aggregated JSON
    }
