"""Unit tests for RAG embedding utilities"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from rag.embedder import EmbeddingManager, embed_text


class TestEmbeddingManager:
    """Test EmbeddingManager class"""
    
    @patch('rag.embedder.SentenceTransformer')
    def test_initialization_default_model(self, mock_st):
        """Test EmbeddingManager initialization with default model"""
        mock_model = Mock()
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        
        assert manager.model == mock_model
        assert manager.model_name == "all-MiniLM-L6-v2"
        mock_st.assert_called_once_with("all-MiniLM-L6-v2")
    
    @patch('rag.embedder.SentenceTransformer')
    def test_initialization_custom_model(self, mock_st):
        """Test EmbeddingManager initialization with custom model"""
        mock_model = Mock()
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager("custom-model")
        
        assert manager.model == mock_model
        assert manager.model_name == "custom-model"
        mock_st.assert_called_once_with("custom-model")
    
    @patch('rag.embedder.SentenceTransformer')
    def test_initialization_failure(self, mock_st):
        """Test EmbeddingManager initialization failure"""
        mock_st.side_effect = Exception("Model not found")
        
        with pytest.raises(Exception):
            EmbeddingManager()
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_single(self, mock_st):
        """Test embedding a single text"""
        mock_model = Mock()
        embedding = np.array([0.1, 0.2, 0.3, 0.4])
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_text("Sample text")
        
        assert np.array_equal(result, embedding)
        mock_model.encode.assert_called_once_with(["Sample text"])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_empty_string(self, mock_st):
        """Test embedding an empty string"""
        mock_model = Mock()
        embedding = np.array([0.0] * 384)  # Default dimension
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_text("")
        
        mock_model.encode.assert_called_once_with([""])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_special_characters(self, mock_st):
        """Test embedding text with special characters"""
        mock_model = Mock()
        embedding = np.array([0.1] * 384)
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        text_with_chars = "Special chars: !@#$%^&*()"
        result = manager.embed_text(text_with_chars)
        
        mock_model.encode.assert_called_once_with([text_with_chars])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_unicode(self, mock_st):
        """Test embedding unicode text"""
        mock_model = Mock()
        embedding = np.array([0.2] * 384)
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        unicode_text = "中文文本 العربية हिन्दी"
        result = manager.embed_text(unicode_text)
        
        mock_model.encode.assert_called_once()
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_long_text(self, mock_st):
        """Test embedding very long text"""
        mock_model = Mock()
        embedding = np.array([0.15] * 384)
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        long_text = "word " * 10000  # Very long text
        result = manager.embed_text(long_text)
        
        mock_model.encode.assert_called_once()
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_text_failure(self, mock_st):
        """Test embedding failure"""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding error")
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        with pytest.raises(Exception):
            manager.embed_text("text")
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_empty(self, mock_st):
        """Test embedding empty batch"""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_batch([])
        
        mock_model.encode.assert_called_once_with([])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_single_item(self, mock_st):
        """Test embedding batch with single item"""
        mock_model = Mock()
        embedding = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = embedding
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_batch(["Single text"])
        
        assert np.array_equal(result, embedding)
        mock_model.encode.assert_called_once_with(["Single text"])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_multiple_items(self, mock_st):
        """Test embedding batch with multiple items"""
        mock_model = Mock()
        embeddings = np.array([
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6]
        ])
        mock_model.encode.return_value = embeddings
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        texts = ["Text 1", "Text 2", "Text 3"]
        result = manager.embed_batch(texts)
        
        assert np.array_equal(result, embeddings)
        assert result.shape == (3, 2)
        mock_model.encode.assert_called_once_with(texts)
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_large_batch(self, mock_st):
        """Test embedding large batch"""
        mock_model = Mock()
        batch_size = 1000
        embeddings = np.random.rand(batch_size, 384)
        mock_model.encode.return_value = embeddings
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        texts = [f"Text {i}" for i in range(batch_size)]
        result = manager.embed_batch(texts)
        
        assert result.shape[0] == batch_size
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_failure(self, mock_st):
        """Test batch embedding failure"""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Batch encoding error")
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        with pytest.raises(Exception):
            manager.embed_batch(["text1", "text2"])
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embed_batch_with_special_texts(self, mock_st):
        """Test batch embedding with special texts"""
        mock_model = Mock()
        embeddings = np.array([[0.1] * 384, [0.2] * 384, [0.3] * 384])
        mock_model.encode.return_value = embeddings
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        texts = [
            "Normal text",
            "Text with 123 numbers!",
            ""  # Empty string
        ]
        result = manager.embed_batch(texts)
        
        assert result.shape[0] == 3


class TestEmbedTextLegacyFunction:
    """Test legacy embed_text function"""
    
    @patch('rag.embedder.embedder')
    def test_embed_text_legacy(self, mock_embedder):
        """Test legacy embed_text function"""
        embedding = np.array([0.1, 0.2, 0.3])
        mock_embedder.encode.return_value = np.array([embedding])
        
        result = embed_text("Sample text")
        
        assert np.array_equal(result, embedding)
        mock_embedder.encode.assert_called_once_with(["Sample text"])
    
    @patch('rag.embedder.embedder')
    def test_embed_text_legacy_returns_first_embedding(self, mock_embedder):
        """Test legacy function returns first embedding from batch"""
        embeddings = np.array([
            [0.1, 0.2],
            [0.3, 0.4]
        ])
        mock_embedder.encode.return_value = embeddings
        
        result = embed_text("text")
        
        # Should return first embedding
        assert np.array_equal(result, embeddings[0])


class TestEmbeddingDimensions:
    """Test embedding output dimensions"""
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embedding_dimension_consistency(self, mock_st):
        """Test embedding dimensions are consistent"""
        mock_model = Mock()
        # all-MiniLM-L6-v2 produces 384-dim embeddings
        embedding = np.random.rand(384)
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_text("text")
        
        assert len(result) == 384
    
    @patch('rag.embedder.SentenceTransformer')
    def test_batch_embeddings_same_dimension(self, mock_st):
        """Test all batch embeddings have same dimension"""
        mock_model = Mock()
        embeddings = np.random.rand(5, 384)
        mock_model.encode.return_value = embeddings
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_batch(["t1", "t2", "t3", "t4", "t5"])
        
        # All embeddings should have dimension 384
        assert all(len(emb) == 384 for emb in result)


class TestEmbeddingNormalization:
    """Test embedding normalization and properties"""
    
    @patch('rag.embedder.SentenceTransformer')
    def test_embedding_returns_array(self, mock_st):
        """Test embedding returns numpy array"""
        mock_model = Mock()
        embedding = np.array([0.1, 0.2, 0.3])
        mock_model.encode.return_value = np.array([embedding])
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_text("text")
        
        assert isinstance(result, np.ndarray)
    
    @patch('rag.embedder.SentenceTransformer')
    def test_batch_embeddings_returns_2d_array(self, mock_st):
        """Test batch returns 2D array"""
        mock_model = Mock()
        embeddings = np.random.rand(3, 384)
        mock_model.encode.return_value = embeddings
        mock_st.return_value = mock_model
        
        manager = EmbeddingManager()
        result = manager.embed_batch(["t1", "t2", "t3"])
        
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 2
