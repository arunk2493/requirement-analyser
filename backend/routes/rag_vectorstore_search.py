from fastapi import APIRouter, HTTPException, Query, Depends
import json
import os
import logging
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import sys

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.file_model import Epic, QA, Upload
from config.db import get_db, get_db_context
from config.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize embedding model
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model loaded successfully for vectorstore search")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {str(e)}")
    embedding_model = None

# Storage folder path
STORAGE_FOLDER = Path(__file__).parent.parent / "storage"


def _load_vectorstore_files():
    """Load all vectorstore JSON files from storage folder."""
    vectorstore_data = {}
    try:
        if not STORAGE_FOLDER.exists():
            logger.warning(f"Storage folder does not exist: {STORAGE_FOLDER}")
            return vectorstore_data
        
        # Find all JSON files in storage folder
        json_files = list(STORAGE_FOLDER.glob("vectorstore*.json"))
        logger.info(f"Found {len(json_files)} vectorstore JSON files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vectorstore_data[json_file.stem] = data
                    logger.info(f"Loaded vectorstore: {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully loaded {len(vectorstore_data)} vectorstore files")
    except Exception as e:
        logger.error(f"Error accessing storage folder: {str(e)}")
    
    return vectorstore_data


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


def _search_vectorstore(query, top_k=5):
    """
    Search through vectorstore JSON files.
    Returns top_k results sorted by similarity score.
    """
    results = []
    
    if not embedding_model:
        logger.error("Embedding model not initialized")
        raise HTTPException(status_code=500, detail="Embedding model not available")
    
    try:
        # Load all vectorstore files
        vectorstore_data = _load_vectorstore_files()
        
        if not vectorstore_data:
            logger.warning("No vectorstore files found or loaded")
            return results
        
        # Get query embedding
        logger.info(f"Encoding query: '{query}'")
        query_embedding = embedding_model.encode(query, show_progress_bar=False).tolist()
        logger.info(f"Query embedding created with dimension: {len(query_embedding)}")
        
        # Search through all vectorstore files
        for store_name, store_data in vectorstore_data.items():
            _search_vectorstore_file(store_name, store_data, query_embedding, results)
        
        logger.info(f"Total vectorstore results before sorting: {len(results)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching vectorstore: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Vectorstore search error: {str(e)}")
    
    # Sort by similarity and limit to top_k
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]
    logger.info(f"Returning {len(results)} vectorstore results after sorting and limiting to top_k={top_k}")
    return results


def _search_vectorstore_file(store_name, store_data, query_embedding, results):
    """Search a single vectorstore file and add results to list."""
    logger.info(f"Searching in {store_name} with {len(store_data)} items")
    
    for doc_key, doc_data in store_data.items():
        try:
            # Extract text and embedding from document
            if isinstance(doc_data, dict):
                text = doc_data.get("text", "")
                doc_embedding = doc_data.get("embedding", None)
                metadata = doc_data.get("metadata", {})
                
                # If no embedding in file, skip or compute
                if not doc_embedding:
                    logger.debug(f"No embedding found for {doc_key} in {store_name}, computing...")
                    if text:
                        doc_embedding = embedding_model.encode(text, show_progress_bar=False).tolist()
                    else:
                        continue
                
                # Calculate similarity
                similarity = _calculate_similarity(query_embedding, doc_embedding)
                
                # Add to results if similarity is above threshold
                if similarity > 0.1:  # Filter very low scores
                    results.append({
                        "source": "vectorstore",
                        "vectorstore": store_name,
                        "document_id": doc_key,
                        "text": text[:500],  # Truncate text for response
                        "full_text": text,  # Keep full text for reference
                        "similarity_score": round(similarity, 4),
                        "similarity_percentage": round(similarity * 100, 2),
                        "metadata": metadata
                    })
        except Exception as e:
            logger.error(f"Error processing document {doc_key} in {store_name}: {str(e)}")
            continue


def _search_database(query, top_k=5):
    """
    Search through database Epics and Test Plans.
    Returns results sorted by similarity score.
    """
    results = []
    
    if not embedding_model:
        logger.error("Embedding model not initialized")
        raise HTTPException(status_code=500, detail="Embedding model not available")
    
    try:
        # Get query embedding
        logger.info(f"Encoding query for database search: '{query}'")
        query_embedding = embedding_model.encode(query, show_progress_bar=False).tolist()
        
        with get_db_context() as db:
            # Search epics
            _search_epics_in_db(db, query_embedding, results)
            
            # Search test plans
            _search_test_plans_in_db(db, query_embedding, results)
        
        logger.info(f"Total database results before sorting: {len(results)}")
    
    except Exception as e:
        logger.error(f"Error searching database: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Sort by similarity and limit to top_k
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]
    logger.info(f"Returning {len(results)} database results after sorting and limiting to top_k={top_k}")
    return results


def _search_epics_in_db(db, query_embedding, results):
    """Search epics in database and add to results."""
    try:
        epics = db.query(Epic).all()
        logger.info(f"Found {len(epics)} epics in database")
        
        for epic in epics:
            try:
                epic_text = epic.name if epic.name else ""
                if epic.content and isinstance(epic.content, dict):
                    description = epic.content.get("description", "")
                    if description:
                        epic_text += " " + description
                
                if epic_text and len(epic_text.strip()) > 0:
                    epic_embedding = embedding_model.encode(epic_text, show_progress_bar=False).tolist()
                    similarity = _calculate_similarity(query_embedding, epic_embedding)
                    
                    if similarity > 0.1:  # Filter very low scores
                        results.append({
                            "source": "database",
                            "type": "epic",
                            "document_id": f"epic_{epic.id}",
                            "epic_id": epic.id,
                            "epic_name": epic.name,
                            "text": epic_text[:500],
                            "full_text": epic_text,
                            "similarity_score": round(similarity, 4),
                            "similarity_percentage": round(similarity * 100, 2),
                            "metadata": {
                                "type": "epic",
                                "upload_id": epic.upload_id,
                                "confluence_page_id": epic.confluence_page_id
                            }
                        })
            except Exception as e:
                logger.error(f"Error processing epic {epic.id}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error searching epics: {str(e)}")


