"""
Simplified unit tests for NYC Services GPT chunker module
Tests core functionality without memory-intensive operations
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the chunker module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingest.chunker import chunk_documents, count_tokens, validate_chunks, simple_tokenize

class TestChunkerSimple:
    """Simplified test cases for document chunking functionality"""
    
    def test_simple_tokenize(self):
        """Test simple tokenization on whitespace"""
        text = "How do I apply for unemployment benefits in NYC?"
        tokens = simple_tokenize(text)
        expected = ["How", "do", "I", "apply", "for", "unemployment", "benefits", "in", "NYC?"]
        assert tokens == expected
    
    def test_count_tokens(self):
        """Test token counting"""
        text = "What documents are required for New York State unemployment?"
        token_count = count_tokens(text)
        assert token_count == 9  # 9 words
    
    def test_chunk_documents_small_docs(self):
        """Test chunking with documents smaller than chunk size"""
        docs = [
            "How do I apply for unemployment benefits in NYC?",
            "What documents are required for New York State unemployment?"
        ]
        
        chunks = chunk_documents(docs, chunk_size=1000, overlap=200)
        
        # Should return 2 chunks (one per document)
        assert len(chunks) == 2
        
        # Each chunk should be within token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 1000
    
    def test_chunk_documents_with_overlap(self):
        """Test chunking with overlap using smaller document"""
        # Create a document that will be split into multiple chunks
        doc = "word " * 150  # 150 words
        
        chunks = chunk_documents([doc], chunk_size=100, overlap=20)
        
        # Should have at least 2 chunks
        assert len(chunks) >= 2
        
        # Check that chunks don't exceed token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 100
    
    def test_chunk_documents_edge_cases(self):
        """Test edge cases for chunking"""
        # Empty document
        chunks = chunk_documents([""], chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert chunks[0] == ""
        
        # Single word document
        chunks = chunk_documents(["hello"], chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert chunks[0] == "hello"
    
    def test_validate_chunks(self):
        """Test chunk validation"""
        valid_chunks = [
            "short chunk",
            "another short chunk",
            "third short chunk"
        ]
        assert validate_chunks(valid_chunks, max_tokens=1000) == True
        
        # Create an invalid chunk (too many tokens)
        invalid_chunks = [
            "short chunk",
            "word " * 1001,  # 1001 words
            "another short chunk"
        ]
        assert validate_chunks(invalid_chunks, max_tokens=1000) == False
    
    def test_chunk_documents_nyc_services_example(self):
        """Test with realistic NYC services content"""
        nyc_docs = [
            "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website.",
            "What documents are required for SNAP benefits? You will need proof of identity, income, expenses, and household composition."
        ]
        
        chunks = chunk_documents(nyc_docs, chunk_size=20, overlap=5)
        
        # Should create multiple chunks due to small chunk size
        assert len(chunks) > 2
        
        # All chunks should be within token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 20

if __name__ == "__main__":
    pytest.main([__file__]) 