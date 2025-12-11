from typing import Dict, Any
from config.gemini import generate_json
from config.db import get_db, get_db_context
from models.file_model import Upload, Epic, QA
from config.config import CONFLUENCE_URL
import datetime
from atlassian import Confluence
from .base_agent import BaseAgent, AgentResponse

SPACE_KEY = "~7120202f433386eb414a158a28270f59730758"
ROOT_FOLDER_ID = "491521"

confluence = Confluence(
    url='https://contactarungk.atlassian.net/wiki',
    username='contactarungk@gmail.com',
    password='ATATT3xFfGF0pJqRBI2r1aUW6qaxgh0eH56zJ4vqnhQoVBor1e3HGqHLDru0qyE54VrCgptsSC41e-oPWrleg7S08xpq3PqcwAioQU-OiIxkA8zR_B4GPa1gjgOJplkaCd2vPfOdubGfxqwZFczfnZTqJB5lIQs8BIW5OziNzS0Zo2LnYdlDFh8=435E9689'
)


def get_confluence_page_url(page_id: str) -> str:
    """Generate Confluence page URL from page ID"""
    if not page_id:
        return None
    try:
        base = (CONFLUENCE_URL or "").strip()
        base = base.strip("'\"").rstrip('/')
    except Exception:
        base = CONFLUENCE_URL
    pid = str(page_id).strip().strip("'\"")
    return f"{base}/pages/viewpage.action?pageId={pid}"


def add_timestamp(name: str):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{ts}"


def create_upload_folder_page(upload_name: str):
    title_ts = add_timestamp(upload_name)
    page = confluence.create_page(
        space=SPACE_KEY,
        title=title_ts,
        body=f"<h2>Requirements Upload: {upload_name}</h2>",
        parent_id=ROOT_FOLDER_ID,
        type='page',
        representation='storage'
    )
    return page, title_ts


def create_epic_page(epic_name: str, content: dict, parent_id: str):
    title_ts = add_timestamp(epic_name)
    page_content = f"<h2>{epic_name}</h2><p>{content.get('description', '')}</p><h3>Acceptance Criteria</h3><ul>"
    for ac in content.get("acceptanceCriteria", []):
        page_content += f"<li>{ac}</li>"
    page_content += "</ul>"
    page = confluence.create_page(
        space=SPACE_KEY,
        title=title_ts,
        body=page_content,
        parent_id=parent_id,
        type='page',
        representation='storage'
    )
    return page, title_ts


class EpicAgent(BaseAgent):
    """Agent responsible for generating epics from requirements"""

    def __init__(self):
        super().__init__("EpicAgent")

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate epics from uploaded requirements.
        
        Context expects:
            - upload_id (int): ID of the uploaded file
        """
        try:
            upload_id = context.get("upload_id")
            if not upload_id:
                return self.create_response(
                    success=False,
                    data=None,
                    message="No upload_id provided",
                    error="Missing upload_id in context"
                )

            with get_db_context() as db:
                upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
                if not upload_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Upload {upload_id} not found",
                        error="Upload not found"
                    )

                requirement_text = upload_obj.content

                # Generate epics from Gemini
                prompt = f"""
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
                self.log_execution("info", f"Generating epics for upload {upload_id}")
                epics = generate_json(prompt)

                if not isinstance(epics, list):
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Expected an array of epic objects",
                        error="Invalid response format"
                    )

                # Create upload folder page in Confluence
                try:
                    upload_folder_page, upload_title_ts = create_upload_folder_page(upload_obj.filename)
                    upload_obj.confluence_page_id = upload_folder_page['id']
                    db.commit()
                except Exception as e:
                    self.log_execution("error", f"Confluence error: {str(e)}")
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Failed to create Confluence folder",
                        error=str(e)
                    )

                result = []
                for epic_data in epics:
                    epic = Epic(
                        upload_id=upload_id,
                        content=epic_data,
                        name=epic_data.get("name")
                    )
                    db.add(epic)
                    db.flush()

                    # Create epic page in Confluence
                    try:
                        epic_page, epic_name_ts = create_epic_page(epic.name, epic_data, upload_folder_page['id'])
                        epic.confluence_page_id = epic_page['id']
                        epic.name = epic_name_ts
                    except Exception as e:
                        self.log_execution("error", f"Failed to create epic page: {str(e)}")

                    db.commit()

                    result.append({
                        "id": epic.id,
                        "name": epic.name,
                        "confluence_page_id": epic.confluence_page_id,
                        "confluence_page_url": get_confluence_page_url(epic.confluence_page_id)
                    })

                self.log_execution("info", f"Successfully generated {len(result)} epics")
                return self.create_response(
                    success=True,
                    data={"epics": result, "upload_id": upload_id},
                    message=f"Successfully generated {len(result)} epics"
                )

        except Exception as e:
            self.log_execution("error", f"Exception: {str(e)}")
            return self.create_response(
                success=False,
                data=None,
                message="Error generating epics",
                error=str(e)
            )
