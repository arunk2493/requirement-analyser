from fastapi import APIRouter, HTTPException, Query
from models.file_model import Epic, QA
from config.db import get_db
from config.config import CONFLUENCE_URL
from typing import Optional

router = APIRouter()

def get_confluence_page_url(page_id: str) -> Optional[str]:
    """Generate Confluence page URL from page ID"""
    if not page_id:
        return None
    # sanitize base URL and page id in case of stray quotes or trailing slashes
    try:
        base = (CONFLUENCE_URL or "").strip()
        # remove any surrounding single/double quotes and trailing slashes
        base = base.strip("'\"")
        base = base.rstrip('/')
    except Exception:
        base = CONFLUENCE_URL

    pid = str(page_id).strip()
    pid = pid.strip("'\"")

    return f"{base}/pages/viewpage.action?pageId={pid}"

@router.get("/testplans/{epic_id}")
def get_testplans(epic_id: int):
    """Get all test plans for a given epic"""
    with get_db() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")

        testplans = db.query(QA).filter(
            QA.epic_id == epic_id,
            QA.type == "test_plan"
        ).all()
        
        if not testplans:
            raise HTTPException(status_code=404, detail="No test plans found for this epic")

        testplan_list = []
        for testplan in testplans:
            testplan_data = {
                "id": testplan.id,
                "content": testplan.content,
                "confluence_page_id": testplan.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(testplan.confluence_page_id),
                "created_at": testplan.created_at
            }
            testplan_list.append(testplan_data)

        return {
            "message": "Test plans retrieved successfully",
            "epic_id": epic_id,
            "total_test_plans": len(testplan_list),
            "test_plans": testplan_list
        }

@router.get("/testplans/{epic_id}/{testplan_id}")
def get_testplan_details(epic_id: int, testplan_id: int):
    """Get details of a specific test plan"""
    with get_db() as db:
        epic_obj = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise HTTPException(status_code=404, detail="Epic not found")

        testplan = db.query(QA).filter(
            QA.id == testplan_id,
            QA.epic_id == epic_id,
            QA.type == "test_plan"
        ).first()
        
        if not testplan:
            raise HTTPException(status_code=404, detail="Test plan not found")

        return {
            "message": "Test plan details retrieved successfully",
            "test_plan": {
                "id": testplan.id,
                "content": testplan.content,
                "confluence_page_id": testplan.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(testplan.confluence_page_id),
                "created_at": testplan.created_at
            }
        }


@router.get("/testplans")
def get_all_testplans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    """Get all test plans across all epics (paginated). Supports sorting by `id` or `created_at`."""
    with get_db() as db:
        base_query = db.query(QA).filter(QA.type == "test_plan")
        total_count = base_query.count()
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

        testplans = base_query.order_by(order_clause).offset(offset).limit(page_size).all()

        testplan_list = []
        for testplan in testplans:
            # extract title from stored JSON content if present
            title = None
            try:
                if isinstance(testplan.content, dict):
                    title = testplan.content.get("title") or testplan.content.get("name")
                else:
                    # content might be stored as stringified JSON
                    import json
                    try:
                        parsed = json.loads(testplan.content)
                        if isinstance(parsed, dict):
                            title = parsed.get("title") or parsed.get("name")
                    except Exception:
                        title = None
            except Exception:
                title = None

            testplan_data = {
                "id": testplan.id,
                "title": title or ("Test Plan " + str(testplan.id)),
                "epic_id": testplan.epic_id,
                "confluence_page_id": testplan.confluence_page_id,
                "confluence_page_url": get_confluence_page_url(testplan.confluence_page_id),
                "created_at": testplan.created_at,
                "content": testplan.content
            }
            testplan_list.append(testplan_data)

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "message": "All test plans retrieved successfully",
            "total_test_plans": total_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "test_plans": testplan_list
        }
