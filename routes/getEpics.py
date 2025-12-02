from fastapi import APIRouter, HTTPException, Query
from models.file_model import Upload, Epic
from config.db import get_db
from config.config import CONFLUENCE_URL
from typing import Optional

router = APIRouter()

def get_confluence_page_url(page_id: str) -> Optional[str]:
    """Generate Confluence page URL from page ID"""
    if not page_id:
        return None
    # sanitize base URL and page id to avoid stray quotes or trailing slashes
    try:
        base = (CONFLUENCE_URL or "").strip()
        base = base.strip("'\"")
        base = base.rstrip('/')
    except Exception:
        base = CONFLUENCE_URL

    pid = str(page_id).strip()
    pid = pid.strip("'\"")

    return f"{base}/pages/viewpage.action?pageId={pid}"

@router.get("/epics/{upload_id}")
def get_epics(upload_id: int):
    """Get all epics for a given upload"""
    with get_db() as db:
        upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload_obj:
            raise HTTPException(status_code=404, detail="Upload not found")

        epics = db.query(Epic).filter(Epic.upload_id == upload_id).all()
        
        if not epics:
            raise HTTPException(status_code=404, detail="No epics found for this upload")

        epic_list = []
        for epic in epics:
            epic_data = {
                "id": epic.id,
                "name": epic.name,
                "content": epic.content,
                "confluence_page_id": epic.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(epic.confluence_page_id),
                "created_at": epic.created_at
            }
            epic_list.append(epic_data)

        return {
            "message": "Epics retrieved successfully",
            "upload_id": upload_id,
            "total_epics": len(epic_list),
            "epics": epic_list
        }


@router.get("/epics")
def get_all_epics(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Get all epics across all uploads (paginated)."""
    with get_db() as db:
        total_count = db.query(Epic).count()
        offset = (page - 1) * page_size
        epics = db.query(Epic).order_by(Epic.created_at.desc()).offset(offset).limit(page_size).all()

        epic_list = []
        for epic in epics:
            epic_data = {
                "id": epic.id,
                "name": epic.name,
                "content": epic.content,
                "confluence_page_id": epic.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(epic.confluence_page_id),
                "created_at": epic.created_at
            }
            epic_list.append(epic_data)

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "message": "All epics retrieved successfully",
            "total_epics": total_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "epics": epic_list
        }

@router.get("/epics/{upload_id}/{epic_id}")
def get_epic_details(upload_id: int, epic_id: int):
    """Get details of a specific epic"""
    with get_db() as db:
        upload_obj = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload_obj:
            raise HTTPException(status_code=404, detail="Upload not found")

        epic = db.query(Epic).filter(
            Epic.id == epic_id,
            Epic.upload_id == upload_id
        ).first()
        
        if not epic:
            raise HTTPException(status_code=404, detail="Epic not found")

        return {
            "message": "Epic details retrieved successfully",
            "epic": {
                "id": epic.id,
                "name": epic.name,
                "content": epic.content,
                "confluence_page_id": epic.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(epic.confluence_page_id),
                "created_at": epic.created_at
            }
        }
