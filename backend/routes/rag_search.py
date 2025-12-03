from fastapi import APIRouter, HTTPException, Query, Depends
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.file_model import Upload, Epic, QA
from config.db import get_db
from config.auth import get_current_user, TokenData
import numpy as np
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
SEARCH_QUERY_DESC = "Search query across all uploads and epics"
TOP_K_DESC = "Number of top results to return"

# Initialize model once at module level for reuse
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    embedding_model = None

# Cache for embeddings to avoid recalculating
_embedding_cache = {}


def _get_embedding(text, use_cache=True):
    """Get embedding for text using sentence transformer with caching."""
    try:
        # Check cache first
        if use_cache and text in _embedding_cache:
            return _embedding_cache[text]
        
        if not embedding_model:
            return None
        
        embedding = embedding_model.encode(text, show_progress_bar=False).tolist()
        
        # Store in cache
        if use_cache:
            _embedding_cache[text] = embedding
        
        return embedding
    except Exception as e:
        logger.error(f"Error embedding text: {str(e)}")
        return None


def _calculate_similarity(query_embedding, doc_embedding):
    """Calculate cosine similarity between two embeddings."""
    try:
        query_vec = np.array(query_embedding)
        doc_vec = np.array(doc_embedding)
        
        norm_q = np.linalg.norm(query_vec)
        norm_d = np.linalg.norm(doc_vec)
        
        if norm_q == 0 or norm_d == 0:
            return 0.0
        
        similarity = np.dot(query_vec, doc_vec) / (norm_q * norm_d)
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0


def _extract_text(obj):
    """Safely extract text from various object types."""
    if isinstance(obj, str):
        return obj.strip()
    elif isinstance(obj, dict):
        text_parts = []
        for value in obj.values():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(v) for v in value if v])
        return " ".join(text_parts).strip()
    elif isinstance(obj, (list, tuple)):
        return " ".join([str(v) for v in obj if v]).strip()
    return str(obj).strip() if obj else ""


def _search_database_only(db, query, top_k):
    """
    Search through uploads, epics, and test plans (no stories or other details).
    Returns sorted results with similarity scores and Confluence links.
    """
    results = []
    
    try:
        # Get query embedding
        query_embedding = _get_embedding(query)
        if not query_embedding:
            logger.error("Failed to embed query")
            return results
        
        logger.info(f"Searching database for query: '{query}'")
        
        # Search in uploads table
        uploads = db.query(Upload).all()
        logger.info(f"Found {len(uploads)} uploads in database")
        
        for upload in uploads:
            upload_text = _extract_text(upload.content) if upload.content else ""
            
            if upload_text:
                upload_embedding = _get_embedding(upload_text)
                if upload_embedding:
                    similarity = _calculate_similarity(query_embedding, upload_embedding)
                    if similarity > 0.05:  # Filter very low scores
                        results.append({
                            "type": "upload",
                            "upload_id": upload.id,
                            "upload_name": upload.filename,
                            "similarity_score": round(similarity, 4),
                            "similarity_percentage": round(similarity * 100, 2),
                            "confluence_page_id": upload.confluence_page_id
                        })
        
        # Search in epics table
        epics = db.query(Epic).all()
        logger.info(f"Found {len(epics)} epics in database")
        
        for epic in epics:
            epic_text = epic.name if epic.name else ""
            if epic.content:
                content_text = _extract_text(epic.content)
                epic_text = f"{epic_text} {content_text}".strip()
            
            if epic_text:
                epic_embedding = _get_embedding(epic_text)
                if epic_embedding:
                    similarity = _calculate_similarity(query_embedding, epic_embedding)
                    if similarity > 0.05:  # Filter very low scores
                        # Get parent upload
                        upload = db.query(Upload).filter(Upload.id == epic.upload_id).first()
                        
                        results.append({
                            "type": "epic",
                            "epic_id": epic.id,
                            "epic_name": epic.name,
                            "upload_id": epic.upload_id,
                            "upload_name": upload.filename if upload else "Unknown",
                            "similarity_score": round(similarity, 4),
                            "similarity_percentage": round(similarity * 100, 2),
                            "confluence_page_id": epic.confluence_page_id
                        })
        
        # Search in test plans (QA table with type='test_plan')
        test_plans = db.query(QA).filter(QA.type == "test_plan").all()
        logger.info(f"Found {len(test_plans)} test plans in database")
        
        for test_plan in test_plans:
            test_plan_text = _extract_text(test_plan.content) if test_plan.content else ""
            
            if test_plan_text:
                test_plan_embedding = _get_embedding(test_plan_text)
                if test_plan_embedding:
                    similarity = _calculate_similarity(query_embedding, test_plan_embedding)
                    if similarity > 0.05:  # Filter very low scores
                        # Get parent epic and upload
                        epic = db.query(Epic).filter(Epic.id == test_plan.epic_id).first()
                        upload = None
                        if epic:
                            upload = db.query(Upload).filter(Upload.id == epic.upload_id).first()
                        
                        results.append({
                            "type": "test_plan",
                            "test_plan_id": test_plan.id,
                            "test_plan_title": test_plan.content.get("title", "Test Plan") if isinstance(test_plan.content, dict) else "Test Plan",
                            "epic_id": test_plan.epic_id,
                            "epic_name": epic.name if epic else "Unknown",
                            "upload_id": epic.upload_id if epic else None,
                            "upload_name": upload.filename if upload else "Unknown",
                            "similarity_score": round(similarity, 4),
                            "similarity_percentage": round(similarity * 100, 2),
                            "confluence_page_id": test_plan.confluence_page_id
                        })
        
        logger.info(f"Total results before sorting: {len(results)}")
    
    except Exception as e:
        logger.error(f"Error searching database: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Sort by similarity and limit to top_k
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]
    logger.info(f"Returning {len(results)} results after sorting and limiting to top_k={top_k}")
    return results


