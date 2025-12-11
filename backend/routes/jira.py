import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import logging
from jira import JIRA

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db import get_db
from config.auth import get_current_user
from models.file_model import Epic, Story, User

router = APIRouter(prefix="/api/jira", tags=["jira"])
logger = logging.getLogger(__name__)


class JiraCredentials(BaseModel):
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str


class CreateEpicRequest(BaseModel):
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str
    epic_name: str
    epic_description: str
    technical_implementation: Optional[str] = None
    epic_id: Optional[int] = None


class CreateStoriesRequest(BaseModel):
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str
    story_ids: List[int]


class CreateEpicWithConfluenceRequest(BaseModel):
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str
    epic_name: str
    epic_description: str
    epic_id: Optional[int] = None
    confluence_upload_id: Optional[int] = None


class CreateStoryWithConfluenceRequest(BaseModel):
    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_project_key: str
    jira_project_id: Optional[str] = None  # Jira project ID (numeric, e.g., 10001)
    story_issuetype_id: Optional[str] = None  # Story issue type ID (numeric, e.g., 10010)
    story_name: Optional[str] = None
    story_title: Optional[str] = None
    story_description: str
    story_acceptance_criteria: Optional[str] = None
    story_id: Optional[int] = None
    epic_id: Optional[int] = None
    story_epic_id: Optional[int] = None
    epic_jira_key: Optional[str] = None  # Parent epic's Jira key for reference
    epic_jira_issue_id: Optional[str] = None  # Parent epic's Jira issue ID (numeric, for parent field)

    @property
    def final_story_name(self) -> str:
        return self.story_name or self.story_title or "Untitled Story"


class JiraIssueResponse(BaseModel):
    key: str
    url: str
    message: str


@router.post("/test-connection")
async def test_jira_connection(
    credentials: JiraCredentials,
    current_user: User = Depends(get_current_user),
):
    """Test connection to Jira with provided credentials"""
    try:
        jira = JIRA(
            server=credentials.jira_url,
            basic_auth=(credentials.jira_username, credentials.jira_api_token),
        )
        user = jira.current_user()
        logger.info(f"Successfully connected to Jira: {credentials.jira_url}")
        
        # Get display name from user object (handle different response formats)
        display_name = None
        if isinstance(user, dict):
            display_name = user.get('displayName', user.get('name', credentials.jira_username))
        elif hasattr(user, 'displayName'):
            display_name = user.displayName
        elif hasattr(user, 'name'):
            display_name = user.name
        else:
            display_name = str(user)
        
        return {
            "status": "success",
            "message": f"Successfully connected to Jira as {display_name}",
            "user": display_name,
        }
    except Exception as e:
        logger.error(f"Failed to connect to Jira: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to Jira: {str(e)}",
        )


def format_epic_description(description: str, technical_implementation: Optional[str] = None) -> str:
    """Format epic description with description and technical implementation"""
    # Combine description and technical implementation if both exist
    if technical_implementation and isinstance(technical_implementation, str) and technical_implementation.strip():
        return f"""{description}

Technical Implementation:
{technical_implementation}"""
    
    return description


