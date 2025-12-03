from fastapi import APIRouter, HTTPException
from agents.agent_coordinator import AgentCoordinator
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


class RAGSearchRequest(BaseModel):
    query: str
    upload_id: Optional[int] = None
    top_k: int = 5


class WorkflowExecutionRequest(BaseModel):
    upload_id: int


@router.post("/epic/generate")
def generate_epics_endpoint(request: EpicGenerationRequest):
    """Generate epics from uploaded requirements using EpicAgent"""
    response = coordinator.generate_epics(request.upload_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/story/generate")
def generate_stories_endpoint(request: StoryGenerationRequest):
    """Generate stories from an epic using StoryAgent"""
    response = coordinator.generate_stories(request.epic_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {
        "message": response.message,
        "data": response.data
    }


@router.post("/qa/generate")
def generate_qa_endpoint(request: QAGenerationRequest):
    """Generate QA test cases from a story using QAAgent"""
    response = coordinator.generate_qa(request.story_id)
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
