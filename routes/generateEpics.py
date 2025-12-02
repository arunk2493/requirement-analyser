from fastapi import APIRouter, HTTPException
from models.file_model import Upload, Epic, QA
from config.gemini import generate_json
from config.db import get_db
from atlassian import Confluence
from config.config import CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD, CONFLUENCE_SPACE_KEY, CONFLUENCE_ROOT_FOLDER_ID
import datetime

router = APIRouter()
print("Confluence URL from config:", CONFLUENCE_URL)
print("Confluence Username from config:", CONFLUENCE_USERNAME)
print("Confluence Password from config:", CONFLUENCE_PASSWORD)
print("Confluence Space Key from config:", CONFLUENCE_SPACE_KEY)
print("Confluence Root Folder ID from config:", CONFLUENCE_ROOT_FOLDER_ID)
print("Initializing Confluence clientssss.............")

# Initialize Confluence client
confluence = Confluence(
    url='https://contactarungk.atlassian.net/wiki',
    username='contactarungk@gmail.com',
    password='ATATT3xFfGF0pJqRBI2r1aUW6qaxgh0eH56zJ4vqnhQoVBor1e3HGqHLDru0qyE54VrCgptsSC41e-oPWrleg7S08xpq3PqcwAioQU-OiIxkA8zR_B4GPa1gjgOJplkaCd2vPfOdubGfxqwZFczfnZTqJB5lIQs8BIW5OziNzS0Zo2LnYdlDFh8=435E9689'
)

SPACE_KEY = "~7120202f433386eb414a158a28270f59730758"
ROOT_FOLDER_ID = "491521"

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


def create_testplan_page(title: str, content: dict, parent_id: str):
    test_plan_title = "Test Plan: " + title
    title_ts = add_timestamp(test_plan_title)
    page_content = f"<h2>{test_plan_title}</h2>"
    for k, v in content.items():
        if isinstance(v, list):
            page_content += f"<h3>{k}</h3><ul>"
            for item in v:
                page_content += f"<li>{item}</li>"
            page_content += "</ul>"
        else:
            page_content += f"<p><strong>{k}:</strong> {v}</p>"

    page = confluence.create_page(
        space=SPACE_KEY,
        title=title_ts,
        body=page_content,
        parent_id=parent_id,
        type='page',
        representation='storage'
    )
    return page, title_ts


@router.post("/generate-epics/{upload_id}")
def generate_epics(upload_id: int):
    with get_db() as db:
        upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload_obj:
            raise HTTPException(status_code=404, detail="Upload not found")

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
        try:
            epics = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        if not isinstance(epics, list):
            raise HTTPException(status_code=400, detail="Expected an array of epic objects")

        # Create upload folder page in Confluence
        try:
            upload_folder_page, upload_title_ts = create_upload_folder_page(upload_obj.filename)
            upload_obj.confluence_page_id = upload_folder_page['id']
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Confluence folder creation error: {str(e)}")

        result = []

        for epic_data in epics:
            epic = Epic(
                upload_id=upload_id,
                content=epic_data,
                name=epic_data.get("name")
            )
            db.add(epic)
            db.flush()  # assign epic.id

            # Create epic page in Confluence
            try:
                epic_page, epic_name_ts = create_epic_page(epic.name, epic_data, upload_folder_page['id'])
                epic.confluence_page_id = epic_page['id']
                epic.name = epic_name_ts
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Confluence epic creation error: {str(e)}")

            db.commit()  # save epic with Confluence page ID

            # Generate test plan under epic
            testplan_prompt = f"""
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
{epic_data}
"""
            try:
                testplans = generate_json(testplan_prompt)
            except ValueError as e:
                raise HTTPException(status_code=500, detail=f"Test plan generation error: {str(e)}")

            if not isinstance(testplans, list):
                raise HTTPException(status_code=400, detail="Expected an array of test plan objects")

            testplan_results = []
            for plan in testplans:
                testplan_db = QA(
                    epic_id=epic.id,
                    type="test_plan",
                    content=plan
                )
                db.add(testplan_db)
                db.flush()

                # Create Confluence page under epic
                try:
                    confluence_page, title_ts = create_testplan_page(plan.get("title", "Test Plan"), plan, epic.confluence_page_id)
                    testplan_db.confluence_page_id = confluence_page['id']
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Confluence test plan creation error: {str(e)}")

                db.commit()
                testplan_results.append({
                    "id": testplan_db.id,
                    "content": plan,
                    "confluence_page_id": testplan_db.confluence_page_id
                })

            result.append({
                "id": epic.id,
                "name": epic.name,
                "confluence_page_id": epic.confluence_page_id,
                "test_plans": testplan_results
            })

        return {
            "message": "Epics and test plans generated with Confluence pages",
            "upload_id": upload_id,
            "upload_folder_page_id": upload_folder_page['id'],
            "epics": result
        }
