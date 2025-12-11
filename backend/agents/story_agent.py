from typing import Dict, Any
import os
from pathlib import Path
from config.gemini import generate_json
from config.db import get_db, get_db_context
from models.file_model import Epic, Story
from .base_agent import BaseAgent, AgentResponse


class StoryAgent(BaseAgent):
    """Agent responsible for generating stories from epics"""

    def __init__(self):
        super().__init__("StoryAgent")

    def load_story_prompt(self) -> str:
        """Load story generation prompt from file with fallback"""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prompts",
                "stories_prompt.txt"
            )
            with open(prompt_path, "r") as f:
                content = f.read()
                # Extract content between """ markers if present
                if '"""' in content:
                    parts = content.split('"""')
                    if len(parts) >= 2:
                        return parts[1].strip()
                return content.strip()
        except Exception as e:
            self.log_execution("warning", f"Failed to load prompt file: {str(e)}, using fallback")
            # Fallback prompt
            return """You are an experienced agile product manager. Break down the provided epic into user stories and technical stories.

## Instructions:
1. Understand the epic's purpose and scope
2. Identify user-facing features first (user stories)
3. Identify necessary technical/infrastructure work (technical stories)
4. Each story should have clear acceptance criteria
5. Stories should be independent and completable in 2-5 days

## Output Format (STRICTLY VALID JSON ONLY):
Respond ONLY with a valid JSON array. NO explanations, NO text outside JSON.

Each story object MUST have:
- name (string): Story title
- type (string): Either "user_story" or "technical_story"
- description (string): Story description
- acceptanceCriteria (array of strings): 3-4 testable criteria

Epic Details:
{{requirement}}"""

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate stories from an epic.
        
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

            with get_db_context() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Epic {epic_id} not found",
                        error="Epic not found"
                    )

                # Load prompt from file
                prompt_template = self.load_story_prompt()
                
                # Convert epic content to string if it's a dict
                epic_content = epic_obj.content
                if isinstance(epic_content, dict):
                    epic_content = str(epic_content)
                else:
                    epic_content = str(epic_content) if epic_content else ""
                
                # Replace placeholder with epic content
                prompt = prompt_template.replace("{{requirement}}", epic_content)

                self.log_execution("info", f"Generating stories for epic {epic_id}")
                stories_raw = generate_json(prompt)

                # Normalize response to a list of story objects
                if isinstance(stories_raw, dict):
                    stories_list = [
                        {"name": k, **v} if isinstance(v, dict) else {"name": k, "content": v}
                        for k, v in stories_raw.items()
                    ]
                elif isinstance(stories_raw, list):
                    stories_list = stories_raw
                else:
                    return self.create_response(
                        success=False,
                        data=None,
                        message="Unexpected response format from Gemini",
                        error="Invalid response format"
                    )

                response_array = []
                for story_item in stories_list:
                    story = Story(
                        epic_id=epic_obj.id,
                        name=story_item.get("name", "Unnamed Story"),
                        content=story_item
                    )
                    db.add(story)
                    db.flush()
                    response_array.append({
                        "id": story.id,
                        "name": story.name,
                        "content": story_item
                    })

                db.commit()

                self.log_execution("info", f"Successfully generated {len(response_array)} stories")
                return self.create_response(
                    success=True,
                    data={"stories": response_array, "epic_id": epic_id},
                    message=f"Successfully generated {len(response_array)} stories"
                )

        except Exception as e:
            self.log_execution("error", f"Exception: {str(e)}")
            return self.create_response(
                success=False,
                data=None,
                message="Error generating stories",
                error=str(e)
            )
