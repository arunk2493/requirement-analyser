from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for RAG system using JSON storage with per-upload support"""
    
    def __init__(self, store_path: str = "storage/vectorstore.json", upload_id: str = None):
        """
        Initialize vector store.
        
        Args:
            store_path: Base path for vector stores
            upload_id: Optional upload ID for per-upload vector stores. 
                      If provided, creates a unique store path for this upload.
        """
        if upload_id:
            # Create per-upload vector store path
            self.upload_id = str(upload_id)
            base_dir = os.path.dirname(store_path) or "storage"
            self.store_path = os.path.join(base_dir, f"vectorstore_upload_{upload_id}.json")
        else:
            self.store_path = store_path
            self.upload_id = None
            
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.data = self._load_store()
        
        # Initialize with sample documents only if default store and empty
        if not self.data and upload_id is None:
            self._init_sample_documents()
        
        logger.info(f"Initialized VectorStore at {self.store_path} with {len(self.data)} documents")
    
    @staticmethod
    def create_vectorstore_id() -> str:
        """Generate a unique vector store ID"""
        return str(uuid.uuid4())
    
    def _load_store(self) -> Dict[str, Any]:
        """Load vectorstore from disk"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading vectorstore: {e}")
                return {}
        return {}
    
    def _init_sample_documents(self):
        """Initialize with sample documents for demo purposes"""
        # Removed hardcoded sample documents - only use actual data from database
        pass
    
    
    def _save_store(self):
        """Save vectorstore to disk"""
        try:
            os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
            with open(self.store_path, "w") as f:
                json.dump(self.data, f)
        except Exception as e:
            logger.error(f"Error saving vectorstore: {e}")
            raise
    
    def store_document(self, text: str, doc_id: str, metadata: Dict = None) -> bool:
        """Store a document with its embedding"""
        try:
            embedding = self.model.encode(text).tolist()
            self.data[doc_id] = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            self._save_store()
            logger.info(f"Stored document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing document {doc_id}: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search vectorstore for similar documents"""
        try:
            if not self.data:
                logger.warning("Vectorstore is empty")
                return []
            
            query_embedding = self.model.encode(query)
            results = []
            
            for doc_id, doc_data in self.data.items():
                doc_embedding = np.array(doc_data["embedding"])
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding) + 1e-8
                )
                results.append({
                    "doc_id": doc_id,
                    "text": doc_data["text"],
                    "similarity": float(similarity),
                    "metadata": doc_data.get("metadata", {})
                })
            
            # Sort by similarity descending and return top-k
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
            logger.info(f"Found {len(results)} results for query")
            return results
        except Exception as e:
            logger.error(f"Error searching vectorstore: {e}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from vectorstore"""
        try:
            if doc_id in self.data:
                del self.data[doc_id]
                self._save_store()
                logger.info(f"Deleted document: {doc_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise
    
    def clear(self) -> bool:
        """Clear all documents from vectorstore"""
        try:
            self.data = {}
            self._save_store()
            logger.info("Cleared vectorstore")
            return True
        except Exception as e:
            logger.error(f"Error clearing vectorstore: {e}")
            raise


# Legacy functions for backward compatibility
model = SentenceTransformer("all-MiniLM-L6-v2")
STORE_PATH = "storage/vectorstore.json"

def store_document(text: str, doc_id: str):
    """Legacy function - use VectorStore class instead"""
    embedding = model.encode(text).tolist()
    
    if not os.path.exists("storage"):
        os.makedirs("storage")
    
    data = {}
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, "r") as f:
            data = json.load(f)
    
    data[doc_id] = {
        "text": text,
        "embedding": embedding
    }
    
    with open(STORE_PATH, "w") as f:
        json.dump(data, f)
    
    return True