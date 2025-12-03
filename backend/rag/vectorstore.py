from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for RAG system using JSON storage"""
    
    def __init__(self, store_path: str = "storage/vectorstore.json"):
        self.store_path = store_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.data = self._load_store()
        
        # Initialize with sample documents if empty
        if not self.data:
            self._init_sample_documents()
        
        logger.info(f"Initialized VectorStore at {store_path} with {len(self.data)} documents")
    
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
        sample_docs = {
            "sample_1": {
                "text": "User authentication feature: Implement secure login with email and password. Accept criteria: User can login with valid credentials, invalid credentials show error message, remember me option for 30 days.",
                "metadata": {"type": "epic", "category": "authentication"}
            },
            "sample_2": {
                "text": "API endpoint for user registration: POST /api/users/register with email, password, name. Response includes user ID and auth token. Validation for email format and password strength.",
                "metadata": {"type": "story", "category": "api"}
            },
            "sample_3": {
                "text": "Database schema migration: Create users table with id, email, password_hash, created_at, updated_at. Add indexes on email for faster lookups. Support for role-based access control.",
                "metadata": {"type": "implementation", "category": "database"}
            },
            "sample_4": {
                "text": "QA Test: Login with valid email and password, verify token is returned, check token validity. Test invalid email format rejection, test password strength requirements.",
                "metadata": {"type": "qa", "category": "testing"}
            },
            "sample_5": {
                "text": "Two-factor authentication feature: Send OTP via email after login, verify OTP before granting access. Support TOTP apps like Google Authenticator. Recovery codes for backup access.",
                "metadata": {"type": "epic", "category": "security"}
            }
        }
        
        for doc_id, doc_data in sample_docs.items():
            try:
                self.store_document(doc_data["text"], doc_id, doc_data.get("metadata", {}))
            except Exception as e:
                logger.error(f"Error initializing sample document {doc_id}: {e}")
    
    
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