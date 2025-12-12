import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends, status
from config.db import get_db_context
from config.auth import get_current_user, TokenData
from services.content_generator import ContentGenerationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

QA_GENERATION_PROMPT = """
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
{story_content}
"""


@router.post("/generate-qa/{story_id}")
def generate_qa(story_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Generate QA test cases from a user story.
    
    Args:
        story_id: ID of the story
        current_user: Authenticated user
        
    Returns:
        Generated QA test cases
    """
    logger.info(f"generate_qa: user={current_user.email}, story_id={story_id}")
    
    with get_db_context() as db:
        service = ContentGenerationService(db)
        
        try:
            # Generate QA tests
            qa_data = service.generate_qa(story_id, QA_GENERATION_PROMPT)
            
            # Save QA tests
            saved_qa = service.save_qa(story_id, qa_data, qa_type="qa")
            
            saved_tests = [
                {
                    "id": qa_id,
                    "content": qa_item
                }
                for qa_id, qa_item in saved_qa
            ]
            
            return {
                "message": "QA tests generated successfully",
                "story_id": story_id,
                "qa": saved_tests
            }
            
        except Exception as e:
            logger.error(f"Failed to generate QA: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"QA generation failed: {str(e)}"
            )
