import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import APIRouter, Depends
from config.db import get_db
from config.auth import get_current_user, TokenData
from models.file_model import Upload, Epic, Story, QA, AggregatedUpload

router = APIRouter()

@router.get("/list-files")
def list_files(current_user: TokenData = Depends(get_current_user)):
    with get_db() as db:
        uploads = db.query(Upload).filter(Upload.user_id == current_user.user_id).all()
        result = []

        for up in uploads:
            upload_entry = {
                "upload_id": up.id,
                "name": up.name,
                "epics": []
            }

            epics = db.query(Epic).filter(Epic.upload_id == up.id).all()
            for e in epics:
                epic_entry = {
                    "epic_id": e.id,
                    "name": e.name,
                    "stories": []
                }

                stories = db.query(Story).filter(Story.epic_id == e.id).all()
                for s in stories:
                    story_entry = {
                        "story_id": s.id,
                        "name": s.name,
                        "content": s.content,
                        "qa": []
                    }

                    qa_entries = db.query(QA).filter(QA.story_id == s.id).all()
                    for q in qa_entries:
                        story_entry["qa"].append({
                            "qa_id": q.id,
                            "type": q.type,
                            "content": q.content
                        })

                    epic_entry["stories"].append(story_entry)

                upload_entry["epics"].append(epic_entry)

            # Optionally include aggregated JSON if exists
            agg = db.query(AggregatedUpload).filter(AggregatedUpload.upload_id == up.id).first()
            if agg:
                upload_entry["aggregated"] = agg.content

            result.append(upload_entry)

    return {"uploads": result}
