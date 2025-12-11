import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends
from models.file_model import Story, QA
from config.gemini import generate_json
from config.db import get_db, get_db_context
from config.auth import get_current_user, TokenData
from rag.vectorstore import VectorStore
import json
import re
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
vectorstore = VectorStore()

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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"generate_qa: Authenticated user={current_user.email}, user_id={current_user.user_id}")
    
    with get_db_context() as db:
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
            
            # Index QA test in vectorstore for RAG
            qa_text = f"QA Test: {qa_item.get('title', '')}\nAPI Endpoint: {qa_item.get('apiEndpoint', '')}\nMethod: {qa_item.get('method', '')}\nValidation Steps: {', '.join(qa_item.get('validationSteps', []))}"
            doc_id = f"qa_{qa_obj.id}_{str(uuid.uuid4())[:8]}"
            try:
                vectorstore.store_document(qa_text, doc_id, metadata={
                    "type": "qa",
                    "qa_id": qa_obj.id,
                    "story_id": story_id
                })
            except Exception as e:
                print(f"Warning: Could not index QA in vectorstore: {e}")

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
