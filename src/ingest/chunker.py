"""
Document Chunker for NYC Services GPT RAG System
TODO: implement document chunking to support Self-Service Success Rate ≥ 90% as specified in PROJECT_SPEC.md

This module handles chunking of NYC service documents for the RAG pipeline.
Supports 100 synthetic queries across 5 NYC services (Unemployment, SNAP, Medicaid, Cash Assistance, Child Care).
"""

import re
from typing import List, Union
from pathlib import Path

def simple_tokenize(text: str) -> List[str]:
    """
    Simple tokenizer that splits text on whitespace.
    Used for token counting in chunking operations.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tokens
    """
    return text.split()

def count_tokens(text: str) -> int:
    """
    Count tokens in text using simple whitespace splitting.
    
    Args:
        text: Input text
        
    Returns:
        Number of tokens
    """
    return len(simple_tokenize(text))

def chunk_documents(docs: List[str], chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split documents into chunks of specified size with overlap.
    
    Designed for NYC Services GPT RAG system to achieve ≥ 90% Self-Service Success Rate.
    Processes documents for 5 key NYC services: Unemployment, SNAP, Medicaid, Cash Assistance, Child Care.
    
    Args:
        docs: List of document strings or file paths to chunk
        chunk_size: Maximum tokens per chunk (default: 1000)
        overlap: Number of overlapping tokens between chunks (default: 200)
        
    Returns:
        List of text chunks, each containing up to chunk_size tokens
        
    Example:
        >>> docs = ["How do I apply for unemployment benefits in NYC?", "What documents are required?"]
        >>> chunks = chunk_documents(docs, chunk_size=10, overlap=2)
        >>> len(chunks)  # Number of chunks
        >>> all(len(simple_tokenize(chunk)) <= 10 for chunk in chunks)  # No chunk exceeds limit
    """
    all_chunks = []
    
    for doc in docs:
        # Handle file paths - only check if it looks like a reasonable file path
        if isinstance(doc, str) and len(doc) < 255 and ('/' in doc or '.' in doc) and Path(doc).exists():
            with open(doc, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = str(doc)
        
        # Tokenize the document
        tokens = simple_tokenize(text)
        
        if len(tokens) <= chunk_size:
            # Document fits in one chunk
            all_chunks.append(text)
        else:
            # Split into overlapping chunks
            start = 0
            while start < len(tokens):
                end = min(start + chunk_size, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = ' '.join(chunk_tokens)
                all_chunks.append(chunk_text)
                
                # Move start position, accounting for overlap
                start = end - overlap
                if start >= len(tokens):
                    break
    
    return all_chunks

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split a single text string into chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum tokens per chunk (default: 1000)
        overlap: Number of overlapping tokens between chunks (default: 200)
        
    Returns:
        List of text chunks
    """
    return chunk_documents([text], chunk_size, overlap)

def validate_chunks(chunks: List[str], max_tokens: int = 1000) -> bool:
    """
    Validate that all chunks are within token limits.
    
    Args:
        chunks: List of text chunks to validate
        max_tokens: Maximum allowed tokens per chunk
        
    Returns:
        True if all chunks are within limits, False otherwise
    """
    for chunk in chunks:
        token_count = count_tokens(chunk)
        if token_count > max_tokens:
            return False
    return True 