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

STORY_GENERATION_PROMPT = """
Break down the following epic into multiple user stories strictly in JSON format.
Each story should have:
- name
- type
- description
- acceptanceCriteria
- implementationDetails (if technical)
No extra text, only JSON.

Epic content:
{epic_content}
"""


@router.post("/generate-stories/{epic_id}")
def generate_stories(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Generate user stories from an epic.
    
    Args:
        epic_id: ID of the epic
        current_user: Authenticated user
        
    Returns:
        Generated stories
    """
    logger.info(f"generate_stories: user={current_user.email}, epic_id={epic_id}")
    
    with get_db_context() as db:
        service = ContentGenerationService(db)
        
        try:
            # Generate stories
            stories_data = service.generate_stories(epic_id, STORY_GENERATION_PROMPT)
            
            # Save stories
            saved_stories = service.save_stories(epic_id, stories_data)
            
            response_array = [
                {
                    "id": story_id,
                    "story": story_data
                }
                for story_id, story_data in saved_stories
            ]
            
            return {
                "message": "Stories generated successfully",
                "epic_id": epic_id,
                "stories": response_array
            }
            
        except Exception as e:
            logger.error(f"Failed to generate stories: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Story generation failed: {str(e)}"
            )
