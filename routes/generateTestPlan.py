from fastapi import APIRouter, HTTPException
from models.file_model import Story, QA, Epic
from config.gemini import generate_json
from config.db import get_db
from atlassian import Confluence
import datetime

router = APIRouter()

# Reuse Confluence client
confluence = Confluence(
    url='https://contactarungk.atlassian.net/wiki',
    username='contactarungk@gmail.com',
    password='ATATT3xFfGF0pJqRBI2r1aUW6qaxgh0eH56zJ4vqnhQoVBor1e3HGqHLDru0qyE54VrCgptsSC41e-oPWrleg7S08xpq3PqcwAioQU-OiIxkA8zR_B4GPa1gjgOJplkaCd2vPfOdubGfxqwZFczfnZTqJB5lIQs8BIW5OziNzS0Zo2LnYdlDFh8=435E9689'
)

SPACE_KEY = "~7120202f433386eb414a158a28270f59730758"


def add_timestamp(name: str):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{ts}"


def create_testplan_page(title: str, content: dict, parent_id: str):
    title_ts = add_timestamp(title)
    page_content = f"<h2>{title}</h2>"
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


@router.post("/generate-testplan/{story_id}")
def generate_testplan(story_id: int):
    with get_db() as db:
        # Fetch story
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

        # Fetch epic details using story.epic_id
        epic_obj = db.query(Epic).filter(Epic.id == story_obj.epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")

        if not epic_obj.confluence_page_id:
            raise HTTPException(status_code=400, detail="Epic does not have a Confluence page")

        # Prompt (unchanged)
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

        # Generate JSON from Gemini
        try:
            testplan_list = generate_json(prompt)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

        if not isinstance(testplan_list, list):
            raise HTTPException(status_code=400, detail="Expected an array of test plan objects")

        saved_items = []

        for plan in testplan_list:
            # Save QA in DB
            testplan_db = QA(
                story_id=story_id,
                type="test_plan",
                content=plan
            )
            db.add(testplan_db)
            db.flush()  # Get generated ID

            # Create Confluence page under the epic's page
            try:
                confluence_page, title_ts = create_testplan_page(
                    plan.get("title", "Test Plan"), plan, epic_obj.confluence_page_id
                )
                testplan_db.confluence_page_id = confluence_page['id']
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Confluence test plan creation error: {str(e)}")

            db.commit()  # Save Confluence page ID in QA table
            saved_items.append({
                "id": testplan_db.id,
                "content": plan,
                "confluence_page_id": testplan_db.confluence_page_id
            })

        return {
            "message": "Test plan generated and pages created in Confluence",
            "story_id": story_id,
            "test_plan": saved_items
        }
