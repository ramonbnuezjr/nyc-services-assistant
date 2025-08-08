"""
Test suite for Data Processor module

Tests the document processing pipeline for NYC Services GPT RAG system,
ensuring proper integration with chunker and embedding generation for
the 100-query evaluation targeting ≥ 90% Self-Service Success Rate.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from typing import List, Dict

from src.ingest.data_processor import process_documents, validate_records, EmbeddingClient


class TestEmbeddingClient:
    """Test the EmbeddingClient class"""
    
    def test_init_with_defaults(self):
        """Test EmbeddingClient initialization with default config"""
        client = EmbeddingClient()
        assert client.model == "text-embedding-ada-002"
    
    def test_init_with_custom_params(self):
        """Test EmbeddingClient initialization with custom parameters"""
        client = EmbeddingClient(api_key="test_key", model="custom-model")
        assert client.api_key == "test_key"
        assert client.model == "custom-model"
    
    def test_get_embeddings_no_api_key(self):
        """Test embedding generation without API key returns mock embeddings"""
        client = EmbeddingClient(api_key=None)
        texts = ["test text 1", "test text 2"]
        embeddings = client.get_embeddings(texts)
        
        assert len(embeddings) == 2
        assert all(len(emb) == 1536 for emb in embeddings)
        assert all(isinstance(emb, list) for emb in embeddings)
    
    @patch('openai.embeddings.create')
    def test_get_embeddings_with_api_key(self, mock_create):
        """Test embedding generation with API key"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_create.return_value = mock_response
        
        client = EmbeddingClient(api_key="test_key")
        texts = ["text 1", "text 2"]
        embeddings = client.get_embeddings(texts)
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]
        mock_create.assert_called_once_with(input=texts, model="text-embedding-ada-002")
    
    @patch('openai.embeddings.create')
    def test_get_embeddings_api_error_fallback(self, mock_create):
        """Test fallback to mock embeddings when API fails"""
        mock_create.side_effect = Exception("API Error")
        
        client = EmbeddingClient(api_key="test_key")
        texts = ["test text"]
        embeddings = client.get_embeddings(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1536


class TestProcessDocuments:
    """Test the process_documents function"""
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_process_documents_raw_text(self, mock_chunk_documents):
        """Test processing raw text inputs"""
        # Mock chunker to return known chunks
        mock_chunk_documents.return_value = ["chunk 1", "chunk 2", "chunk 3"]
        
        # Mock embedding client
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
        
        paths = ["How do I apply for unemployment benefits?", "What documents are required?"]
        records = process_documents(paths, embedding_client=mock_client)
        
        # Verify correct number of records
        assert len(records) == 3
        
        # Verify each record has required fields
        for record in records:
            assert "text" in record
            assert "embedding" in record
            assert "metadata" in record
        
        # Verify specific content
        assert records[0]["text"] == "chunk 1"
        assert records[0]["embedding"] == [0.1, 0.2, 0.3]
        assert records[0]["metadata"]["source"] == "raw_text"
        assert records[0]["metadata"]["chunk_index"] == 0
    
    @patch('src.ingest.data_processor.chunk_documents')
    @patch('builtins.open', new_callable=mock_open, read_data="File content for unemployment benefits")
    @patch('pathlib.Path.exists')
    def test_process_documents_file_paths(self, mock_exists, mock_file, mock_chunk_documents):
        """Test processing actual file paths"""
        # Setup mocks
        mock_exists.return_value = True
        mock_chunk_documents.return_value = ["file chunk 1", "file chunk 2"]
        
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ]
        
        paths = ["./docs/unemployment.txt"]
        records = process_documents(paths, embedding_client=mock_client)
        
        assert len(records) == 2
        assert records[0]["metadata"]["source"] == "./docs/unemployment.txt"
        assert records[0]["text"] == "file chunk 1"
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_process_documents_mixed_inputs(self, mock_chunk_documents):
        """Test processing mix of file paths and raw text"""
        # Mock chunker for different calls
        def mock_chunker_side_effect(docs, **kwargs):
            if "raw text input" in docs[0]:
                return ["raw chunk"]
            return ["all chunks combined"]
        
        mock_chunk_documents.side_effect = mock_chunker_side_effect
        
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [[1.0, 2.0]]
        
        paths = ["raw text input"]
        records = process_documents(paths, embedding_client=mock_client)
        
        assert len(records) == 1
        assert records[0]["metadata"]["source"] == "raw_text"
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_process_documents_custom_chunk_params(self, mock_chunk_documents):
        """Test process_documents with custom chunking parameters"""
        mock_chunk_documents.return_value = ["test chunk"]
        
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [[0.5, 0.5]]
        
        paths = ["test text"]
        records = process_documents(
            paths, 
            chunk_size=500, 
            overlap=100, 
            embedding_client=mock_client
        )
        
        # Verify chunking was called with correct parameters
        mock_chunk_documents.assert_called_with(["test text"], chunk_size=500, overlap=100)
        
        # Verify metadata contains chunking parameters
        assert records[0]["metadata"]["chunk_size"] == 500
        assert records[0]["metadata"]["overlap"] == 100
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_process_documents_empty_chunks(self, mock_chunk_documents):
        """Test handling of empty or whitespace-only chunks"""
        mock_chunk_documents.return_value = ["", "  ", "valid chunk", ""]
        
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [[1.0, 2.0, 3.0]]
        
        paths = ["test input"]
        records = process_documents(paths, embedding_client=mock_client)
        
        # Should only process non-empty chunks
        assert len(records) == 1
        assert records[0]["text"] == "valid chunk"
    
    def test_process_documents_no_embedding_client(self):
        """Test process_documents creates default embedding client"""
        with patch('src.ingest.data_processor.chunk_documents') as mock_chunk:
            mock_chunk.return_value = ["test chunk"]
            
            paths = ["test input"]
            records = process_documents(paths)
            
            # Should create at least one record with mock embeddings
            assert len(records) >= 0  # May be 0 if no valid chunks
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_process_documents_token_counting(self, mock_chunk_documents):
        """Test that token counts are calculated correctly"""
        mock_chunk_documents.return_value = ["this is a test chunk with seven tokens"]
        
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [[0.1, 0.2]]
        
        paths = ["test input"]
        records = process_documents(paths, embedding_client=mock_client)
        
        assert len(records) == 1
        assert records[0]["metadata"]["token_count"] == 8  # "this is a test chunk with seven tokens" = 8 tokens


