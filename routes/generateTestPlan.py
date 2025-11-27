# routes/generateTestPlan.py

from fastapi import APIRouter, HTTPException
from models.file_model import Story, QA
from config.gemini import generate_json
from config.db import get_db

router = APIRouter()


@router.post("/generate-testplan/{story_id}")
def generate_testplan(story_id: int):
    with get_db() as db:

        # Get story
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        # Prompt for Gemini
        prompt = f"""
Generate a detailed test plan only in STRICT JSON format.
The JSON must be an array of testPlan objects.

Each test plan object should contain:
- title
- objective
- preconditions
- testScenarios (array)
- risks
- mitigationStrategies
- testing types (e.g., functional, performance, security)

DO NOT ADD any text outside JSON.
DO NOT wrap JSON inside keys.

Story:
{story_obj.content}
"""

        # Generate JSON output
        try:
            testplan_list = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Validate array
        if not isinstance(testplan_list, list):
            raise HTTPException(status_code=400, detail="Expected an array of test plan objects")

        saved_items = []

        # Save each test plan entry
        for plan in testplan_list:
            testplan_db = QA(
                story_id=story_id,
                type="test_plan",      # <--- correct field
                content=plan           # <--- store actual JSON
            )
            db.add(testplan_db)
            db.flush()  # Get generated ID

            saved_items.append({
                "id": testplan_db.id,
                "content": plan
            })

        db.commit()

    return {
        "message": "Test plan generated",
        "story_id": story_id,
        "test_plan": saved_items
    }
