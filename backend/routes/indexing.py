from fastapi import APIRouter, HTTPException
from models.file_model import Upload, Epic, Story, QA
from config.db import get_db
from rag.vectorstore import VectorStore
import uuid
import json

router = APIRouter()
vectorstore = VectorStore()


@router.post("/reindex")
def reindex_all():
    """Reindex all content from database into vectorstore"""
    indexed_count = 0
    
    with get_db() as db:
        # Index all epics
        epics = db.query(Epic).all()
        for epic in epics:
            try:
                epic_text = f"Epic: {epic.name}\nDescription: {epic.content.get('description', '')}\nAcceptance Criteria: {', '.join(epic.content.get('acceptanceCriteria', []))}"
                doc_id = f"epic_{epic.id}_{str(uuid.uuid4())[:8]}"
                vectorstore.store_document(epic_text, doc_id, metadata={
                    "type": "epic",
                    "epic_id": epic.id,
                    "upload_id": epic.upload_id,
                    "epic_name": epic.name
                })
                indexed_count += 1
            except Exception as e:
                print(f"Error indexing epic {epic.id}: {e}")
        
        # Index all stories
        stories = db.query(Story).all()
        for story in stories:
            try:
                story_text = f"Story: {story.name}\nType: {story.content.get('type', '')}\nDescription: {story.content.get('description', '')}\nAcceptance Criteria: {', '.join(story.content.get('acceptanceCriteria', []))}"
                doc_id = f"story_{story.id}_{str(uuid.uuid4())[:8]}"
                vectorstore.store_document(story_text, doc_id, metadata={
                    "type": "story",
                    "story_id": story.id,
                    "epic_id": story.epic_id,
                    "story_name": story.name
                })
                indexed_count += 1
            except Exception as e:
                print(f"Error indexing story {story.id}: {e}")
        
        # Index all QA tests
        qa_tests = db.query(QA).all()
        for qa in qa_tests:
            try:
                qa_text = f"QA Test: {qa.content.get('title', '')}\nAPI Endpoint: {qa.content.get('apiEndpoint', '')}\nMethod: {qa.content.get('method', '')}\nValidation Steps: {', '.join(qa.content.get('validationSteps', []))}"
                doc_id = f"qa_{qa.id}_{str(uuid.uuid4())[:8]}"
                vectorstore.store_document(qa_text, doc_id, metadata={
                    "type": "qa",
                    "qa_id": qa.id,
                    "story_id": qa.story_id
                })
                indexed_count += 1
            except Exception as e:
                print(f"Error indexing QA {qa.id}: {e}")
        
        # Index all uploads
        uploads = db.query(Upload).all()
        for upload in uploads:
            try:
                upload_text = f"Upload: {upload.filename}\nContent: {json.dumps(upload.content) if isinstance(upload.content, dict) else str(upload.content)}"
                doc_id = f"upload_{upload.id}_{str(uuid.uuid4())[:8]}"
                vectorstore.store_document(upload_text, doc_id, metadata={
                    "type": "upload",
                    "upload_id": upload.id,
                    "filename": upload.filename
                })
                indexed_count += 1
            except Exception as e:
                print(f"Error indexing upload {upload.id}: {e}")
    
    return {
        "message": "Reindexing complete",
        "documents_indexed": indexed_count,
        "total_documents_in_store": len(vectorstore.data)
    }


@router.get("/vectorstore/stats")
def vectorstore_stats():
    """Get vectorstore statistics"""
    stats = {
        "total_documents": len(vectorstore.data),
        "documents_by_type": {}
    }
    
    for doc_id, doc_data in vectorstore.data.items():
        doc_type = doc_data.get("metadata", {}).get("type", "unknown")
        if doc_type not in stats["documents_by_type"]:
            stats["documents_by_type"][doc_type] = 0
        stats["documents_by_type"][doc_type] += 1
    
    return stats


@router.post("/vectorstore/clear")
def clear_vectorstore():
    """Clear all documents from vectorstore (for testing)"""
    vectorstore.clear()
    return {
        "message": "Vectorstore cleared",
        "documents_in_store": len(vectorstore.data)
    }
