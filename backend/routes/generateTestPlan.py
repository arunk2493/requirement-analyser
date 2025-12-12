import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends, status
from config.db import get_db_context
from config.auth import get_current_user, TokenData
from atlassian import Confluence
from config.config import CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD, CONFLUENCE_SPACE_KEY
from services.content_generator import ContentGenerationService
from utils.confluence_helper import add_timestamp, create_confluence_html_content, build_confluence_page
from models.file_model import Epic, QA
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Confluence client once
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    password=CONFLUENCE_PASSWORD
)

SPACE_KEY = CONFLUENCE_SPACE_KEY

TESTPLAN_GENERATION_PROMPT = """
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

Epic:
{epic_content}
"""


@router.post("/generate-testplan/{epic_id}")
def generate_testplan(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Generate test plans from an epic.
    
    Args:
        epic_id: ID of the epic
        current_user: Authenticated user
        
    Returns:
        Generated test plans with Confluence pages
    """
    logger.info(f"generate_testplan: user={current_user.email}, epic_id={epic_id}")
    
    with get_db_context() as db:
        service = ContentGenerationService(db)
        
        try:
            # Fetch epic to verify it exists
            epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
            if not epic_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Epic not found")
            
            if not epic_obj.confluence_page_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Epic does not have a Confluence page. Generate epics first."
                )
            
            # Generate test plans
            testplan_data = service.generate_test_plan(epic_id, TESTPLAN_GENERATION_PROMPT)
            
            # Save test plans
            saved_testplans = service.save_qa(epic_id, testplan_data, qa_type="test_plan")
            
            saved_items = []
            for testplan_id, testplan_item in saved_testplans:
                # Create Confluence page for test plan
                section_configs = {"testScenarios": {"is_list": True, "heading_level": 3}}
                testplan_content = create_confluence_html_content(
                    f"Test Plan: {testplan_item.get('title', 'Test Plan')}",
                    testplan_item,
                    section_configs
                )
                
                testplan_page = build_confluence_page(
                    confluence,
                    SPACE_KEY,
                    add_timestamp(testplan_item.get("title", "Test Plan")),
                    testplan_content,
                    epic_obj.confluence_page_id
                )
                
                # Update test plan with confluence page ID
                testplan_obj = db.query(QA).filter(QA.id == testplan_id).first()
                testplan_obj.confluence_page_id = testplan_page['id']
                db.commit()
                
                saved_items.append({
                    "id": testplan_id,
                    "title": testplan_item.get("title", "Test Plan"),
                    "confluence_page_id": testplan_page['id']
                })
            
            return {
                "message": "Test plans generated with Confluence pages",
                "epic_id": epic_id,
                "test_plans": saved_items
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate test plans: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Test plan generation failed: {str(e)}"
            )
