from fastapi import APIRouter, HTTPException, Query, Depends
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.file_model import Upload, Epic, Story, QA
from config.db import get_db, get_db_context
from config.auth import get_current_user, TokenData

router = APIRouter()

@router.get("/qa/{story_id}")
def get_qa(story_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get all QA test cases for a given story"""
    with get_db_context() as db:
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")
        epic_obj = db.query(Epic).filter(Epic.id == story_obj.epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")
        upload_obj = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == current_user.user_id).first()
        if not upload_obj:
            raise HTTPException(status_code=403, detail="You don't have access to this story")

        qa_tests = db.query(QA).filter(
            QA.story_id == story_id,
            QA.type == "qa"
        ).all()
        
        if not qa_tests:
            raise HTTPException(status_code=404, detail="No QA test cases found for this story")

        qa_list = []
        for qa in qa_tests:
            qa_data = {
                "id": qa.id,
                "content": qa.content,
                "created_at": qa.created_at
            }
            qa_list.append(qa_data)

        return {
            "message": "QA test cases retrieved successfully",
            "story_id": story_id,
            "total_qa_tests": len(qa_list),
            "qa_tests": qa_list
        }

@router.get("/qa/{story_id}/{qa_id}")
def get_qa_details(story_id: int, qa_id: int, current_user: TokenData = Depends(get_current_user)):
    """Get details of a specific QA test case"""
    with get_db_context() as db:
        story_obj = db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")
        epic_obj = db.query(Epic).filter(Epic.id == story_obj.epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")
        upload_obj = db.query(Upload).filter(Upload.id == epic_obj.upload_id, Upload.user_id == current_user.user_id).first()
        if not upload_obj:
            raise HTTPException(status_code=403, detail="You don't have access to this story")

        qa = db.query(QA).filter(
            QA.id == qa_id,
            QA.story_id == story_id,
            QA.type == "qa"
        ).first()
        
        if not qa:
            raise HTTPException(status_code=404, detail="QA test case not found")

        return {
            "message": "QA test case details retrieved successfully",
            "qa": {
                "id": qa.id,
                "content": qa.content,
                "created_at": qa.created_at
            }
        }


@router.get("/qa")
def get_all_qa(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: TokenData = Depends(get_current_user),
):
    """Get all QA test cases from user's stories (paginated). Supports sorting by `id` or `created_at`."""
    with get_db_context() as db:
        # Get user's uploads, epics, and stories
        user_uploads = db.query(Upload.id).filter(Upload.user_id == current_user.user_id).all()
        upload_ids = [u[0] for u in user_uploads]
        
        if not upload_ids:
            return {
                "message": "No QA tests found for this user",
                "total_qa_tests": 0,
                "current_page": page,
                "page_size": page_size,
                "total_pages": 0,
                "qa_tests": []
            }
        
        user_epics = db.query(Epic.id).filter(Epic.upload_id.in_(upload_ids)).all()
        epic_ids = [e[0] for e in user_epics]
        
        if not epic_ids:
            return {
                "message": "No QA tests found for this user",
                "total_qa_tests": 0,
                "current_page": page,
                "page_size": page_size,
                "total_pages": 0,
                "qa_tests": []
            }
        
        user_stories = db.query(Story.id).filter(Story.epic_id.in_(epic_ids)).all()
        story_ids = [s[0] for s in user_stories]
        
        if not story_ids:
            return {
                "message": "No QA tests found for this user",
                "total_qa_tests": 0,
                "current_page": page,
                "page_size": page_size,
                "total_pages": 0,
                "qa_tests": []
            }
        
        query = db.query(QA).filter(QA.type == "qa", QA.story_id.in_(story_ids))
        total_count = query.count()
        offset = (page - 1) * page_size
        sort_by = (sort_by or "created_at").lower()
        sort_order = (sort_order or "desc").lower()
        if sort_by == "id":
            col = QA.id
        else:
            col = QA.created_at

        if sort_order == "asc":
            order_clause = col.asc()
        else:
            order_clause = col.desc()

        qa_tests = query.order_by(order_clause).offset(offset).limit(page_size).all()

        qa_list = []
        for qa in qa_tests:
            qa_data = {
                "id": qa.id,
                "content": qa.content,
                "story_id": qa.story_id,
                "created_at": qa.created_at
            }
            qa_list.append(qa_data)

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "message": "All QA test cases retrieved successfully",
            "total_qa_tests": total_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "qa_tests": qa_list
        }
