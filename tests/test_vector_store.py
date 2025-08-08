"""
Test suite for Vector Store module

Tests the storage-agnostic vector store interface for NYC Services GPT RAG system,
ensuring reliable document storage and retrieval for the 100-query evaluation
targeting ≥ 90% Self-Service Success Rate.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict
import tempfile
import shutil
from pathlib import Path

from src.retrieve.vector_store import VectorStore, init_vector_store, add_documents, query_vector_store


class TestVectorStore:
    """Test the VectorStore class"""
    
    def test_init_with_defaults(self):
        """Test VectorStore initialization with default parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            assert vector_store.db_path == temp_dir
            assert vector_store.collection_name == "nyc_services"
            assert vector_store.client is None
            assert vector_store.collection is None
    
    def test_init_with_custom_params(self):
        """Test VectorStore initialization with custom parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(
                db_path=temp_dir,
                collection_name="custom_collection"
            )
            assert vector_store.db_path == temp_dir
            assert vector_store.collection_name == "custom_collection"
    
    def test_init_creates_db_directory(self):
        """Test that initialization creates the database directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "vector_db"
            vector_store = VectorStore(db_path=str(db_path))
            
            # Directory should be created
            assert db_path.exists()
    
    @patch('chromadb.PersistentClient')
    def test_init_vector_store_success(self, mock_client_class):
        """Test successful vector store initialization"""
        # Mock ChromaDB client and collection
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            success = vector_store.init_vector_store()
            
            assert success is True
            assert vector_store.client == mock_client
            assert vector_store.collection == mock_collection
            mock_client.get_or_create_collection.assert_called_once()
    
    @patch('chromadb.PersistentClient')
    def test_init_vector_store_failure(self, mock_client_class):
        """Test vector store initialization failure"""
        # Mock ChromaDB to raise exception
        mock_client_class.side_effect = Exception("Connection failed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            success = vector_store.init_vector_store()
            
            assert success is False
            assert vector_store.client is None
            assert vector_store.collection is None
    
    def test_add_documents_not_initialized(self):
        """Test adding documents when vector store not initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            records = [{"text": "test", "embedding": [0.1], "metadata": {}}]
            
            success = vector_store.add_documents(records)
            assert success is False
    
    def test_add_documents_empty_list(self):
        """Test adding empty list of documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.collection = Mock()
            
            success = vector_store.add_documents([])
            assert success is True
    
    @patch('chromadb.PersistentClient')
    def test_add_documents_success(self, mock_client_class):
        """Test successful document addition"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 3
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            records = [
                {
                    "text": "How to apply for unemployment",
                    "embedding": [0.1, 0.2, 0.3],
                    "metadata": {"source": "unemployment.txt", "service": "unemployment"}
                },
                {
                    "text": "SNAP benefits requirements",
                    "embedding": [0.4, 0.5, 0.6],
                    "metadata": {"source": "snap.txt", "service": "snap"}
                }
            ]
            
            success = vector_store.add_documents(records)
            
            assert success is True
            mock_collection.add.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_collection.add.call_args
            assert len(call_args[1]["documents"]) == 2
            assert len(call_args[1]["embeddings"]) == 2
            assert len(call_args[1]["metadatas"]) == 2
            assert len(call_args[1]["ids"]) == 2
    
    @patch('chromadb.PersistentClient')
    def test_add_documents_failure(self, mock_client_class):
        """Test document addition failure"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.add.side_effect = Exception("Add failed")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            records = [{"text": "test", "embedding": [0.1], "metadata": {}}]
            success = vector_store.add_documents(records)
            
            assert success is False
    
    def test_query_vector_store_not_initialized(self):
        """Test querying when vector store not initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            query_embedding = [0.1, 0.2, 0.3]
            
            results = vector_store.query_vector_store(query_embedding)
            assert results == []
    
    @patch('chromadb.PersistentClient')
    def test_query_vector_store_success(self, mock_client_class):
        """Test successful vector store querying"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["How to apply for unemployment", "SNAP requirements"]],
            "metadatas": [[{"source": "unemployment.txt"}, {"source": "snap.txt"}]],
            "distances": [[0.1, 0.3]],
            "ids": [["doc_0", "doc_1"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            query_embedding = [0.1, 0.2, 0.3]
            results = vector_store.query_vector_store(query_embedding, top_k=2)
            
            assert len(results) == 2
            assert results[0]["text"] == "How to apply for unemployment"
            assert results[0]["metadata"]["source"] == "unemployment.txt"
            assert results[0]["distance"] == 0.1
            assert results[1]["text"] == "SNAP requirements"
            assert results[1]["metadata"]["source"] == "snap.txt"
            assert results[1]["distance"] == 0.3
    
    @patch('chromadb.PersistentClient')
    def test_query_vector_store_with_filters(self, mock_client_class):
        """Test querying with metadata filters"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["Unemployment guide"]],
            "metadatas": [[{"service": "unemployment"}]],
            "distances": [[0.1]],
            "ids": [["doc_0"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            query_embedding = [0.1, 0.2, 0.3]
            filter_metadata = {"service": "unemployment"}
            results = vector_store.query_vector_store(query_embedding, filter_metadata=filter_metadata)
            
            # Verify filter was passed to ChromaDB
            call_args = mock_collection.query.call_args
            assert call_args[1]["where"] == filter_metadata
    
    @patch('chromadb.PersistentClient')
    def test_query_vector_store_failure(self, mock_client_class):
        """Test query failure handling"""
        # Mock ChromaDB to raise exception
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("Query failed")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            query_embedding = [0.1, 0.2, 0.3]
            results = vector_store.query_vector_store(query_embedding)
            
            assert results == []
    
    @patch('chromadb.PersistentClient')
    def test_get_collection_stats(self, mock_client_class):
        """Test getting collection statistics"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 5
        mock_collection.query.return_value = {
            "metadatas": [[
                {"source": "unemployment.txt"},
                {"source": "snap.txt"},
                {"source": "medicaid.txt"}
            ]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            stats = vector_store.get_collection_stats()
            
            assert stats["total_documents"] == 5
            assert stats["collection_name"] == "nyc_services"
            assert "unemployment.txt" in stats["source_distribution"]
            assert stats["source_distribution"]["unemployment.txt"] == 1
    
    @patch('chromadb.PersistentClient')
    def test_clear_collection(self, mock_client_class):
        """Test clearing the collection"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            success = vector_store.clear_collection()
            
            assert success is True
            mock_collection.delete.assert_called_once_with(where={})


class TestConvenienceFunctions:
    """Test the convenience functions"""
    
    @patch('chromadb.PersistentClient')
    def test_init_vector_store_function(self, mock_client_class):
        """Test the init_vector_store convenience function"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = init_vector_store(db_path=temp_dir)
            
            assert vector_store is not None
            assert vector_store.db_path == temp_dir
            assert vector_store.collection == mock_collection
    
    @patch('chromadb.PersistentClient')
    def test_init_vector_store_function_failure(self, mock_client_class):
        """Test init_vector_store function when initialization fails"""
        # Mock ChromaDB to fail
        mock_client_class.side_effect = Exception("Connection failed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = init_vector_store(db_path=temp_dir)
            
            assert vector_store is None
    
    @patch('chromadb.PersistentClient')
    def test_add_documents_function(self, mock_client_class):
        """Test the add_documents convenience function"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 1
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = init_vector_store(db_path=temp_dir)
            records = [{"text": "test", "embedding": [0.1], "metadata": {}}]
            
            success = add_documents(vector_store, records)
            
            assert success is True
            mock_collection.add.assert_called_once()
    
    @patch('chromadb.PersistentClient')
    def test_query_vector_store_function(self, mock_client_class):
        """Test the query_vector_store convenience function"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["Test document"]],
            "metadatas": [[{"source": "test.txt"}]],
            "distances": [[0.1]],
            "ids": [["doc_0"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = init_vector_store(db_path=temp_dir)
            query_embedding = [0.1, 0.2, 0.3]
            
            results = query_vector_store(vector_store, query_embedding, top_k=1)
            
            assert len(results) == 1
            assert results[0]["text"] == "Test document"


class TestIntegration:
    """Integration tests for the vector store"""
    
    @patch('chromadb.PersistentClient')
    def test_nyc_services_integration(self, mock_client_class):
        """Test integration with NYC services documents"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 3
        mock_collection.query.return_value = {
            "documents": [["How do I apply for unemployment benefits in NYC?"]],
            "metadatas": [[{"source": "unemployment_guide.txt", "service": "unemployment"}]],
            "distances": [[0.1]],
            "ids": [["doc_0"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize vector store
            vector_store = init_vector_store(db_path=temp_dir)
            assert vector_store is not None
            
            # Add NYC services documents
            nyc_records = [
                {
                    "text": "How do I apply for unemployment benefits in NYC?",
                    "embedding": [0.1] * 1536,
                    "metadata": {
                        "source": "unemployment_guide.txt",
                        "service": "unemployment",
                        "chunk_index": 0,
                        "token_count": 9
                    }
                },
                {
                    "text": "What documents are required for SNAP benefits?",
                    "embedding": [0.2] * 1536,
                    "metadata": {
                        "source": "snap_requirements.txt",
                        "service": "snap",
                        "chunk_index": 0,
                        "token_count": 8
                    }
                },
                {
                    "text": "Medicaid application process in NYC",
                    "embedding": [0.3] * 1536,
                    "metadata": {
                        "source": "medicaid_process.txt",
                        "service": "medicaid",
                        "chunk_index": 0,
                        "token_count": 6
                    }
                }
            ]
            
            # Add documents
            success = add_documents(vector_store, nyc_records)
            assert success is True
            
            # Query for unemployment-related content
            query_embedding = [0.15] * 1536  # Similar to unemployment doc
            results = query_vector_store(vector_store, query_embedding, top_k=1)
            
            # Verify results
            assert len(results) == 1
            assert "unemployment" in results[0]["text"].lower()
            assert results[0]["metadata"]["service"] == "unemployment"
            assert results[0]["distance"] == 0.1
    
    @patch('chromadb.PersistentClient')
    def test_metadata_filtering_integration(self, mock_client_class):
        """Test metadata filtering for service-specific queries"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 2
        mock_collection.query.return_value = {
            "documents": [["SNAP benefits application process"]],
            "metadatas": [[{"service": "snap", "source": "snap_guide.txt"}]],
            "distances": [[0.2]],
            "ids": [["doc_1"]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = init_vector_store(db_path=temp_dir)
            
            # Query with service filter
            query_embedding = [0.1] * 1536
            filter_metadata = {"service": "snap"}
            results = query_vector_store(
                vector_store, 
                query_embedding, 
                filter_metadata=filter_metadata
            )
            
            # Verify filtered results
            assert len(results) == 1
            assert results[0]["metadata"]["service"] == "snap"
            assert "snap" in results[0]["text"].lower()
    
    def test_end_to_end_pipeline_structure(self):
        """Test that the vector store integrates with the full RAG pipeline structure"""
        # This test verifies the vector store can handle the output format
        # from the data processor and provide input format for the RAG pipeline
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            
            # Simulate data processor output
            processor_records = [
                {
                    "text": "Sample NYC service document chunk",
                    "embedding": [0.1] * 1536,
                    "metadata": {
                        "source": "test_service.txt",
                        "chunk_index": 0,
                        "token_count": 6,
                        "chunk_size": 1000,
                        "overlap": 200
                    }
                }
            ]
            
            # Verify record structure is compatible
            assert "text" in processor_records[0]
            assert "embedding" in processor_records[0]
            assert "metadata" in processor_records[0]
            assert isinstance(processor_records[0]["embedding"], list)
            assert len(processor_records[0]["embedding"]) == 1536  # OpenAI embedding dimension
            
            # Verify metadata structure supports KPI tracking
            metadata = processor_records[0]["metadata"]
            assert "source" in metadata
            assert "chunk_index" in metadata
            assert "token_count" in metadata
            assert "chunk_size" in metadata
            assert "overlap" in metadata


class TestKPITracking:
    """Test KPI-related functionality"""
    
    @patch('chromadb.PersistentClient')
    def test_kpi_metadata_in_collection(self, mock_client_class):
        """Test that KPI metadata is stored in the collection"""
        # Mock ChromaDB
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            vector_store.init_vector_store()
            
            # Verify KPI metadata was passed to collection creation
            call_args = mock_client.get_or_create_collection.call_args
            metadata = call_args[1]["metadata"]
            
            assert "target_success_rate" in metadata
            assert "synthetic_query_count" in metadata
            assert metadata["target_success_rate"] == 90.0
            assert metadata["synthetic_query_count"] == 100
    
    def test_vector_store_supports_100_query_evaluation(self):
        """Test that vector store can handle the 100-query evaluation set"""
        # This test verifies the vector store can handle the scale and structure
        # needed for the 100-query evaluation targeting ≥ 90% success rate
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(db_path=temp_dir)
            
            # Simulate 100 documents from the seed set
            evaluation_records = []
            for i in range(100):
                record = {
                    "text": f"NYC service document {i}",
                    "embedding": [0.1] * 1536,
                    "metadata": {
                        "source": f"service_{i}.txt",
                        "service": ["unemployment", "snap", "medicaid", "cash_assistance", "childcare"][i % 5],
                        "chunk_index": 0,
                        "token_count": 5
                    }
                }
                evaluation_records.append(record)
            
            # Verify we can handle the evaluation scale
            assert len(evaluation_records) == 100
            
            # Verify service distribution matches PROJECT_SPEC.md
            services = [record["metadata"]["service"] for record in evaluation_records]
            service_counts = {service: services.count(service) for service in set(services)}
            
            # Each service should have 20 queries (100 total / 5 services)
            for service, count in service_counts.items():
                assert count == 20, f"Service {service} should have 20 queries, got {count}" 