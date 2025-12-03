from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.file_model import Upload, Epic, User
from config.db import get_db
from config.dependencies import get_current_user_with_db
from config.config import CONFLUENCE_URL
from rag.vectorstore import VectorStore
from PyPDF2 import PdfReader
from docx import Document
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_confluence_page_url(page_id: str) -> Optional[str]:
    """Generate Confluence page URL from page ID"""
    if not page_id:
        return None
    try:
        base = (CONFLUENCE_URL or "").strip()
        base = base.strip("'\"")
        base = base.rstrip('/')
    except Exception:
        base = CONFLUENCE_URL

    pid = str(page_id).strip()
    pid = pid.strip("'\"")

    return f"{base}/pages/viewpage.action?pageId={pid}"

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_with_db)
):
    try:
        # Extract text from file
        if file.filename.endswith(".pdf"):
            reader = PdfReader(file.file)
            text = "".join([p.extract_text() + "\n" for p in reader.pages])
        elif file.filename.endswith(".docx"):
            doc = Document(file.file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            contents = await file.read()
            try:
                text = contents.decode("utf-8")
            except UnicodeDecodeError:
                text = contents.decode("latin1")

        # Store as JSON
        content_json = {"requirement": text}

        # Store in DB
        with get_db() as db:
            upload_obj = Upload(
                filename=file.filename,
                content=content_json,
                user_id=current_user.id
            )
            db.add(upload_obj)
            db.commit()      # <-- commit transaction
            db.refresh(upload_obj)  # <-- refresh to get the ID
            
            # Create a vector store for this upload
            vectorstore_id = VectorStore.create_vectorstore_id()
            vectorstore = VectorStore(upload_id=upload_obj.id)
            
            # Store the requirement text in the vector store
            vectorstore.store_document(
                text=text,
                doc_id=f"requirement_{upload_obj.id}",
                metadata={
                    "type": "requirement",
                    "filename": file.filename,
                    "upload_id": upload_obj.id
                }
            )
            
            # Store vectorstore ID in database
            upload_obj.vectorstore_id = vectorstore_id
            db.commit()
            db.refresh(upload_obj)
            
            logger.info(f"Created vector store {vectorstore_id} for upload {upload_obj.id}")

        return {
            "message": "File uploaded successfully",
            "upload_id": upload_obj.id,
            "vectorstore_id": vectorstore_id
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uploads")
def get_all_uploads(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user_with_db)
):
    """Get all uploaded files with pagination. Returns file info with first epic's Confluence link if available."""
    try:
        with get_db() as db:
            # Get total count for current user
            total_count = db.query(Upload).filter(Upload.user_id == current_user.id).count()
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get paginated results for current user
            uploads = db.query(Upload).filter(Upload.user_id == current_user.id).order_by(Upload.created_at.desc()).offset(offset).limit(page_size).all()
            
            upload_list = []
            for upload in uploads:
                # Get the first epic for this upload to get Confluence link
                first_epic = db.query(Epic).filter(Epic.upload_id == upload.id).first()
                
                upload_data = {
                    "id": upload.id,
                    "filename": upload.filename,
                    "created_at": upload.created_at,
                    "confluence_page_url": get_confluence_page_url(first_epic.confluence_page_id) if first_epic else None
                }
                upload_list.append(upload_data)
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            
            return {
                "message": "Uploads retrieved successfully",
                "total_uploads": total_count,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "uploads": upload_list
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
