from typing import Dict, Any
from config.gemini import generate_json
from config.db import get_db
from models.file_model import Epic, Story
from .base_agent import BaseAgent, AgentResponse


class StoryAgent(BaseAgent):
    """Agent responsible for generating stories from epics"""

    def __init__(self):
        super().__init__("StoryAgent")

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

            with get_db() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return self.create_response(
                        success=False,
                        data=None,
                        message=f"Epic {epic_id} not found",
                        error="Epic not found"
                    )

                prompt = f"""
Break down the following epic into multiple user stories strictly in JSON format.
Each story should have:
- name
- type
- description
- acceptanceCriteria
- implementationDetails (if technical)
No extra text, only JSON.

Epic content:
{epic_obj.content}
"""

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
