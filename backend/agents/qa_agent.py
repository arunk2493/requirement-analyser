from typing import Dict, Any
import os
import json
import re
from config.gemini import generate_json
from config.db import get_db, get_db_context
from models.file_model import Story, QA
from .base_agent import BaseAgent, AgentResponse


def safe_parse_json(output):
    """Ensures the model output is a Python list."""
    if isinstance(output, list):
        return output

    if not isinstance(output, str):
        raise ValueError(f"Unexpected type from model: {type(output)}")

    text = output.strip()
    
    # Remove markdown code fence markers if present
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
    
    # Remove any leading text before the first [ or after the last ]
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        text = match.group(0)
    
    # Clean up common formatting issues
    text = text.replace("'", '"')
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    
    if not text.strip():
        raise ValueError("Empty output after cleaning")

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {str(e)}\nRaw output: {text[:500]}")


class QAAgent(BaseAgent):
    """Agent responsible for generating QA test cases from stories"""

    def __init__(self):
        super().__init__("QAAgent")

    def load_qa_prompt(self) -> str:
        """Load QA generation prompt from file with fallback"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prompts",
                "qa_prompt.txt"
            )
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            self.log_execution("warning", f"Failed to load prompt file: {str(e)}, using fallback")
            # Fallback prompt
            return """You are a QA automation engineer. Generate comprehensive test cases for the provided user story, categorizing them by type: Functional, Non-Functional, and API.

## Instructions:
1. Identify all testable scenarios from the story
2. Categorize tests into three types:
   - FUNCTIONAL: Tests that verify core functionality
   - NON_FUNCTIONAL: Tests for performance, security, usability
   - API: Tests for API endpoints and integrations
3. Generate automation scripts in Karate DSL format

## Output Format (STRICTLY VALID JSON ONLY):
Respond ONLY with a valid JSON array. Each test case object MUST have:
- title (string): Test case name
- type (enum): "functional", "non_functional", or "api"
- apiEndpoint (string): API endpoint or "N/A"
- method (string): HTTP method or "N/A"
- request (object): Request payload
- response (object): Expected response
- validationSteps (array): Verification steps
- automationScript (string): Karate DSL script

[
  {
    "title": "Sample test",
    "type": "functional",
    "apiEndpoint": "/api/test",
    "method": "POST",
    "request": {"key": "value"},
    "response": {"status": 200},
    "validationSteps": ["Check status", "Verify response"],
    "automationScript": "Feature: Test\\n  Scenario: Test case\\n    Given url"
  }
]

User Story:
{{requirement}}"""

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

            with get_db_context() as db:
                story_obj = db.query(Story).filter(Story.id == story_id).first()
                if not story_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Story {story_id} not found",
                        error="Story not found"
                    )

                # Load prompt from file
                prompt_template = self.load_qa_prompt()
                
                # Convert story content to string if it's a dict
                story_content = story_obj.content
                if isinstance(story_content, dict):
                    story_content = str(story_content)
                else:
                    story_content = str(story_content) if story_content else ""
                
                # Replace placeholder with story content
                prompt = prompt_template.replace("{{requirement}}", story_content)

                self.log_execution("info", f"Generating QA test cases for story {story_id}")
                raw_output = generate_json(prompt)
                
                try:
                    qa_list = safe_parse_json(raw_output)
                except ValueError as parse_error:
                    self.log_execution("error", f"JSON parsing error: {str(parse_error)}")
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Could not extract valid JSON from model output.",
                        error=f"JSON parsing failed: {str(parse_error)}"
                    )

                if not isinstance(qa_list, list):
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Expected an array of QA objects",
                        error="Invalid response format"
                    )

                saved_tests = []
                for qa_item in qa_list:
                    # Extract test_type from the test case
                    test_type = qa_item.get("type", "functional")
                    # Normalize test_type values
                    if test_type:
                        test_type = test_type.lower().replace(" ", "_")
                    
                    qa_obj = QA(
                        story_id=story_id,
                        type="qa",
                        test_type=test_type,
                        content=qa_item
                    )
                    db.add(qa_obj)
                    db.flush()

                    saved_tests.append({
                        "id": qa_obj.id,
                        "story_id": story_id,
                        "title": qa_item.get("title", f"QA Test {qa_obj.id}"),
                        "test_type": test_type,
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

