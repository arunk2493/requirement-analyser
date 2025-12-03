from fastapi import APIRouter, HTTPException, Query, Depends
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.file_model import Story, QA, User, Epic, Upload
from config.db import get_db
from config.dependencies import get_current_user_with_db

router = APIRouter()

@router.get("/qa/{story_id}")
def get_qa(
    story_id: int,
    current_user: User = Depends(get_current_user_with_db)
):
    """Get all QA test cases for a given story"""
    with get_db() as db:
        # Verify story belongs to current user
        story_obj = db.query(Story).join(Epic).join(Upload).filter(
            Story.id == story_id,
            Upload.user_id == current_user.id
        ).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

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
def get_qa_details(
    story_id: int,
    qa_id: int,
    current_user: User = Depends(get_current_user_with_db)
):
    """Get details of a specific QA test case"""
    with get_db() as db:
        # Verify story belongs to current user
        story_obj = db.query(Story).join(Epic).join(Upload).filter(
            Story.id == story_id,
            Upload.user_id == current_user.id
        ).first()
        if not story_obj:
            raise HTTPException(status_code=404, detail="Story not found")

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
    current_user: User = Depends(get_current_user_with_db)
):
    """Get all QA test cases across all stories (paginated). Supports sorting by `id` or `created_at`."""
    with get_db() as db:
        # Get QA only from current user's uploads
        query = db.query(QA).join(Story).join(Epic).join(Upload).filter(
            QA.type == "qa",
            Upload.user_id == current_user.id
        )
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
