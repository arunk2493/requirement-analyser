from typing import Dict, Any, List, Optional
from .base_agent import AgentResponse
from .epic_agent import EpicAgent
from .story_agent import StoryAgent
from .qa_agent import QAAgent
from .testplan_agent import TestPlanAgent
from .rag_agent import RAGAgent
from models.file_model import Upload, Epic, Story, QA
from config.db import get_db, get_db_context
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_serialize_content(content):
    """Safely serialize content field for JSON response"""
    if content is None:
        return None
    if isinstance(content, (dict, str)):
        return content
    try:
        return str(content)
    except Exception:
        return None


def create_coordinator_response(
    success: bool,
    data: Any = None,
    message: str = "",
    error: Optional[str] = None
) -> AgentResponse:
    """Create a standardized AgentResponse from the coordinator"""
    return AgentResponse(
        success=success,
        data=data or {},
        message=message,
        agent_name="AgentCoordinator",
        timestamp=datetime.now().isoformat(),
        error=error
    )


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

    def get_epics(self, upload_id: int, user_id: int = None) -> AgentResponse:
        """Get all epics for a given upload"""
        logger.info(f"Coordinator: Fetching epics for upload {upload_id}, user {user_id}")
        try:
            with get_db_context() as db:
                upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
                if not upload_obj:
                    return create_coordinator_response(
                        success=False,
                        error="Upload not found",
                        message=""
                    )
                
                # Verify user access if user_id provided
                if user_id and upload_obj.user_id != user_id:
                    return create_coordinator_response(
                        success=False,
                        error="Unauthorized: You do not have access to this upload",
                        message=""
                    )
                
                epics = db.query(Epic).filter(Epic.upload_id == upload_id).all()
                epic_list = []
                for e in epics:
                    try:
                        confluence_url = self._get_confluence_url(e.confluence_page_id)
                        epic_data = {
                            "id": e.id,
                            "name": e.name or "Untitled",
                            "content": e.content if isinstance(e.content, (dict, str)) else str(e.content),
                            "confluence_page_id": e.confluence_page_id,
                            "confluence_page_url": confluence_url,
                            "jira_key": e.jira_key,
                            "jira_issue_id": e.jira_issue_id,
                            "jira_url": e.jira_url,
                            "jira_creation_success": e.jira_creation_success,
                            "created_at": str(e.created_at) if e.created_at else None
                        }
                        epic_list.append(epic_data)
                    except Exception as item_error:
                        logger.error(f"Error serializing epic {e.id}: {str(item_error)}")
                        # Skip problematic items
                        continue
                
                return create_coordinator_response(
                    success=True,
                    message=f"Retrieved {len(epic_list)} epics",
                    data={"epics": epic_list, "total": len(epic_list)}
                )
        except Exception as e:
            logger.error(f"Error fetching epics: {str(e)}")
            return create_coordinator_response(
                success=False,
                error=str(e),
                message=""
            )

    def get_stories(self, epic_id: int, user_id: int = None) -> AgentResponse:
        """Get all stories for a given epic"""
        logger.info(f"Coordinator: Fetching stories for epic {epic_id}, user {user_id}")
        try:
            with get_db_context() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return create_coordinator_response(
                        success=False,
                        error="Epic not found",
                        message=""
                    )
                
                # Verify user access if user_id provided
                if user_id:
                    upload = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == user_id).first()
                    if not upload:
                        return create_coordinator_response(
                            success=False,
                            error="Unauthorized: You do not have access to this epic",
                            message=""
                        )
                
                stories = db.query(Story).filter(Story.epic_id == epic_id).all()
                story_list = []
                for s in stories:
                    try:
                        story_data = {
                            "id": s.id,
                            "name": s.name or "Untitled",
                            "content": s.content if isinstance(s.content, (dict, str)) else str(s.content),
                            "jira_key": s.jira_key,
                            "jira_issue_id": s.jira_issue_id,
                            "jira_url": s.jira_url,
                            "epic_jira_key": s.epic_jira_key,
                            "epic_jira_issue_id": s.epic_jira_issue_id,
                            "jira_creation_success": s.jira_creation_success,
                            "created_at": str(s.created_at) if s.created_at else None
                        }
                        story_list.append(story_data)
                    except Exception as item_error:
                        logger.error(f"Error serializing story {s.id}: {str(item_error)}")
                        continue
                
                return create_coordinator_response(
                    success=True,
                    message=f"Retrieved {len(story_list)} stories",
                    data={"stories": story_list, "total": len(story_list)}
                )
        except Exception as e:
            logger.error(f"Error fetching stories: {str(e)}")
            return create_coordinator_response(
                success=False,
                error=str(e),
                message=""
            )

    def get_qa(self, story_id: int, user_id: int = None) -> AgentResponse:
        """Get all QA test cases for a given story"""
        logger.info(f"Coordinator: Fetching QA tests for story {story_id}, user {user_id}")
        try:
            with get_db_context() as db:
                story_obj = db.query(Story).filter(Story.id == story_id).first()
                if not story_obj:
                    return create_coordinator_response(
                        success=False,
                        error="Story not found",
                        message=""
                    )
                
                # Verify user access if user_id provided
                if user_id:
                    epic = db.query(Epic).filter(Epic.id == story_obj.epic_id).first()
                    if not epic:
                        return create_coordinator_response(
                            success=False,
                            error="Epic not found",
                            message=""
                        )
                    upload = db.query(Upload).filter(Upload.id == epic.upload_id, Upload.user_id == user_id).first()
                    if not upload:
                        return create_coordinator_response(
                            success=False,
                            error="Unauthorized: You do not have access to this story",
                            message=""
                        )
                
                qa_tests = db.query(QA).filter(QA.story_id == story_id).all()
                qa_list = []
                for q in qa_tests:
                    try:
                        qa_data = {
                            "id": q.id,
                            "story_id": q.story_id,
                            "test_type": q.test_type,
                            "content": q.content if isinstance(q.content, (dict, str)) else str(q.content),
                            "created_at": str(q.created_at) if q.created_at else None
                        }
                        qa_list.append(qa_data)
                    except Exception as item_error:
                        logger.error(f"Error serializing QA {q.id}: {str(item_error)}")
                        continue
                
                return create_coordinator_response(
                    success=True,
                    message=f"Retrieved {len(qa_list)} QA tests",
                    data={"qa_tests": qa_list, "total": len(qa_list)}
                )
        except Exception as e:
            logger.error(f"Error fetching QA tests: {str(e)}")
            return create_coordinator_response(
                success=False,
                error=str(e),
                message=""
            )

    def get_testplan(self, epic_id: int, user_id: int = None) -> AgentResponse:
        """Get all test plans for a given epic"""
        logger.info(f"Coordinator: Fetching test plans for epic {epic_id}, user {user_id}")
        try:
            with get_db_context() as db:
                epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
                if not epic_obj:
                    return create_coordinator_response(
                        success=False,
                        error="Epic not found",
                        message=""
                    )
                
                # Verify user access if user_id provided
                if user_id:
                    upload = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == user_id).first()
                    if not upload:
                        return create_coordinator_response(
                            success=False,
                            error="Unauthorized: You do not have access to this epic",
                            message=""
                        )
                
                # Get test plans for this epic
                test_plans = db.query(QA).filter(QA.epic_id == epic_id, QA.type == "test_plan").all()
                test_plan_list = self._build_test_plan_list(test_plans)
                
                return create_coordinator_response(
                    success=True,
                    message=f"Retrieved {len(test_plan_list)} test plans",
                    data={"test_plans": test_plan_list, "total": len(test_plan_list)}
                )
        except Exception as e:
            logger.error(f"Error fetching test plans: {str(e)}")
            return create_coordinator_response(
                success=False,
                error=str(e),
                message=""
            )

    def _build_test_plan_list(self, test_plans):
        """Helper method to build test plan list with proper formatting"""
        DEFAULT_NAME = "Test Plan"
        test_plan_list = []
        
        for tp in test_plans:
            try:
                tp_name = self._extract_test_plan_name(tp.content, DEFAULT_NAME)
                confluence_url = self._get_confluence_url(tp.confluence_page_id)
                
                test_plan_data = {
                    "id": tp.id,
                    "name": tp_name,
                    "content": tp.content if isinstance(tp.content, (dict, str)) else str(tp.content),
                    "confluence_page_id": tp.confluence_page_id,
                    "confluence_page_url": confluence_url,
                    "created_at": str(tp.created_at) if tp.created_at else None
                }
                test_plan_list.append(test_plan_data)
            except Exception as item_error:
                logger.error(f"Error serializing test plan {tp.id}: {str(item_error)}")
        
        return test_plan_list

    @staticmethod
    def _extract_test_plan_name(content, default_name: str) -> str:
        """Extract test plan name from content"""
        try:
            if isinstance(content, dict):
                return content.get("title") or content.get("name") or default_name
            elif isinstance(content, str):
                import json
                parsed = json.loads(content)
                return parsed.get("title") or parsed.get("name") or default_name
        except Exception:
            pass
        return default_name

    @staticmethod
    def _get_confluence_url(page_id: str) -> str:
        """Generate Confluence page URL from page ID"""
        if not page_id:
            return ""
        pid = str(page_id).strip().strip("'\"")
        return f"https://contactarungk.atlassian.net/wiki/pages/viewpage.action?pageId={pid}"
