from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import logging
import uuid
from typing import List, Dict, Any, Optional
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for RAG system with caching and optimized search"""
    
    # Class-level cache for embeddings to avoid redundant computations
    _embedding_cache: Dict[str, np.ndarray] = {}
    _cache_timestamp: Dict[str, datetime] = {}
    CACHE_TTL = timedelta(hours=24)  # Cache embeddings for 24 hours
    
    def __init__(self, store_path: str = "storage/vectorstore.json", upload_id: str = None):
        """
        Initialize vector store with caching support.
        
        Args:
            store_path: Base path for vector stores
            upload_id: Optional upload ID for per-upload vector stores
        """
        if upload_id:
            # Create per-upload vector store path
            self.upload_id = str(upload_id)
            base_dir = os.path.dirname(store_path) or "storage"
            self.store_path = os.path.join(base_dir, f"vectorstore_upload_{upload_id}.json")
        else:
            self.store_path = store_path
            self.upload_id = None
        
        # Lazy load model only when needed
        self._model = None
        self.data = self._load_store()
        
        logger.info(f"Initialized VectorStore at {self.store_path} with {len(self.data)} documents")
    
    @property
    def model(self):
        """Lazy load embedding model to avoid initialization overhead"""
        if self._model is None:
            logger.debug("Initializing embedding model")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model
    
    @staticmethod
    def create_vectorstore_id() -> str:
        """Generate a unique vector store ID"""
        return str(uuid.uuid4())
    
    def _load_store(self) -> Dict[str, Any]:
        """Load vectorstore from disk with error handling"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading vectorstore from {self.store_path}: {e}")
                return {}
        return {}
    
    def _save_store(self) -> None:
        """Save vectorstore to disk with atomic writes"""
        try:
            os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
            # Write to temp file first for atomicity
            temp_path = f"{self.store_path}.tmp"
            with open(temp_path, "w") as f:
                json.dump(self.data, f, indent=2)
            # Atomic rename
            os.replace(temp_path, self.store_path)
            logger.debug(f"Saved vectorstore to {self.store_path}")
        except Exception as e:
            logger.error(f"Error saving vectorstore: {e}")
            raise
    
    def _get_cached_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding from cache or compute and cache it.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Embedding vector
        """
        # Clean cache for expired entries
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self._cache_timestamp.items()
            if now - timestamp > self.CACHE_TTL
        ]
        for key in expired_keys:
            del self._embedding_cache[key]
            del self._cache_timestamp[key]
        
        # Check cache
        if text in self._embedding_cache:
            logger.debug("Using cached embedding")
            return self._embedding_cache[text]
        
        # Compute and cache
        embedding = self.model.encode(text)
        self._embedding_cache[text] = embedding
        self._cache_timestamp[text] = datetime.now()
        return embedding
    
    def store_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        Store a document with its embedding.
        
        Args:
            text: Document text
            doc_id: Unique document ID
            metadata: Optional metadata for the document
            
        Returns:
            True if successful
            
        Raises:
            Exception: If storage fails
        """
        try:
            embedding = self._get_cached_embedding(text).tolist()
            self.data[doc_id] = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }
            self._save_store()
            logger.info(f"Stored document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing document {doc_id}: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.0) -> List[Dict]:
        """
        Search vectorstore for similar documents with optimizations.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not self.data:
                logger.warning("Vectorstore is empty")
                return []
            
            query_embedding = self._get_cached_embedding(query)
            results = []
            
            # Vectorized computation for better performance
            for doc_id, doc_data in self.data.items():
                try:
                    doc_embedding = np.array(doc_data["embedding"])
                    
                    # Compute cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    
                    if similarity >= similarity_threshold:
                        results.append({
                            "doc_id": doc_id,
                            "text": doc_data["text"],
                            "similarity": float(similarity),
                            "metadata": doc_data.get("metadata", {}),
                            "created_at": doc_data.get("created_at")
                        })
                except Exception as e:
                    logger.warning(f"Error processing document {doc_id}: {e}")
                    continue
            
            # Sort by similarity descending and return top-k
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
            logger.debug(f"Found {len(results)} results for query (threshold: {similarity_threshold})")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectorstore: {e}")
            raise
    
    @staticmethod
    def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec_a: First vector
            vec_b: Second vector
            
        Returns:
            Cosine similarity value
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from vectorstore.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
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
    
    def delete_by_metadata(self, metadata_key: str, metadata_value: Any) -> int:
        """
        Delete documents matching metadata criteria.
        
        Args:
            metadata_key: Metadata field key
            metadata_value: Metadata field value
            
        Returns:
            Number of documents deleted
        """
        deleted_count = 0
        try:
            doc_ids_to_delete = [
                doc_id for doc_id, doc_data in self.data.items()
                if doc_data.get("metadata", {}).get(metadata_key) == metadata_value
            ]
            
            for doc_id in doc_ids_to_delete:
                del self.data[doc_id]
                deleted_count += 1
            
            if deleted_count > 0:
                self._save_store()
                logger.info(f"Deleted {deleted_count} documents by metadata")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents by metadata: {e}")
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vectorstore statistics"""
        return {
            "total_documents": len(self.data),
            "store_path": self.store_path,
            "embedding_cache_size": len(self._embedding_cache),
            "upload_id": self.upload_id
        }


# Maintain backward compatibility with legacy functions
_default_store = None

def get_default_store() -> VectorStore:
    """Get or create default vectorstore instance"""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store

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