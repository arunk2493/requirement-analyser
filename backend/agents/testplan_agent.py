from typing import Dict, Any
import json
import re
from config.gemini import generate_json
from config.db import get_db
from config.config import CONFLUENCE_URL
from models.file_model import Epic, QA
from atlassian import Confluence
from .base_agent import BaseAgent, AgentResponse
import datetime

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
    # Ensure page_id is clean
    pid = str(page_id).strip().strip("'\"")
    # Return properly formatted URL without double slashes
    return f"https://contactarungk.atlassian.net/wiki/pages/viewpage.action?pageId={pid}"


def safe_parse_json(output):
    """Ensures the model output is a Python object."""
    if isinstance(output, dict):
        return output
    
    if isinstance(output, list):
        return output[0] if output else {}

    if not isinstance(output, str):
        raise ValueError(f"Unexpected type from model: {type(output)}")

    text = output.strip()
    text = re.sub(r"^```json|```$", "", text, flags=re.IGNORECASE)
    text = text.replace("'", '"')
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else parsed[0] if isinstance(parsed, list) else parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {str(e)}\nRaw output: {text}")


class TestPlanAgent(BaseAgent):
    """Agent responsible for generating test plans from epics"""

    def __init__(self):
        super().__init__("TestPlanAgent")

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate test plan from an epic.
        
        Context expects:
            - epic_id (int): ID of the epic
        """
        try:
            epic_id = context.get("epic_id")
            if not epic_id:
                return self.create_response(
                    success=False,
                    data=None,
                    message="No epic_id provided",
                    error="Missing epic_id in context"
                )

            with get_db() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Epic {epic_id} not found",
                        error="Epic not found"
                    )

                if not epic_obj.confluence_page_id:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Epic {epic_id} does not have a Confluence page",
                        error="No Confluence page for epic"
                    )

                prompt = f"""
Generate a comprehensive test plan for the following epic strictly in JSON format.
The JSON must be an object (NOT an array) with the following structure:
{{
  "title": "Test Plan for [Epic Name]",
  "objective": "Brief description of testing objectives",
  "scope": "What is included/excluded in testing",
  "testingTypes": ["Functional", "Performance", "Security", "Integration"],
  "testScenarios": [
    {{
      "scenario": "Scenario name",
      "testCases": ["Test case 1", "Test case 2"],
      "expectedResult": "Expected outcome"
    }}
  ],
  "preconditions": ["Precondition 1", "Precondition 2"],
  "risks": ["Risk 1", "Risk 2"],
  "mitigationStrategies": ["Strategy 1", "Strategy 2"],
  "timeline": "Estimated testing duration",
  "resources": ["Team member 1", "Tool 1"]
}}

NO comments. NO text outside JSON. NO array wrapping.

Epic:
{epic_obj.content if hasattr(epic_obj, 'content') else epic_obj.name}
"""

                self.log_execution("info", f"Generating test plan for epic {epic_id}")
                raw_output = generate_json(prompt)
                testplan_data = safe_parse_json(raw_output)

                # If it's a list, take the first item
                if isinstance(testplan_data, list):
                    testplan_data = testplan_data[0] if testplan_data else {}

                if not isinstance(testplan_data, dict):
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Expected a test plan object",
                        error="Invalid response format"
                    )

                # Create test plan entry in database
                testplan_obj = QA(
                    type="test_plan",
                    epic_id=epic_id,
                    content=testplan_data
                )
                db.add(testplan_obj)
                db.flush()

                # Create Confluence page for test plan
                confluence_page_id = None
                confluence_page_url = None
                try:
                    page_title = f"Test Plan - {testplan_data.get('title', f'Epic {epic_id}')}"
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    page_title_ts = f"{page_title}_{ts}"

                    # Convert content to Confluence storage format
                    page_content = f"<h2>{testplan_data.get('title', 'Test Plan')}</h2>"
                    page_content += f"<h3>Objective</h3><p>{testplan_data.get('objective', 'N/A')}</p>"
                    page_content += f"<h3>Scope</h3><p>{testplan_data.get('scope', 'N/A')}</p>"
                    
                    if testplan_data.get('testingTypes'):
                        page_content += "<h3>Testing Types</h3><ul>"
                        for testing_type in testplan_data.get('testingTypes', []):
                            page_content += f"<li>{testing_type}</li>"
                        page_content += "</ul>"
                    
                    if testplan_data.get('testScenarios'):
                        page_content += "<h3>Test Scenarios</h3>"
                        for scenario in testplan_data.get('testScenarios', []):
                            page_content += f"<h4>{scenario.get('scenario', 'Scenario')}</h4>"
                            page_content += "<ul>"
                            for test_case in scenario.get('testCases', []):
                                page_content += f"<li>{test_case}</li>"
                            page_content += f"</ul><p><strong>Expected Result:</strong> {scenario.get('expectedResult', 'N/A')}</p>"
                    
                    if testplan_data.get('preconditions'):
                        page_content += "<h3>Preconditions</h3><ul>"
                        for precond in testplan_data.get('preconditions', []):
                            page_content += f"<li>{precond}</li>"
                        page_content += "</ul>"
                    
                    if testplan_data.get('risks'):
                        page_content += "<h3>Risks</h3><ul>"
                        for risk in testplan_data.get('risks', []):
                            page_content += f"<li>{risk}</li>"
                        page_content += "</ul>"

                    confluence_page = confluence.create_page(
                        space=SPACE_KEY,
                        title=page_title_ts,
                        body=page_content,
                        parent_id=epic_obj.confluence_page_id,
                        type='page',
                        representation='storage'
                    )
                    
                    confluence_page_id = confluence_page.get('id')
                    # Build URL using just the page ID to avoid double URLs
                    confluence_page_url = f"https://contactarungk.atlassian.net/wiki/pages/viewpage.action?pageId={confluence_page_id}" if confluence_page_id else None

                    testplan_obj.confluence_page_id = confluence_page_id
                    self.log_execution("info", f"Created Confluence page for test plan: {confluence_page_id}")
                except Exception as e:
                    self.log_execution("error", f"Failed to create Confluence page: {str(e)}")
                    # Continue even if Confluence fails

                db.commit()

                saved_testplan = {
                    "id": testplan_obj.id,
                    "name": testplan_data.get("title", f"Test Plan for Epic {epic_id}"),
                    "content": testplan_data,
                    "confluence_page_id": confluence_page_id,
                    "confluence_page_url": confluence_page_url
                }

                self.log_execution("info", f"Successfully generated test plan for epic {epic_id}")
                return self.create_response(
                    success=True,
                    data={"test_plans": [saved_testplan], "epic_id": epic_id},
                    message=f"Successfully generated test plan for epic {epic_id}"
                )

        except Exception as e:
            self.log_execution("error", f"Exception: {str(e)}")
            return self.create_response(
                success=False,
                data=None,
                message="Error generating test plan",
                error=str(e)
            )
