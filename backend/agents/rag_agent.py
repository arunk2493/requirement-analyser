from typing import Dict, Any, List
from config.db import get_db
from models.file_model import Upload, Epic, QA
from rag.embedder import EmbeddingManager
from .base_agent import BaseAgent, AgentResponse
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    """Agent responsible for retrieving relevant documents from RAG system"""

    def __init__(self):
        super().__init__("RAGAgent")
        try:
            self.embedder = EmbeddingManager()
        except Exception as e:
            self.log_execution("error", f"Failed to initialize RAG components: {str(e)}")
            self.embedder = None

    def _get_embedding(self, text):
        """Get embedding for text using sentence transformer."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            return None

    def _calculate_similarity(self, query_embedding, doc_embedding):
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

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Retrieve relevant documents from RAG system.
        
        Context expects:
            - query (str): Search query
            - upload_id (int, optional): Specific upload to search within
            - top_k (int, optional): Number of results to return (default: 5)
        """
        try:
            query = context.get("query")
            if not query:
                return self.create_response(
                    success=False,
                    data=None,
                    message="No query provided",
                    error="Missing query in context"
                )

            upload_id = context.get("upload_id")
            top_k = context.get("top_k", 5)

            self.log_execution("info", f"Searching RAG database for: {query}")

            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return self.create_response(
                    success=False,
                    data=None,
                    message="Failed to embed query",
                    error="Embedding generation failed"
                )

            results = []

            with get_db() as db:
                # Search in uploads table
                uploads = db.query(Upload).all()
                
                for upload in uploads:
                    if upload_id and upload.id != upload_id:
                        continue
                    
                    upload_text = ""
                    if upload.content and isinstance(upload.content, dict):
                        upload_text = upload.content.get("requirement", "")
                    
                    if upload_text and len(upload_text.strip()) > 0:
                        upload_embedding = self._get_embedding(upload_text)
                        if upload_embedding:
                            similarity = self._calculate_similarity(query_embedding, upload_embedding)
                            
                            results.append({
                                "type": "upload",
                                "text": upload_text,
                                "similarity": round(similarity, 4),
                                "metadata": {
                                    "type": "upload",
                                    "upload_id": upload.id,
                                    "upload_name": upload.filename,
                                    "confluence_page_id": upload.confluence_page_id
                                }
                            })
                
                # Search in epics table
                epics = db.query(Epic).all()
                
                for epic in epics:
                    if upload_id and epic.upload_id != upload_id:
                        continue
                    
                    epic_text = ""
                    if epic.name:
                        epic_text = epic.name
                    if epic.content and isinstance(epic.content, dict):
                        description = epic.content.get("description", "")
                        if description:
                            epic_text += " " + description
                    
                    if epic_text and len(epic_text.strip()) > 0:
                        epic_embedding = self._get_embedding(epic_text)
                        if epic_embedding:
                            similarity = self._calculate_similarity(query_embedding, epic_embedding)
                            
                            upload = db.query(Upload).filter(Upload.id == epic.upload_id).first()
                            
                            results.append({
                                "type": "epic",
                                "text": epic_text,
                                "similarity": round(similarity, 4),
                                "metadata": {
                                    "type": "epic",
                                    "epic_id": epic.id,
                                    "epic_name": epic.name,
                                    "upload_id": epic.upload_id,
                                    "upload_name": upload.filename if upload else "Unknown",
                                    "confluence_page_id": epic.confluence_page_id
                                }
                            })
                
                # Search in test plans (QA table with type='test_plan')
                test_plans = db.query(QA).filter(QA.type == "test_plan").all()
                
                for test_plan in test_plans:
                    if upload_id and test_plan.epic_id:
                        epic = db.query(Epic).filter(Epic.id == test_plan.epic_id).first()
                        if not epic or epic.upload_id != upload_id:
                            continue
                    
                    test_plan_text = ""
                    if test_plan.content and isinstance(test_plan.content, dict):
                        title = test_plan.content.get("title", "")
                        objective = test_plan.content.get("objective", "")
                        test_plan_text = f"{title} {objective}"
                    
                    if test_plan_text and len(test_plan_text.strip()) > 0:
                        test_plan_embedding = self._get_embedding(test_plan_text)
                        if test_plan_embedding:
                            similarity = self._calculate_similarity(query_embedding, test_plan_embedding)
                            
                            epic = db.query(Epic).filter(Epic.id == test_plan.epic_id).first()
                            upload = None
                            if epic:
                                upload = db.query(Upload).filter(Upload.id == epic.upload_id).first()
                            
                            results.append({
                                "type": "test_plan",
                                "text": test_plan_text,
                                "similarity": round(similarity, 4),
                                "metadata": {
                                    "type": "test_plan",
                                    "test_plan_id": test_plan.id,
                                    "test_plan_title": test_plan.content.get("title", "Test Plan") if test_plan.content else "Test Plan",
                                    "epic_id": test_plan.epic_id,
                                    "epic_name": epic.name if epic else "Unknown",
                                    "upload_id": epic.upload_id if epic else None,
                                    "upload_name": upload.filename if upload else "Unknown",
                                    "confluence_page_id": test_plan.confluence_page_id
                                }
                            })

            # Sort by similarity and limit to top_k
            results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]

            if not results:
                return self.create_response(
                    success=True,
                    data={"documents": [], "query": query},
                    message="No results found"
                )

            formatted_results = [
                {
                    "text": r.get("text", ""),
                    "similarity": r.get("similarity", 0),
                    "metadata": r.get("metadata", {})
                }
                for r in results
            ]

            self.log_execution("info", f"Found {len(formatted_results)} relevant documents")
            return self.create_response(
                success=True,
                data={"documents": formatted_results, "query": query},
                message=f"Retrieved {len(formatted_results)} relevant documents"
            )

        except Exception as e:
            self.log_execution("error", f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.create_response(
                success=False,
                data=None,
                message="Error retrieving documents from RAG",
                error=str(e)
            )
