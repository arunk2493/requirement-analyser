from fastapi import APIRouter, HTTPException
from models.file_model import Story, QA
from config.gemini import generate_json
from config.db import get_db

router = APIRouter()

@router.post("/generate-qa/{story_id}")
def generate_qa(story_id: int):
    with get_db() as db:
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        prompt = f"""
Generate QA test cases for the following user story strictly in JSON.
Each test should include:
- title
- steps
- expectedOutcome

Return JSON:
[
  {{
    "title": "",
    "steps": [],
    "expectedOutcome": ""
  }}
]
User Story:
{story_obj.content}
"""

        try:
            qa_list = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        if not isinstance(qa_list, list):
            raise HTTPException(status_code=400, detail="Expected an array of QA objects")

        saved_tests = []

        for qa_item in qa_list:
            qa_obj = QA(
                story_id=story_id,
                type="qa",
                content=qa_item              # <-- FIXED HERE
            )
            db.add(qa_obj)
            db.flush()

            saved_tests.append({
                "id": qa_obj.id,
                "content": qa_item
            })

        return {
            "message": "QA generated",
            "story_id": story_id,
            "qa": saved_tests
        }