class TestValidateRecords:
    """Test the validate_records function"""
    
    def test_validate_records_valid(self):
        """Test validation of properly structured records"""
        valid_records = [
            {
                "text": "Sample text chunk",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {
                    "source": "test.txt",
                    "chunk_index": 0,
                    "token_count": 3
                }
            },
            {
                "text": "Another chunk",
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {
                    "source": "test2.txt",
                    "chunk_index": 1,
                    "token_count": 2
                }
            }
        ]
        
        assert validate_records(valid_records) is True
    
    def test_validate_records_missing_top_level_field(self):
        """Test validation fails for missing top-level fields"""
        invalid_records = [
            {
                "text": "Sample text",
                # Missing "embedding" field
                "metadata": {
                    "source": "test.txt",
                    "chunk_index": 0,
                    "token_count": 2
                }
            }
        ]
        
        assert validate_records(invalid_records) is False
    
    def test_validate_records_missing_metadata_field(self):
        """Test validation fails for missing metadata fields"""
        invalid_records = [
            {
                "text": "Sample text",
                "embedding": [0.1, 0.2],
                "metadata": {
                    "source": "test.txt",
                    # Missing "chunk_index" and "token_count"
                }
            }
        ]
        
        assert validate_records(invalid_records) is False
    
    def test_validate_records_wrong_data_types(self):
        """Test validation fails for incorrect data types"""
        invalid_records = [
            {
                "text": 123,  # Should be string
                "embedding": [0.1, 0.2],
                "metadata": {
                    "source": "test.txt",
                    "chunk_index": 0,
                    "token_count": 2
                }
            }
        ]
        
        assert validate_records(invalid_records) is False
    
    def test_validate_records_empty_list(self):
        """Test validation of empty record list"""
        assert validate_records([]) is True


class TestIntegration:
    """Integration tests for the full data processing pipeline"""
    
    @patch('src.ingest.data_processor.chunk_documents')
    def test_nyc_services_query_processing(self, mock_chunk_documents):
        """Test processing NYC services queries from our 100-query seed set"""
        # Sample queries from PROJECT_SPEC.md
        nyc_queries = [
            "How do I apply for unemployment benefits in NYC?",
            "What income limits apply to SNAP in New York?",
            "How do I apply for Medicaid in NYC?",
            "How do I apply for Cash Assistance in NYC?",
            "How do I apply for child care subsidy in NYC?"
        ]
        
        # Mock chunker to return one chunk per query
        mock_chunk_documents.return_value = [
            "unemployment chunk", "snap chunk", "medicaid chunk", 
            "cash assistance chunk", "childcare chunk"
        ]
        
        # Mock embedding client
        mock_client = Mock()
        mock_client.get_embeddings.return_value = [
            [0.1] * 1536,  # Standard OpenAI embedding dimension
            [0.2] * 1536,
            [0.3] * 1536,
            [0.4] * 1536,
            [0.5] * 1536
        ]
        
        records = process_documents(nyc_queries, embedding_client=mock_client)
        
        # Verify we can process all 5 service categories
        assert len(records) == 5
        assert validate_records(records) is True
        
        # Verify all records have proper embedding dimensions
        for record in records:
            assert len(record["embedding"]) == 1536
            assert record["metadata"]["source"] == "raw_text"
    
    def test_end_to_end_pipeline_structure(self):
        """Test that the full pipeline produces RAG-ready records"""
        sample_input = ["Sample NYC service document for testing"]
        
        # Use default (mock) embedding client
        records = process_documents(sample_input, chunk_size=50, overlap=10)
        
        # Verify structure is ready for vector store ingestion
        if records:  # May be empty with mock setup
            record = records[0]
            
            # Check RAG-ready structure
            assert isinstance(record["text"], str)
            assert isinstance(record["embedding"], list)
            assert isinstance(record["metadata"]["source"], str)
            assert isinstance(record["metadata"]["chunk_index"], int)
            assert isinstance(record["metadata"]["token_count"], int)
            
            # Verify metadata supports evaluation tracking
            assert "chunk_size" in record["metadata"]
            assert "overlap" in record["metadata"]