@router.post("/create-epic", response_model=JiraIssueResponse)
async def create_epic_in_jira(
    request: CreateEpicRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an epic directly in Jira using the provided credentials"""
    try:
        try:
            jira = JIRA(
                server=request.jira_url,
                basic_auth=(request.jira_username, request.jira_api_token),
            )
            jira.current_user()
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Jira credentials: {str(e)}",
            )

        issue_dict = {
            "project": request.jira_project_key,
            "summary": request.epic_name,
            "description": format_epic_description(
                request.epic_description,
                request.technical_implementation
            ),
            "issuetype": {"name": "Epic"},
        }
        
        # Log for debugging
        logger.info(f"Epic creation - Name: {request.epic_name}, Description length: {len(request.epic_description)}, TechImpl: {request.technical_implementation is not None}")

        try:
            issue = jira.create_issue(**issue_dict)
            logger.info(f"Created Jira epic: {issue.key}")
            
            jira_url = f"{request.jira_url}/browse/{issue.key}"
            
            if request.epic_id:
                epic = db.query(Epic).filter(Epic.id == request.epic_id).first()
                if epic:
                    epic.jira_key = issue.key
                    epic.jira_issue_id = str(issue.id)
                    epic.jira_url = jira_url
                    epic.jira_creation_success = True
                    if epic.content is None:
                        epic.content = {}
                    epic.content['jira_key'] = issue.key
                    epic.content['jira_issue_id'] = str(issue.id)
                    db.commit()
            
            return JiraIssueResponse(
                key=issue.key,
                url=jira_url,
                message=f"Epic '{request.epic_name}' created successfully in Jira",
            )
        except Exception as e:
            logger.error(f"Failed to create epic in Jira: {str(e)}")
            
            # Mark epic as failed if it exists
            if request.epic_id:
                epic = db.query(Epic).filter(Epic.id == request.epic_id).first()
                if epic:
                    epic.jira_creation_success = False
                    db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create epic in Jira: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating epic: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating epic: {str(e)}",
        )


@router.post("/create-story-jira")
async def create_story_in_jira(
    request: CreateStoryWithConfluenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a story as a subtask/child work item linked to an epic in Jira using issue IDs"""
    try:
        try:
            jira = JIRA(
                server=request.jira_url,
                basic_auth=(request.jira_username, request.jira_api_token),
            )
            jira.current_user()
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Jira credentials: {str(e)}",
            )

        # Build the issue dictionary using IDs (required for child work items)
        issue_dict = {
            "summary": request.final_story_name,
            "description": request.story_description,
        }

        # Add project using key (fallback) or ID
        if request.jira_project_id:
            issue_dict["project"] = {"id": request.jira_project_id}
        else:
            issue_dict["project"] = request.jira_project_key

        # Add issue type using ID (fallback) or name
        if request.story_issuetype_id:
            issue_dict["issuetype"] = {"id": request.story_issuetype_id}
        else:
            issue_dict["issuetype"] = {"name": "Story"}

        # If epic_jira_issue_id is provided, link the story as a child work item using parent ID
        if request.epic_jira_issue_id:
            issue_dict["parent"] = {"id": request.epic_jira_issue_id}

        try:
            issue = jira.create_issue(**issue_dict)
            logger.info(f"Created Jira story: {issue.key}")
            
            jira_url = f"{request.jira_url}/browse/{issue.key}"
            
            # Update the story in the database with Jira information
            if request.story_id:
                story = db.query(Story).filter(Story.id == request.story_id).first()
                if story:
                    story.jira_key = issue.key
                    story.jira_issue_id = str(issue.id)
                    story.jira_url = jira_url
                    story.epic_jira_key = request.epic_jira_key
                    story.epic_jira_issue_id = request.epic_jira_issue_id
                    story.jira_creation_success = True
                    if story.content is None:
                        story.content = {}
                    story.content['jira_key'] = issue.key
                    story.content['jira_issue_id'] = str(issue.id)
                    db.commit()
            
            return JiraIssueResponse(
                key=issue.key,
                url=jira_url,
                message=f"Story '{request.final_story_name}' created as child work item in Jira",
            )
        except Exception as e:
            logger.error(f"Failed to create story in Jira: {str(e)}")
            # Mark creation as failed
            if request.story_id:
                story = db.query(Story).filter(Story.id == request.story_id).first()
                if story:
                    story.jira_creation_success = False
                    db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create story in Jira: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating story: {str(e)}",
        )


