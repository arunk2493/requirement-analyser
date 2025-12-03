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
            "doc_auth_login": {
                "text": "Authentication and Login Feature: Users must be able to log in using email and password. The system should validate credentials against the database, handle invalid login attempts with appropriate error messages, support password reset functionality, and implement session management with secure token-based authentication.",
                "metadata": {"type": "epic", "category": "authentication", "name": "Login Feature"}
            },
            "doc_auth_mfa": {
                "text": "Multi-Factor Authentication: Implement two-factor authentication for enhanced security. Support OTP via email, SMS, and authenticator apps. Users can enable/disable MFA in account settings. Recovery codes should be provided for account recovery. All authentication attempts should be logged.",
                "metadata": {"type": "epic", "category": "security", "name": "MFA System"}
            },
            "doc_api_users": {
                "text": "User Management API: Create REST endpoints for user CRUD operations. Endpoints: POST /api/users/register, GET /api/users/{id}, PUT /api/users/{id}, DELETE /api/users/{id}. Each endpoint should validate input, check authorization, and return standardized JSON responses with proper HTTP status codes.",
                "metadata": {"type": "story", "category": "api", "name": "User API Endpoints"}
            },
            "doc_api_auth": {
                "text": "Authentication API Endpoints: Implement POST /api/auth/login, POST /api/auth/logout, POST /api/auth/refresh-token, POST /api/auth/verify-email. All endpoints must validate requests, handle errors gracefully, and return JWT tokens with appropriate expiration times.",
                "metadata": {"type": "story", "category": "api", "name": "Auth Endpoints"}
            },
            "doc_db_schema": {
                "text": "Database Schema Design: Create tables for users with fields: id (primary key), email (unique), password_hash, first_name, last_name, created_at, updated_at. Add indexes on email and created_at for performance. Implement foreign key relationships for user roles and permissions.",
                "metadata": {"type": "implementation", "category": "database", "name": "User Database Schema"}
            },
            "doc_db_security": {
                "text": "Database Security: Implement row-level security policies. Use prepared statements to prevent SQL injection. Encrypt sensitive data at rest. Enable audit logging for all database changes. Regular backups should be automated with encryption.",
                "metadata": {"type": "implementation", "category": "database", "name": "Security Policies"}
            },
            "doc_qa_login": {
                "text": "QA Test Cases for Login: Test valid credentials, invalid email format, incorrect password, account lockout after failed attempts, password reset flow, remember me functionality, session timeout, and concurrent login handling.",
                "metadata": {"type": "qa", "category": "testing", "name": "Login Test Suite"}
            },
            "doc_qa_api": {
                "text": "API Testing: Test all endpoints with valid/invalid inputs, verify response status codes, validate JSON schema compliance, test rate limiting, verify authentication headers, test error messages, performance testing with load testing.",
                "metadata": {"type": "qa", "category": "testing", "name": "API Test Coverage"}
            },
            "doc_performance": {
                "text": "Performance Requirements: Login must complete within 500ms. API response time should be under 1 second for all endpoints. Database queries must be optimized with appropriate indexes. Implement caching for frequently accessed data. Support at least 1000 concurrent users.",
                "metadata": {"type": "epic", "category": "performance", "name": "Performance SLA"}
            },
            "doc_deployment": {
                "text": "Deployment Strategy: Use containerized deployment with Docker. Implement CI/CD pipeline using GitHub Actions. Automated testing before production deployment. Blue-green deployment strategy for zero-downtime updates. Health checks and monitoring with alerts.",
                "metadata": {"type": "implementation", "category": "devops", "name": "Deployment Pipeline"}
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