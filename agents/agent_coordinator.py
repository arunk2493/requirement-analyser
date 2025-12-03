from typing import Dict, Any, List
from .base_agent import AgentResponse
from .epic_agent import EpicAgent
from .story_agent import StoryAgent
from .qa_agent import QAAgent
from .rag_agent import RAGAgent
import logging

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Orchestrates multiple agents for requirement analysis workflow"""

    def __init__(self):
        self.epic_agent = EpicAgent()
        self.story_agent = StoryAgent()
        self.qa_agent = QAAgent()
        self.rag_agent = RAGAgent()

    def generate_epics(self, upload_id: int) -> AgentResponse:
        """Trigger epic generation"""
        logger.info(f"Coordinator: Triggering epic generation for upload {upload_id}")
        return self.epic_agent.execute({"upload_id": upload_id})

    def generate_stories(self, epic_id: int) -> AgentResponse:
        """Trigger story generation"""
        logger.info(f"Coordinator: Triggering story generation for epic {epic_id}")
        return self.story_agent.execute({"epic_id": epic_id})

    def generate_qa(self, story_id: int) -> AgentResponse:
        """Trigger QA generation"""
        logger.info(f"Coordinator: Triggering QA generation for story {story_id}")
        return self.qa_agent.execute({"story_id": story_id})

    def retrieve_documents(self, query: str, upload_id: int = None, top_k: int = 5) -> AgentResponse:
        """Retrieve relevant documents from RAG"""
        logger.info(f"Coordinator: Retrieving documents for query: {query}")
        context = {"query": query, "top_k": top_k}
        if upload_id:
            context["upload_id"] = upload_id
        return self.rag_agent.execute(context)

    def execute_workflow(self, upload_id: int) -> Dict[str, Any]:
        """Execute full workflow: epics -> stories -> qa
        
        Returns a comprehensive result dict with all generated artifacts
        """
        logger.info(f"Coordinator: Starting full workflow for upload {upload_id}")
        
        workflow_result = {
            "success": True,
            "epics": [],
            "stories": [],
            "qa": [],
            "errors": []
        }

        # Step 1: Generate Epics
        epic_response = self.generate_epics(upload_id)
        if not epic_response.success:
            workflow_result["success"] = False
            workflow_result["errors"].append(f"Epic generation failed: {epic_response.error}")
            return workflow_result

        workflow_result["epics"] = epic_response.data.get("epics", [])
        epic_ids = [e.get("id") for e in workflow_result["epics"]]

        # Step 2: Generate Stories for each epic
        for epic_id in epic_ids:
            story_response = self.generate_stories(epic_id)
            if story_response.success:
                workflow_result["stories"].extend(story_response.data.get("stories", []))
            else:
                workflow_result["errors"].append(f"Story generation failed for epic {epic_id}")

        # Step 3: Generate QA for each story (sample first 5)
        story_ids = [s.get("id") for s in workflow_result["stories"]][:5]
        for story_id in story_ids:
            qa_response = self.generate_qa(story_id)
            if qa_response.success:
                workflow_result["qa"].extend(qa_response.data.get("qa_tests", []))
            else:
                workflow_result["errors"].append(f"QA generation failed for story {story_id}")

        logger.info(f"Coordinator: Workflow completed. Generated {len(workflow_result['epics'])} epics, "
                   f"{len(workflow_result['stories'])} stories, {len(workflow_result['qa'])} QA tests")
        return workflow_result