@router.post("/create-stories-under-epic")
async def create_stories_under_epic(
    request: CreateStoryWithConfluenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create stories under an epic in Jira using the provided credentials"""
    try:
        try:
            jira = JIRA(
                server=request.jira_url,
                basic_auth=(request.jira_username, request.jira_api_token),
            )
            jira.current_user()
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Jira credentials: {str(e)}",
            )

        # Get the epic's jira key if available
        epic_jira_key = None
        if request.epic_id:
            epic = db.query(Epic).filter(Epic.id == request.epic_id).first()
            if epic and epic.jira_key:
                epic_jira_key = epic.jira_key

        issue_dict = {
            "project": request.jira_project_key,
            "summary": request.final_story_name,
            "description": request.story_description,
            "issuetype": {"name": "Story"},
        }

        # Link story to epic if epic jira key is available
        if epic_jira_key:
            issue_dict["customfield_10015"] = epic_jira_key  # Common Jira field for epic link

        try:
            issue = jira.create_issue(**issue_dict)
            logger.info(f"Created Jira story: {issue.key} under epic {epic_jira_key}")

            jira_url = f"{request.jira_url}/browse/{issue.key}"

            if request.story_id:
                story = db.query(Story).filter(Story.id == request.story_id).first()
                if story:
                    story.jira_key = issue.key
                    story.jira_url = jira_url
                    story.epic_jira_key = epic_jira_key
                    if story.content is None:
                        story.content = {}
                    story.content['jira_key'] = issue.key
                    db.commit()

            return JiraIssueResponse(
                key=issue.key,
                url=jira_url,
                message=f"Story '{request.final_story_name}' created under epic {epic_jira_key}",
            )
        except Exception as e:
            logger.error(f"Failed to create story under epic: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create story: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating story under epic: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating story: {str(e)}",
        )



@router.post("/save-credentials")
async def save_jira_credentials(
    credentials: JiraCredentials,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save Jira credentials to user profile"""
    try:
        # Test connection first
        try:
            jira = JIRA(
                server=credentials.jira_url,
                basic_auth=(credentials.jira_username, credentials.jira_api_token),
            )
            jira.current_user()
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Jira credentials: {str(e)}",
            )

        # Get actual User object from database
        user = db.query(User).filter(User.id == current_user.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Save credentials to user profile
        user.jira_url = credentials.jira_url
        user.jira_username = credentials.jira_username
        user.jira_api_token = credentials.jira_api_token
        user.jira_project_key = credentials.jira_project_key
        db.commit()

        logger.info(f"Saved Jira credentials for user {user.id}")
        return {
            "status": "success",
            "message": "Jira credentials saved successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving Jira credentials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving credentials: {str(e)}",
        )


@router.get("/get-credentials")
async def get_jira_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve saved Jira credentials for the user"""
    try:
        # Get actual User object from database
        user = db.query(User).filter(User.id == current_user.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.jira_url:
            return {
                "status": "not_configured",
                "message": "No Jira credentials configured",
                "credentials": None,
            }

        return {
            "status": "success",
            "message": "Jira credentials retrieved",
            "credentials": {
                "jira_url": user.jira_url,
                "jira_username": user.jira_username,
                "jira_api_token": user.jira_api_token,
                "jira_project_key": user.jira_project_key,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Jira credentials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving credentials: {str(e)}",
        )


@router.delete("/delete-credentials")
async def delete_jira_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete Jira credentials from user profile"""
    try:
        # Get actual User object from database
        user = db.query(User).filter(User.id == current_user.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.jira_url = None
        user.jira_username = None
        user.jira_api_token = None
        user.jira_project_key = None
        db.commit()

        logger.info(f"Deleted Jira credentials for user {current_user.user_id}")
        return {
            "status": "success",
            "message": "Jira credentials deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting Jira credentials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting credentials: {str(e)}",
        )


class MarkEpicFailedRequest(BaseModel):
    epic_id: int


@router.post("/mark-epic-failed")
async def mark_epic_failed(
    request: MarkEpicFailedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an epic as failed in Jira creation (for audit trail)"""
    try:
        epic = db.query(Epic).filter(Epic.id == request.epic_id).first()
        if not epic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Epic not found",
            )
        
        # Mark as failed
        epic.jira_creation_success = False
        db.commit()
        
        logger.info(f"Marked epic {request.epic_id} as failed in Jira creation")
        return {
            "status": "success",
            "message": "Epic marked as failed",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking epic as failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking epic as failed: {str(e)}",
        )
