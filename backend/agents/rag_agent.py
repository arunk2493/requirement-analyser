from typing import Dict, Any, List
from config.db import get_db
from models.file_model import Upload
from rag.embedder import EmbeddingManager
from rag.vectorstore import VectorStore
from .base_agent import BaseAgent, AgentResponse


class RAGAgent(BaseAgent):
    """Agent responsible for retrieving relevant documents from RAG system"""

    def __init__(self):
        super().__init__("RAGAgent")
        try:
            self.embedder = EmbeddingManager()
            self.vectorstore = VectorStore()
        except Exception as e:
            self.log_execution("error", f"Failed to initialize RAG components: {str(e)}")
            self.embedder = None
            self.vectorstore = None

    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Retrieve relevant documents from RAG system.
        
        Context expects:
            - query (str): Search query
            - upload_id (int, optional): Specific upload to search within
            - top_k (int, optional): Number of results to return (default: 5)
        """
        try:
            if not self.embedder or not self.vectorstore:
                return self.create_response(
                    success=False,
                    data=None,
                    message="RAG system not initialized",
                    error="Missing embedder or vectorstore"
                )

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

            self.log_execution("info", f"Searching RAG for: {query}")

            # Search vectorstore with query string
            results = self.vectorstore.search(query, top_k=top_k)

            # Filter by upload_id if provided
            if upload_id and results:
                with get_db() as db:
                    upload = db.query(Upload).filter(Upload.id == upload_id).first()
                    if upload:
                        # Convert upload content to string for filtering
                        import json
                        upload_content_str = json.dumps(upload.content) if isinstance(upload.content, dict) else str(upload.content)
                        results = [r for r in results if upload_content_str in str(r.get("text", "")).lower()]

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
            return self.create_response(
                success=False,
                data=None,
                message="Error retrieving documents from RAG",
                error=str(e)
            )
