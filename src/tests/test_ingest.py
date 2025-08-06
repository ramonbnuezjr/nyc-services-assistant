"""
Unit tests for NYC Services GPT ingest module
TODO: implement comprehensive testing for document chunking to support Self-Service Success Rate ≥ 90% as specified in PROJECT_SPEC.md
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the chunker module
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingest.chunker import chunk_documents, count_tokens, validate_chunks, simple_tokenize

class TestChunker:
    """Test cases for document chunking functionality"""
    
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
    
    def test_chunk_documents_large_doc(self):
        """Test chunking with a document larger than chunk size"""
        # Create a document with 1500 words (larger than chunk size of 1000)
        large_doc = "word " * 1500  # 1500 words
        
        chunks = chunk_documents([large_doc], chunk_size=1000, overlap=200)
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be within token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 1000
    
    def test_chunk_documents_overlap(self):
        """Test that chunks have proper overlap"""
        # Create a document that will be split into multiple chunks
        doc = "word " * 1200  # 1200 words
        
        chunks = chunk_documents([doc], chunk_size=1000, overlap=200)
        
        # Should have at least 2 chunks
        assert len(chunks) >= 2
        
        # Check that chunks don't exceed token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 1000
    
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
        
        # Document exactly at chunk size
        exact_doc = "word " * 999 + "final"  # 1000 words
        chunks = chunk_documents([exact_doc], chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert count_tokens(chunks[0]) == 1000
    
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
    
    @patch('builtins.open', create=True)
    def test_chunk_documents_file_path(self, mock_open):
        """Test chunking with file paths"""
        # Mock file content
        mock_file = MagicMock()
        mock_file.read.return_value = "How do I apply for unemployment benefits in NYC?"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock Path.exists to return True
        with patch('pathlib.Path.exists', return_value=True):
            chunks = chunk_documents(["fake_file.txt"], chunk_size=1000, overlap=200)
            
            assert len(chunks) == 1
            assert chunks[0] == "How do I apply for unemployment benefits in NYC?"
    
    def test_chunk_documents_mixed_input(self):
        """Test chunking with mixed string and file path inputs"""
        docs = [
            "Direct string document",
            "fake_file.txt"  # Will be treated as string since file doesn't exist
        ]
        
        chunks = chunk_documents(docs, chunk_size=1000, overlap=200)
        
        # Should return 2 chunks
        assert len(chunks) == 2
        assert chunks[0] == "Direct string document"
        assert chunks[1] == "fake_file.txt"
    
    def test_chunk_documents_nyc_services_example(self):
        """Test with realistic NYC services content"""
        nyc_docs = [
            "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website. You will need to provide personal information including your Social Security number, employment history, and reason for separation from your job.",
            "What documents are required for SNAP benefits? You will need proof of identity, income, expenses, and household composition. This includes pay stubs, bank statements, rent receipts, and utility bills."
        ]
        
        chunks = chunk_documents(nyc_docs, chunk_size=50, overlap=10)
        
        # Should create multiple chunks due to small chunk size
        assert len(chunks) > 2
        
        # All chunks should be within token limit
        for chunk in chunks:
            token_count = count_tokens(chunk)
            assert token_count <= 50

if __name__ == "__main__":
    pytest.main([__file__]) 