from fastapi import APIRouter, HTTPException, Query, Depends
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.file_model import Epic, Story
from config.db import get_db
from config.auth import get_current_user, TokenData

router = APIRouter()

@router.get("/stories/{epic_id}")
def get_stories(epic_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all stories for a given epic"""
    with get_db() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")

        stories = db.query(Story).filter(Story.epic_id == epic_id).all()
        
        if not stories:
            raise HTTPException(status_code=404, detail="No stories found for this epic")

        story_list = []
        for story in stories:
            story_data = {
                "id": story.id,
                "name": story.name,
                "content": story.content,
                "created_at": story.created_at
            }
            story_list.append(story_data)

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
                "name": story.name,
                "content": story.content,
                "created_at": story.created_at
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
    """Get all stories across all epics (paginated). Supports sorting by `id` or `created_at`."""
    with get_db() as db:
        total_count = db.query(Story).count()
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

        stories = db.query(Story).order_by(order_clause).offset(offset).limit(page_size).all()

        story_list = []
        for story in stories:
            story_data = {
                "id": story.id,
                "name": story.name,
                "content": story.content,
                "epic_id": story.epic_id,
                "created_at": story.created_at
            }
            story_list.append(story_data)

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "message": "All stories retrieved successfully",
            "total_stories": total_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "stories": story_list
        }
