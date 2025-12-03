from fastapi import APIRouter, HTTPException, Query, Depends
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.file_model import Upload, Epic, Story
from config.db import get_db
from config.auth import get_current_user, TokenData

router = APIRouter()

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

@router.get("/stories/{epic_id}")
def get_stories(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all stories for a given epic"""
    with get_db() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")
        upload_obj = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == current_user.user_id).first()
        if not upload_obj:
            raise HTTPException(status_code=403, detail="You don't have access to this epic")

        stories = db.query(Story).filter(Story.epic_id == epic_id).all()
        
        if not stories:
            raise HTTPException(status_code=404, detail="No stories found for this epic")

        story_list = []
        for story in stories:
            try:
                story_data = {
                    "id": story.id,
                    "name": story.name or "Untitled",
                    "content": safe_serialize_content(story.content),
                    "created_at": str(story.created_at) if story.created_at else None
                }
                story_list.append(story_data)
            except Exception:
                # Skip stories that fail to serialize
                continue

        return {
            "message": "Stories retrieved successfully",
            "epic_id": epic_id,
            "total_stories": len(story_list),
            "stories": story_list
        }

@router.get("/stories/{epic_id}/{story_id}")
def get_story_details(epic_id: int, story_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get details of a specific story"""
    with get_db() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")
        upload_obj = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == current_user.user_id).first()
        if not upload_obj:
            raise HTTPException(status_code=403, detail="You don't have access to this epic")

        story = db.query(Story).filter(
            Story.id == story_id,
            Story.epic_id == epic_id
        ).first()
        
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        return {
            "message": "Story details retrieved successfully",
            "story": {
                "id": story.id,
                "name": story.name or "Untitled",
                "content": safe_serialize_content(story.content),
                "created_at": str(story.created_at) if story.created_at else None
            }
        }


@router.get("/stories")
def get_all_stories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: TokenData = Depends(get_current_user),
):
    """Get all stories from user's epics (paginated). Supports sorting by `id` or `created_at`."""
    with get_db() as db:
        # Get user's uploads and epics
        user_uploads = db.query(Upload.id).filter(Upload.user_id == current_user.user_id).all()
        upload_ids = [u[0] for u in user_uploads]
        
        if not upload_ids:
            return {
                "message": "No stories found for this user",
                "total_stories": 0,
                "current_page": page,
                "page_size": page_size,
                "total_pages": 0,
                "stories": []
            }
        
        user_epics = db.query(Epic.id).filter(Epic.upload_id.in_(upload_ids)).all()
        epic_ids = [e[0] for e in user_epics]
        
        if not epic_ids:
            return {
                "message": "No stories found for this user",
                "total_stories": 0,
                "current_page": page,
                "page_size": page_size,
                "total_pages": 0,
                "stories": []
            }
        
        total_count = db.query(Story).filter(Story.epic_id.in_(epic_ids)).count()
        offset = (page - 1) * page_size
        sort_by = (sort_by or "created_at").lower()
        sort_order = (sort_order or "desc").lower()
        if sort_by == "id":
            col = Story.id
        else:
            col = Story.created_at

        if sort_order == "asc":
            order_clause = col.asc()
        else:
            order_clause = col.desc()

        stories = db.query(Story).filter(Story.epic_id.in_(epic_ids)).order_by(order_clause).offset(offset).limit(page_size).all()

        story_list = []
        for story in stories:
            try:
                story_data = {
                    "id": story.id,
                    "name": story.name or "Untitled",
                    "content": safe_serialize_content(story.content),
                    "epic_id": story.epic_id,
                    "created_at": str(story.created_at) if story.created_at else None
                }
                story_list.append(story_data)
            except Exception:
                # Skip stories that fail to serialize
                continue

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "message": "All stories retrieved successfully",
            "total_stories": total_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "stories": story_list
        }
