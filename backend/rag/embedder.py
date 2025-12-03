from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embeddings for RAG system"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"Initialized embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def embed_text(self, text: str):
        """Generate embedding for a single text"""
        try:
            return self.model.encode([text])[0]
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_batch(self, texts: list):
        """Generate embeddings for multiple texts"""
        try:
            return self.model.encode(texts)
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            raise


# Legacy function for backward compatibility
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text):
    """Legacy function - use EmbeddingManager instead"""
    return embedder.encode([text])[0]
