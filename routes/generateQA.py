from fastapi import APIRouter, HTTPException, Depends
from models.file_model import Story, QA
from config.gemini import generate_json
from config.db import get_db
from config.dependencies import get_current_user
from config.auth import TokenData
import json
import re

router = APIRouter()

def safe_parse_json(output):
    """
    Ensures the model output is a Python list.
    Cleans strings from backticks, single quotes, trailing commas if needed.
    """
    if isinstance(output, list):
        return output  # Already a list, nothing to do

    if not isinstance(output, str):
        raise ValueError(f"Unexpected type from model: {type(output)}")

    text = output.strip()

    # Remove code block backticks if present
    import re
    text = re.sub(r"^```json|```$", "", text, flags=re.IGNORECASE)

    # Replace single quotes with double quotes (common GPT issue)
    text = text.replace("'", '"')

    # Remove trailing commas before closing brackets
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    import json
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {str(e)}\nRaw output: {text}")


@router.post("/generate-qa/{story_id}")
def generate_qa(story_id: int, current_user: TokenData = Depends(get_current_user)):
    with get_db() as db:
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        prompt = f"""
Generate QA test cases for the following user story strictly in JSON.
Each object in the array must include:
- title
- apiEndpoint
- method
- request
- response
- validationSteps (array)
- automationScript (Karate DSL or RestAssured)

NO comments. NO text outside JSON.

User Story:
{story_obj.content}
"""

        try:
            raw_output = generate_json(prompt)
            qa_list = safe_parse_json(raw_output)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Could not extract valid JSON from model output: {str(e)}")

        if not isinstance(qa_list, list):
            raise HTTPException(status_code=400, detail="Expected an array of QA objects")

        saved_tests = []

        for qa_item in qa_list:
            qa_obj = QA(
                story_id=story_id,
                type="qa",
                content=qa_item
            )
            db.add(qa_obj)
            db.flush()

            saved_tests.append({
                "id": qa_obj.id,
                "content": qa_item
            })

        db.commit()

        return {
            "message": "QA generated",
            "story_id": story_id,
            "qa": saved_tests
        }
