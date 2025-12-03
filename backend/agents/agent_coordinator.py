from typing import Dict, Any, List
from .base_agent import AgentResponse
from .epic_agent import EpicAgent
from .story_agent import StoryAgent
from .qa_agent import QAAgent
from .testplan_agent import TestPlanAgent
from .rag_agent import RAGAgent
from models.file_model import Upload, Epic, Story, QA
from config.db import get_db
import logging

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Orchestrates multiple agents for requirement analysis workflow"""

    def __init__(self):
        self.epic_agent = EpicAgent()
        self.story_agent = StoryAgent()
        self.qa_agent = QAAgent()
        self.testplan_agent = TestPlanAgent()
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

    def generate_testplan(self, epic_id: int) -> AgentResponse:
        """Trigger test plan generation"""
        logger.info(f"Coordinator: Triggering test plan generation for epic {epic_id}")
        return self.testplan_agent.execute({"epic_id": epic_id})

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

    def get_epics(self, upload_id: int) -> AgentResponse:
        """Get all epics for a given upload"""
        logger.info(f"Coordinator: Fetching epics for upload {upload_id}")
        try:
            with get_db() as db:
                upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
                if not upload_obj:
                    return AgentResponse(
                        success=False,
                        error="Upload not found",
                        message="",
                        data={}
                    )
                
                epics = db.query(Epic).filter(Epic.upload_id == upload_id).all()
                epic_list = [
                    {
                        "id": e.id,
                        "name": e.name,
                        "content": e.content,
                        "confluence_page_id": e.confluence_page_id,
                        "created_at": str(e.created_at)
                    }
                    for e in epics
                ]
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved {len(epic_list)} epics",
                    data={"epics": epic_list, "total": len(epic_list)},
                    error=None
                )
        except Exception as e:
            logger.error(f"Error fetching epics: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e),
                message="",
                data={}
            )

    def get_stories(self, epic_id: int) -> AgentResponse:
        """Get all stories for a given epic"""
        logger.info(f"Coordinator: Fetching stories for epic {epic_id}")
        try:
            with get_db() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return AgentResponse(
                        success=False,
                        error="Epic not found",
                        message="",
                        data={}
                    )
                
                stories = db.query(Story).filter(Story.epic_id == epic_id).all()
                story_list = [
                    {
                        "id": s.id,
                        "name": s.name,
                        "epic_id": s.epic_id,
                        "content": s.content,
                        "created_at": str(s.created_at)
                    }
                    for s in stories
                ]
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved {len(story_list)} stories",
                    data={"stories": story_list, "total": len(story_list)},
                    error=None
                )
        except Exception as e:
            logger.error(f"Error fetching stories: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e),
                message="",
                data={}
            )

    def get_qa(self, story_id: int) -> AgentResponse:
        """Get all QA test cases for a given story"""
        logger.info(f"Coordinator: Fetching QA tests for story {story_id}")
        try:
            with get_db() as db:
                story_obj = db.query(Story).filter(Story.id == story_id).first()
                if not story_obj:
                    return AgentResponse(
                        success=False,
                        error="Story not found",
                        message="",
                        data={}
                    )
                
                qa_tests = db.query(QA).filter(QA.story_id == story_id).all()
                qa_list = [
                    {
                        "id": q.id,
                        "story_id": q.story_id,
                        "content": q.content,
                        "created_at": str(q.created_at)
                    }
                    for q in qa_tests
                ]
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved {len(qa_list)} QA tests",
                    data={"qa_tests": qa_list, "total": len(qa_list)},
                    error=None
                )
        except Exception as e:
            logger.error(f"Error fetching QA tests: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e),
                message="",
                data={}
            )

    def get_testplan(self, epic_id: int) -> AgentResponse:
        """Get all test plans for a given epic"""
        logger.info(f"Coordinator: Fetching test plans for epic {epic_id}")
        try:
            with get_db() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return AgentResponse(
                        success=False,
                        error="Epic not found",
                        message="",
                        data={}
                    )
                
                # Get test plans associated with stories in this epic
                stories = db.query(Story).filter(Story.epic_id == epic_id).all()
                
                # For now, return stories as the parent container for test plans
                # In a full implementation, you'd have a TestPlan model
                story_list = [
                    {
                        "id": s.id,
                        "name": s.name,
                        "content": s.content,
                        "created_at": str(s.created_at)
                    }
                    for s in stories
                ]
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved {len(story_list)} stories with test plans",
                    data={"test_plans": story_list, "total": len(story_list)},
                    error=None
                )
        except Exception as e:
            logger.error(f"Error fetching test plans: {str(e)}")
            return AgentResponse(
                success=False,
                error=str(e),
                message="",
                data={}
            )
