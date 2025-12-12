import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends, status
from models.file_model import Upload
from config.db import get_db_context
from config.auth import get_current_user, TokenData
from atlassian import Confluence
from config.config import CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD, CONFLUENCE_SPACE_KEY, CONFLUENCE_ROOT_FOLDER_ID
from services.content_generator import ContentGenerationService
from utils.confluence_helper import add_timestamp, create_confluence_html_content, build_confluence_page
from utils.error_handler import handle_errors, ProcessingError
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
ROOT_FOLDER_ID = CONFLUENCE_ROOT_FOLDER_ID



EPIC_GENERATION_PROMPT = """
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


@router.post("/generate-epics/{upload_id}")
def generate_epics(upload_id: int, current_user: TokenData = Depends(get_current_user)):
    """
    Generate epics from an uploaded requirement document.
    
    Args:
        upload_id: ID of the upload document
        current_user: Authenticated user
        
    Returns:
        Generated epics with Confluence pages
    """
    logger.info(f"generate_epics: user={current_user.email}, upload_id={upload_id}")
    
    with get_db_context() as db:
        service = ContentGenerationService(db)
        
        try:
            # Generate epics
            epics_data = service.generate_epics(upload_id, EPIC_GENERATION_PROMPT)
            
            # Create upload folder page in Confluence
            upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
            upload_title_ts = add_timestamp(upload_obj.filename)
            
            upload_page = build_confluence_page(
                confluence,
                SPACE_KEY,
                upload_title_ts,
                f"<h2>Requirements Upload: {upload_obj.filename}</h2>",
                ROOT_FOLDER_ID
            )
            upload_obj.confluence_page_id = upload_page['id']
            db.commit()
            
            # Save epics and create Confluence pages
            saved_epics = service.save_epics(upload_id, epics_data)
            
            result = []
            for epic_id, epic_data in saved_epics:
                epic_obj = db.query(db.query(db.model_map['Epic']).get_or_404)
                
                # Create epic Confluence page
                section_configs = {"acceptanceCriteria": {"is_list": True, "heading_level": 3}}
                epic_content = create_confluence_html_content(
                    epic_data.get("name", "Epic"),
                    epic_data,
                    section_configs
                )
                epic_page = build_confluence_page(
                    confluence,
                    SPACE_KEY,
                    add_timestamp(epic_data.get("name", "Epic")),
                    epic_content,
                    upload_page['id']
                )
                
                # Update epic with confluence page ID
                from models.file_model import Epic
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                epic_obj.confluence_page_id = epic_page['id']
                db.commit()
                
                # Generate and save test plans
                testplan_data = service.generate_test_plan(epic_id, TESTPLAN_GENERATION_PROMPT)
                saved_testplans = service.save_qa(epic_id, testplan_data, qa_type="test_plan")
                
                testplan_results = []
                for testplan_id, testplan_item in saved_testplans:
                    testplan_content = create_confluence_html_content(
                        f"Test Plan: {testplan_item.get('title', 'Test Plan')}",
                        testplan_item,
                        {"testScenarios": {"is_list": True, "heading_level": 3}}
                    )
                    testplan_page = build_confluence_page(
                        confluence,
                        SPACE_KEY,
                        add_timestamp(testplan_item.get("title", "Test Plan")),
                        testplan_content,
                        epic_page['id']
                    )
                    
                    from models.file_model import QA
                    testplan_obj = db.query(QA).filter(QA.id == testplan_id).first()
                    testplan_obj.confluence_page_id = testplan_page['id']
                    db.commit()
                    
                    testplan_results.append({
                        "id": testplan_id,
                        "title": testplan_item.get("title", "Test Plan"),
                        "confluence_page_id": testplan_page['id']
                    })
                
                result.append({
                    "id": epic_id,
                    "name": epic_data.get("name", "Epic"),
                    "confluence_page_id": epic_page['id'],
                    "test_plans": testplan_results
                })
            
            return {
                "message": "Epics and test plans generated with Confluence pages",
                "upload_id": upload_id,
                "upload_folder_page_id": upload_page['id'],
                "epics": result
            }
            
        except Exception as e:
            logger.error(f"Failed to generate epics: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Epic generation failed: {str(e)}"
            )
