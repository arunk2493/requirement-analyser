import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException, Depends
from agents.agent_coordinator import AgentCoordinator
from config.auth import get_current_user, TokenData
from config.db import get_db
from models.file_model import Upload, Epic, Story
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
    # Verify ownership of upload
    try:
        with get_db() as db:
            upload = db.query(Upload).filter(Upload.id == request.upload_id, Upload.user_id == current_user.user_id).first()
            if not upload:
                raise HTTPException(status_code=403, detail={"error": "Unauthorized: You do not have access to this upload"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    
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
    # Verify ownership of upload
    try:
        with get_db() as db:
            upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.user_id).first()
            if not upload:
                raise HTTPException(status_code=403, detail={"error": "Unauthorized: You do not have access to this upload"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    
    response = coordinator.get_epics(upload_id, current_user.user_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/story/list")
def get_stories_endpoint(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all stories for a given epic"""
    # Verify ownership of epic (through upload)
    try:
        with get_db() as db:
            epic = db.query(Epic).filter(Epic.id == epic_id).first()
            if not epic:
                raise HTTPException(status_code=404, detail={"error": "Epic not found"})
            upload = db.query(Upload).filter(Upload.id == epic.upload_id, Upload.user_id == current_user.user_id).first()
            if not upload:
                raise HTTPException(status_code=403, detail={"error": "Unauthorized: You do not have access to this epic"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    
    response = coordinator.get_stories(epic_id, current_user.user_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/qa/list")
def get_qa_endpoint(story_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all QA test cases for a given story"""
    # Verify ownership of story (through epic -> upload)
    try:
        with get_db() as db:
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise HTTPException(status_code=404, detail={"error": "Story not found"})
            epic = db.query(Epic).filter(Epic.id == story.epic_id).first()
            if not epic:
                raise HTTPException(status_code=404, detail={"error": "Epic not found"})
            upload = db.query(Upload).filter(Upload.id == epic.upload_id, Upload.user_id == current_user.user_id).first()
            if not upload:
                raise HTTPException(status_code=403, detail={"error": "Unauthorized: You do not have access to this story"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    
    response = coordinator.get_qa(story_id, current_user.user_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.get("/testplan/list")
def get_testplan_endpoint(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all test plans for a given epic"""
    # Verify ownership of epic (through upload)
    try:
        with get_db() as db:
            epic = db.query(Epic).filter(Epic.id == epic_id).first()
            if not epic:
                raise HTTPException(status_code=404, detail={"error": "Epic not found"})
            upload = db.query(Upload).filter(Upload.id == epic.upload_id, Upload.user_id == current_user.user_id).first()
            if not upload:
                raise HTTPException(status_code=403, detail={"error": "Unauthorized: You do not have access to this epic"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    
    response = coordinator.get_testplan(epic_id, current_user.user_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }
