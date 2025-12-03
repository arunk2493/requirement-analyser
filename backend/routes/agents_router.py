from fastapi import APIRouter, HTTPException, Depends
from backend.agents.agent_coordinator import AgentCoordinator
from pydantic import BaseModel
from typing import Optional
from config.dependencies import get_current_user_with_db
from models.file_model import User, Upload, Epic, Story
from config.db import SessionLocal

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
def generate_epics_endpoint(
    request: EpicGenerationRequest,
    current_user: User = Depends(get_current_user_with_db)
):
    """Generate epics from uploaded requirements using EpicAgent"""
    # Verify upload belongs to current user
    db = SessionLocal()
    try:
        upload = db.query(Upload).filter(
            Upload.id == request.upload_id,
            Upload.user_id == current_user.id
        ).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
    finally:
        db.close()
    
    response = coordinator.generate_epics(request.upload_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/story/generate")
def generate_stories_endpoint(
    request: StoryGenerationRequest,
    current_user: User = Depends(get_current_user_with_db)
):
    """Generate stories from an epic using StoryAgent"""
    # Verify epic belongs to current user
    db = SessionLocal()
    try:
        epic = db.query(Epic).join(Upload).filter(
            Epic.id == request.epic_id,
            Upload.user_id == current_user.id
        ).first()
        if not epic:
            raise HTTPException(status_code=404, detail="Epic not found")
    finally:
        db.close()
    
    response = coordinator.generate_stories(request.epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/qa/generate")
def generate_qa_endpoint(
    request: QAGenerationRequest,
    current_user: User = Depends(get_current_user_with_db)
):
    """Generate QA test cases from a story using QAAgent"""
    # Verify story belongs to current user
    db = SessionLocal()
    try:
        story = db.query(Story).join(Epic).join(Upload).filter(
            Story.id == request.story_id,
            Upload.user_id == current_user.id
        ).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
    finally:
        db.close()
    
    response = coordinator.generate_qa(request.story_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/testplan/generate")
def generate_testplan_endpoint(
    request: TestPlanGenerationRequest,
    current_user: User = Depends(get_current_user_with_db)
):
    """Generate test plan from an epic using TestPlanAgent"""
    # Verify epic belongs to current user
    db = SessionLocal()
    try:
        epic = db.query(Epic).join(Upload).filter(
            Epic.id == request.epic_id,
            Upload.user_id == current_user.id
        ).first()
        if not epic:
            raise HTTPException(status_code=404, detail="Epic not found")
    finally:
        db.close()
    
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