@router.get("/rag/search")
def rag_search_database(
    query: str = Query(..., description=SEARCH_QUERY_DESC),
    top_k: int = Query(5, ge=1, le=5, description="Number of top results to return (max 5)"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Search through all uploads, epics, and test plans in DATABASE ONLY using semantic similarity.
    Does NOT use vector store JSON files.
    Returns matching uploads, epics, and test plans ranked by relevance with Confluence links.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        with get_db() as db:
            results = _search_database_only(db, query, top_k)
            
            logger.info(f"RAG search completed: {len(results)} results for '{query}'")
            
            if len(results) == 0:
                return {
                    "message": "No results found",
                    "query": query,
                    "search_results": [],
                    "total_matches": 0,
                    "top_k_requested": top_k,
                    "source": "database"
                }
            
            return {
                "message": "RAG search completed successfully",
                "query": query,
                "search_results": results,
                "total_matches": len(results),
                "top_k_requested": top_k,
                "source": "database"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")


@router.post("/rag/search")
def rag_search_database_post(
    query: str = Query(..., description=SEARCH_QUERY_DESC),
    top_k: int = Query(5, ge=1, le=5, description="Number of top results to return (max 5)")
):
    """POST endpoint for RAG search through database."""
    return rag_search_database(query=query, top_k=top_k)


@router.get("/rag/search-grouped")
def rag_search_grouped_by_upload(
    query: str = Query(..., description=SEARCH_QUERY_DESC),
    top_k: int = Query(5, ge=1, le=5, description="Number of top results to return (max 5)"),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Search database and return results grouped by upload (epics and uploads only).
    Useful for UI visualization showing which uploads contain relevant content.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        with get_db() as db:
            results = _search_database_only(db, query, top_k * 3)
            
            # Group results by upload
            grouped_by_upload = {}
            
            for result in results:
                upload_id = result.get("upload_id")
                
                if upload_id not in grouped_by_upload:
                    upload = db.query(Upload).filter(Upload.id == upload_id).first()
                    grouped_by_upload[upload_id] = {
                        "upload_id": upload_id,
                        "upload_name": upload.filename if upload else "Unknown",
                        "confluence_page_id": upload.confluence_page_id if upload else None,
                        "highest_match_score": result["similarity_score"],
                        "highest_match_percentage": result["similarity_percentage"],
                        "epics": [],
                        "test_plans": [],
                        "upload_matches": 0
                    }
                
                if result["type"] == "epic":
                    grouped_by_upload[upload_id]["epics"].append({
                        "epic_id": result["epic_id"],
                        "epic_name": result["epic_name"],
                        "similarity_score": result["similarity_score"],
                        "similarity_percentage": result["similarity_percentage"],
                        "confluence_page_id": result.get("confluence_page_id")
                    })
                elif result["type"] == "test_plan":
                    grouped_by_upload[upload_id]["test_plans"].append({
                        "test_plan_id": result["test_plan_id"],
                        "test_plan_title": result["test_plan_title"],
                        "epic_id": result["epic_id"],
                        "epic_name": result["epic_name"],
                        "similarity_score": result["similarity_score"],
                        "similarity_percentage": result["similarity_percentage"],
                        "confluence_page_id": result.get("confluence_page_id")
                    })
                else:
                    grouped_by_upload[upload_id]["upload_matches"] += 1
            
            # Sort uploads by highest match score
            sorted_uploads = sorted(
                grouped_by_upload.values(),
                key=lambda x: x["highest_match_score"],
                reverse=True
            )
            
            logger.info(f"RAG grouped search: {len(sorted_uploads)} uploads with matches for '{query}'")
            
            if len(sorted_uploads) == 0:
                return {
                    "message": "No results found",
                    "query": query,
                    "uploads_with_results": [],
                    "total_uploads_with_matches": 0,
                    "total_epics_found": 0,
                    "total_test_plans_found": 0,
                    "source": "database"
                }
            
            return {
                "message": "RAG grouped search completed successfully",
                "query": query,
                "uploads_with_results": sorted_uploads,
                "total_uploads_with_matches": len(sorted_uploads),
                "total_epics_found": sum(len(u["epics"]) for u in sorted_uploads),
                "total_test_plans_found": sum(len(u["test_plans"]) for u in sorted_uploads),
                "source": "database"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in grouped RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")


@router.post("/rag/search-grouped")
def rag_search_grouped_post(
    query: str = Query(..., description=SEARCH_QUERY_DESC),
    top_k: int = Query(5, ge=1, le=5, description="Number of top results to return (max 5)")
):
    """POST endpoint for grouped RAG search."""
    return rag_search_grouped_by_upload(query=query, top_k=top_k)
