import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends
from agents.agent_coordinator import AgentCoordinator
from config.auth import get_current_user, TokenData
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/agents", tags=["agents"])
coordinator = AgentCoordinator()


class EpicGenerationRequest(BaseModel):
    upload_id: int


class StoryGenerationRequest(BaseModel):
    epic_id: int


class QAGenerationRequest(BaseModel):
    story_id: int


class TestPlanGenerationRequest(BaseModel):
    epic_id: int


class RAGSearchRequest(BaseModel):
    query: str
    upload_id: Optional[int] = None
    top_k: int = 5


class WorkflowExecutionRequest(BaseModel):
    upload_id: int


@router.post("/epic/generate")
def generate_epics_endpoint(request: EpicGenerationRequest, current_user: TokenData = Depends(get_current_user)):
    """Generate epics from uploaded requirements using EpicAgent"""
    response = coordinator.generate_epics(request.upload_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/story/generate")
def generate_stories_endpoint(request: StoryGenerationRequest, current_user: TokenData = Depends(get_current_user)):
    """Generate stories from an epic using StoryAgent"""
    response = coordinator.generate_stories(request.epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/qa/generate")
def generate_qa_endpoint(request: QAGenerationRequest, current_user: TokenData = Depends(get_current_user)):
    """Generate QA test cases from a story using QAAgent"""
    response = coordinator.generate_qa(request.story_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/testplan/generate")
def generate_testplan_endpoint(request: TestPlanGenerationRequest, current_user: TokenData = Depends(get_current_user)):
    """Generate test plan from an epic using TestPlanAgent"""
    response = coordinator.generate_testplan(request.epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/rag/search")
def rag_search_endpoint(request: RAGSearchRequest):
    """Search for relevant documents using RAGAgent"""
    response = coordinator.retrieve_documents(
        query=request.query,
        upload_id=request.upload_id,
        top_k=request.top_k
    )
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/workflow/execute")
def execute_workflow_endpoint(request: WorkflowExecutionRequest):
    """Execute full agentic workflow: epics -> stories -> qa"""
    try:
        result = coordinator.execute_workflow(request.upload_id)
        return {
            "message": "Workflow executed successfully" if result["success"] else "Workflow completed with errors",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET endpoints for retrieving generated artifacts
@router.get("/epic/list")
def get_epics_endpoint(upload_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all epics for a given upload"""
    response = coordinator.get_epics(upload_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/story/list")
def get_stories_endpoint(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all stories for a given epic"""
    response = coordinator.get_stories(epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/qa/list")
def get_qa_endpoint(story_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all QA test cases for a given story"""
    response = coordinator.get_qa(story_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/testplan/list")
def get_testplan_endpoint(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all test plans for a given epic"""
    response = coordinator.get_testplan(epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }
