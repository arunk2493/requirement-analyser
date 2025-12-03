from typing import Dict, Any
import json
import re
from config.gemini import generate_json
from config.db import get_db
from models.file_model import Story, QA
from .base_agent import BaseAgent, AgentResponse


def safe_parse_json(output):
    """Ensures the model output is a Python list."""
    if isinstance(output, list):
        return output

    if not isinstance(output, str):
        raise ValueError(f"Unexpected type from model: {type(output)}")

    text = output.strip()
    text = re.sub(r"^```json|```$", "", text, flags=re.IGNORECASE)
    text = text.replace("'", '"')
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {str(e)}\nRaw output: {text}")


class QAAgent(BaseAgent):
    """Agent responsible for generating QA test cases from stories"""

    def __init__(self):
        super().__init__("QAAgent")

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate QA test cases from a story.
        
        Context expects:
            - story_id (int): ID of the story
        """
        try:
            story_id = context.get("story_id")
            if not story_id:
                return self.create_response(
                    success=False,
                    data=None,
                    message="No story_id provided",
                    error="Missing story_id in context"
                )

            with get_db() as db:
                story_obj = db.query(Story).filter(Story.id == story_id).first()
                if not story_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Story {story_id} not found",
                        error="Story not found"
                    )

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

                self.log_execution("info", f"Generating QA test cases for story {story_id}")
                raw_output = generate_json(prompt)
                qa_list = safe_parse_json(raw_output)

                if not isinstance(qa_list, list):
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Expected an array of QA objects",
                        error="Invalid response format"
                    )

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
                        "title": qa_item.get("title", f"QA Test {qa_obj.id}"),
                        "content": qa_item
                    })

                db.commit()

                self.log_execution("info", f"Successfully generated {len(saved_tests)} QA test cases")
                return self.create_response(
                    success=True,
                    data={"qa_tests": saved_tests, "story_id": story_id},
                    message=f"Successfully generated {len(saved_tests)} QA test cases"
                )

        except Exception as e:
            self.log_execution("error", f"Exception: {str(e)}")
            return self.create_response(
                success=False,
                data=None,
                message="Error generating QA test cases",
                error=str(e)
            )