def _search_test_plans_in_db(db, query_embedding, results):
    """Search test plans in database and add to results."""
    try:
        test_plans = db.query(QA).filter(QA.type == "test_plan").all()
        logger.info(f"Found {len(test_plans)} test plans in database")
        
        for test_plan in test_plans:
            try:
                test_plan_text = ""
                if test_plan.content and isinstance(test_plan.content, dict):
                    title = test_plan.content.get("title", "")
                    objective = test_plan.content.get("objective", "")
                    test_plan_text = f"{title} {objective}".strip()
                
                if test_plan_text and len(test_plan_text) > 0:
                    test_plan_embedding = embedding_model.encode(test_plan_text, show_progress_bar=False).tolist()
                    similarity = _calculate_similarity(query_embedding, test_plan_embedding)
                    
                    if similarity > 0.1:  # Filter very low scores
                        results.append({
                            "source": "database",
                            "type": "test_plan",
                            "document_id": f"test_plan_{test_plan.id}",
                            "test_plan_id": test_plan.id,
                            "test_plan_title": test_plan.content.get("title", "Test Plan") if test_plan.content else "Test Plan",
                            "epic_id": test_plan.epic_id,
                            "text": test_plan_text[:500],
                            "full_text": test_plan_text,
                            "similarity_score": round(similarity, 4),
                            "similarity_percentage": round(similarity * 100, 2),
                            "metadata": {
                                "type": "test_plan",
                                "epic_id": test_plan.epic_id,
                                "confluence_page_id": test_plan.confluence_page_id
                            }
                        })
            except Exception as e:
                logger.error(f"Error processing test_plan {test_plan.id}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error searching test plans: {str(e)}")


def _search_uploads_in_db(db, query_embedding, results, current_user: TokenData = None):
    """
    Search through uploaded documents (from uploads table).
    Returns results sorted by similarity score.
    """
    try:
        # Get user's uploads
        if current_user:
            uploads = db.query(Upload).filter(Upload.user_id == current_user.user_id).all()
        else:
            uploads = db.query(Upload).all()
        
        logger.info(f"Searching {len(uploads)} uploads")
        
        for upload in uploads:
            try:
                # Get the requirement text from content
                if upload.content and isinstance(upload.content, dict):
                    text = upload.content.get("requirement", "")
                else:
                    text = str(upload.content) if upload.content else ""
                
                if not text or len(text) < 5:
                    continue
                
                # Encode text
                doc_embedding = embedding_model.encode(text, show_progress_bar=False).tolist()
                
                # Calculate similarity
                similarity = _calculate_similarity(query_embedding, doc_embedding)
                
                # Add to results if similarity is above threshold
                if similarity > 0.1:
                    results.append({
                        "source": "upload",
                        "document_id": f"upload_{upload.id}",
                        "filename": upload.filename,
                        "upload_id": upload.id,
                        "text": text[:500],  # Truncate text for response
                        "full_text": text,  # Keep full text for reference
                        "similarity_score": round(similarity, 4),
                        "similarity_percentage": round(similarity * 100, 2),
                        "metadata": {
                            "type": "requirement",
                            "filename": upload.filename,
                            "upload_id": upload.id
                        }
                    })
            except Exception as e:
                logger.error(f"Error processing upload {upload.id}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error searching uploads: {str(e)}")


@router.get("/rag/vectorstore-search")
def rag_vectorstore_search(
    query: str = Query(..., description="Search query across uploads and database"),
    top_k: int = Query(5, ge=1, le=10, description="Number of top results to return (max 10)"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Search through uploaded documents (uploads table) AND database (Epics, Test Plans) using semantic similarity.
    Returns matching documents ranked by relevance from both sources combined.
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"RAG combined search initiated for query: '{query}' by user {current_user.user_id}")
        
        # Search both sources
        with get_db_context() as db:
            # Get query embedding
            query_embedding = embedding_model.encode(query, show_progress_bar=False).tolist() if embedding_model else []
            
            all_results = []
            
            # Search uploads (user-specific)
            _search_uploads_in_db(db, query_embedding, all_results, current_user)
            
            # Search database (epics and test plans)
            _search_epics_in_db(db, query_embedding, all_results)
            _search_test_plans_in_db(db, query_embedding, all_results)
        
        # Sort by similarity and limit to top_k
        all_results = sorted(all_results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]
        
        if len(all_results) == 0:
            return {
                "message": "No results found",
                "query": query,
                "search_results": [],
                "total_matches": 0,
                "top_k_requested": top_k,
                "sources": ["uploads", "epics", "test_plans"]
            }
        
        logger.info(f"Combined search completed: {len(all_results)} total results")
        
        return {
            "message": "Search completed successfully",
            "query": query,
            "search_results": all_results,
            "total_matches": len(all_results),
            "top_k_requested": top_k,
            "sources": ["uploads", "epics", "test_plans"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in combined RAG search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")


@router.post("/rag/vectorstore-search")
def rag_vectorstore_search_post(
    query: str = Query(..., description="Search query across uploads and database"),
    top_k: int = Query(5, ge=1, le=10, description="Number of top results to return (max 10)"),
    current_user: TokenData = Depends(get_current_user)
):
    """POST endpoint for combined RAG search."""
    return rag_vectorstore_search(query=query, top_k=top_k, current_user=current_user)
