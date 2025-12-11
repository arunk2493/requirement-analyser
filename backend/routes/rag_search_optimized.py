from fastapi import APIRouter, HTTPException, Query
from models.file_model import Upload, Epic, QA
from config.db import get_db, get_db_context
import numpy as np
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
SEARCH_QUERY_DESC = "Search query across all uploads and epics"
TOP_K_RESULTS_DESC = "Number of top results to return (max 5)"

# Initialize model once at module level for reuse
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    embedding_model = None


def _calculate_similarity_np(query_embedding, doc_embedding):
    """Calculate cosine similarity between two embeddings using numpy."""
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


def _search_database_only(db, query, top_k):
    """
    Search through uploads, epics, and test plans.
    Returns sorted results with similarity scores and Confluence links.
    """
    results = []
    
    if not embedding_model:
        logger.error("Embedding model not initialized")
        return results
    
    try:
        # Get query embedding once
        logger.info(f"Encoding query: '{query}'")
        query_embedding = embedding_model.encode(query, show_progress_bar=False)
        logger.info(f"Query embedding shape: {query_embedding.shape}")
        
        # Search uploads
        uploads = db.query(Upload).all()
        logger.info(f"Found {len(uploads)} uploads in database")
        
        for upload in uploads:
            try:
                upload_text = ""
                if upload.content and isinstance(upload.content, dict):
                    upload_text = upload.content.get("requirement", "")
                
                if upload_text and len(upload_text.strip()) > 0:
                    upload_embedding = embedding_model.encode(upload_text, show_progress_bar=False)
                    similarity = _calculate_similarity_np(query_embedding, upload_embedding)
                    
                    results.append({
                        "type": "upload",
                        "upload_id": upload.id,
                        "upload_name": upload.filename,
                        "similarity_score": round(similarity, 4),
                        "similarity_percentage": round(similarity * 100, 2),
                        "confluence_page_id": upload.confluence_page_id
                    })
            except Exception as e:
                logger.error(f"Error processing upload {upload.id}: {str(e)}")
                continue
        
        # Search epics
        epics = db.query(Epic).all()
        logger.info(f"Found {len(epics)} epics in database")
        
        for epic in epics:
            try:
                epic_text = ""
                if epic.name:
                    epic_text = epic.name
                if epic.content and isinstance(epic.content, dict):
                    description = epic.content.get("description", "")
                    if description:
                        epic_text += " " + description
                
                if epic_text and len(epic_text.strip()) > 0:
                    epic_embedding = embedding_model.encode(epic_text, show_progress_bar=False)
                    similarity = _calculate_similarity_np(query_embedding, epic_embedding)
                    
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
            except Exception as e:
                logger.error(f"Error processing epic {epic.id}: {str(e)}")
                continue
        
        # Search test plans
        test_plans = db.query(QA).filter(QA.type == "test_plan").all()
        logger.info(f"Found {len(test_plans)} test plans in database")
        
        for test_plan in test_plans:
            try:
                test_plan_text = ""
                if test_plan.content and isinstance(test_plan.content, dict):
                    title = test_plan.content.get("title", "")
                    objective = test_plan.content.get("objective", "")
                    test_plan_text = f"{title} {objective}"
                
                if test_plan_text and len(test_plan_text.strip()) > 0:
                    test_plan_embedding = embedding_model.encode(test_plan_text, show_progress_bar=False)
                    similarity = _calculate_similarity_np(query_embedding, test_plan_embedding)
                    
                    epic = db.query(Epic).filter(Epic.id == test_plan.epic_id).first()
                    upload = None
                    if epic:
                        upload = db.query(Upload).filter(Upload.id == epic.upload_id).first()
                    
                    results.append({
                        "type": "test_plan",
                        "test_plan_id": test_plan.id,
                        "test_plan_title": test_plan.content.get("title", "Test Plan") if test_plan.content else "Test Plan",
                        "epic_id": test_plan.epic_id,
                        "epic_name": epic.name if epic else "Unknown",
                        "upload_id": epic.upload_id if epic else None,
                        "upload_name": upload.filename if upload else "Unknown",
                        "similarity_score": round(similarity, 4),
                        "similarity_percentage": round(similarity * 100, 2),
                        "confluence_page_id": test_plan.confluence_page_id
                    })
            except Exception as e:
                logger.error(f"Error processing test_plan {test_plan.id}: {str(e)}")
                continue
        
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
    top_k: int = Query(5, ge=1, le=5, description=TOP_K_RESULTS_DESC)
):
    """
    Search through all uploads, epics, and test plans using semantic similarity.
    Returns matching documents ranked by relevance with Confluence links.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        with get_db_context() as db:
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
    top_k: int = Query(5, ge=1, le=5, description=TOP_K_RESULTS_DESC)
):
    """POST endpoint for RAG search through database."""
    return rag_search_database(query=query, top_k=top_k)


@router.get("/rag/search-grouped")
def rag_search_grouped_by_upload(
    query: str = Query(..., description=SEARCH_QUERY_DESC),
    top_k: int = Query(5, ge=1, le=5, description=TOP_K_RESULTS_DESC)
):
    """
    Search database and return results grouped by upload.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        with get_db_context() as db:
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
    top_k: int = Query(5, ge=1, le=5, description=TOP_K_RESULTS_DESC)
):
    """POST endpoint for grouped RAG search."""
    return rag_search_grouped_by_upload(query=query, top_k=top_k)
