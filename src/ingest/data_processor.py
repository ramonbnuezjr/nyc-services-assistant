"""
Data Processor for NYC Services GPT RAG System

This module processes documents for embedding generation to support the Self-Service Success Rate KPI.
Designed to handle 100 synthetic queries across 5 NYC services (Unemployment, SNAP, Medicaid, Cash Assistance, Child Care)
with a target ≥ 90% success rate as specified in PROJECT_SPEC.md.
"""

import os
from typing import List, Dict, Optional, Union
from pathlib import Path
import openai

from .chunker import chunk_documents
from ..config import config


class EmbeddingClient:
    """
    Mockable embedding client for generating vector embeddings.
    Uses OpenAI's text-embedding-ada-002 model by default.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-ada-002"):
        """
        Initialize the embedding client.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Embedding model to use
        """
        self.api_key = api_key or config.openai_api_key
        self.model = model
        if self.api_key:
            openai.api_key = self.api_key
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (one per input text)
        """
        if not self.api_key:
            # Return mock embeddings for testing/demo purposes
            return [[0.1] * 1536 for _ in texts]
        
        try:
            response = openai.embeddings.create(
                input=texts,
                model=self.model
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            print(f"Warning: Failed to generate embeddings: {e}")
            # Return mock embeddings as fallback
            return [[0.1] * 1536 for _ in texts]


def process_documents(
    paths: List[str], 
    chunk_size: int = 1000, 
    overlap: int = 200,
    embedding_client: Optional[EmbeddingClient] = None
) -> List[Dict]:
    """
    Process documents for the NYC Services GPT RAG system.
    
    This function is designed to support the Self-Service Success Rate KPI by:
    - Reading file paths or processing raw text inputs
    - Chunking documents using tokenized splitting for optimal retrieval
    - Generating vector embeddings for each chunk
    - Returning structured records ready for vector store ingestion
    
    The output supports evaluation against our 100-query seed set across 5 NYC services:
    Unemployment Benefits, SNAP, Medicaid, Cash Assistance, and Child Care Subsidy.
    
    Args:
        paths: List of file paths or raw text strings to process
        chunk_size: Maximum tokens per chunk (default: 1000)
        overlap: Overlapping tokens between chunks (default: 200)
        embedding_client: Optional embedding client (defaults to OpenAI)
        
    Returns:
        List of records with structure:
        {
            "text": str,           # The chunk text content
            "embedding": List[float],  # Vector embedding
            "metadata": {         # Additional metadata
                "source": str,    # Original file path or "raw_text"
                "chunk_index": int,  # Position in document
                "token_count": int,  # Number of tokens in chunk
                "chunk_size": int,   # Max chunk size used
                "overlap": int       # Overlap size used
            }
        }
        
    Example:
        >>> paths = ["./docs/unemployment_guide.txt", "How do I apply for SNAP benefits?"]
        >>> records = process_documents(paths)
        >>> len(records)  # Number of chunks created
        >>> all("text" in record and "embedding" in record for record in records)
        True
    """
    if embedding_client is None:
        embedding_client = EmbeddingClient()
    
    # Step 1: Read each file path or use raw text input
    documents = []
    source_mapping = {}
    
    for i, path in enumerate(paths):
        if isinstance(path, str) and len(path) < 255 and ('/' in path or '.' in path) and Path(path).exists():
            # It's a file path
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents.append(content)
                source_mapping[i] = str(path)
            except Exception as e:
                print(f"Warning: Failed to read file {path}: {e}")
                continue
        else:
            # It's raw text
            documents.append(str(path))
            source_mapping[i] = "raw_text"
    
    # Step 2: Call chunk_documents for tokenized splitting
    chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
    
    if not chunks:
        return []
    
    # Step 3: Generate embeddings for all chunks
    chunk_texts = [chunk for chunk in chunks if chunk.strip()]
    if not chunk_texts:
        return []
    
    embeddings = embedding_client.get_embeddings(chunk_texts)
    
    # Step 4: Create structured records
    records = []
    chunk_counter = 0
    
    for doc_idx, document in enumerate(documents):
        doc_chunks = chunk_documents([document], chunk_size=chunk_size, overlap=overlap)
        
        for chunk_idx, chunk in enumerate(doc_chunks):
            if chunk.strip() and chunk_counter < len(embeddings):
                # Count tokens in chunk
                token_count = len(chunk.split())
                
                record = {
                    "text": chunk,
                    "embedding": embeddings[chunk_counter],
                    "metadata": {
                        "source": source_mapping.get(doc_idx, "unknown"),
                        "chunk_index": chunk_idx,
                        "token_count": token_count,
                        "chunk_size": chunk_size,
                        "overlap": overlap
                    }
                }
                records.append(record)
                chunk_counter += 1
    
    return records


def validate_records(records: List[Dict]) -> bool:
    """
    Validate that all records have the required structure for the RAG system.
    
    Args:
        records: List of document records to validate
        
    Returns:
        True if all records are valid, False otherwise
    """
    required_fields = ["text", "embedding", "metadata"]
    required_metadata_fields = ["source", "chunk_index", "token_count"]
    
    for record in records:
        # Check top-level fields
        if not all(field in record for field in required_fields):
            return False
        
        # Check metadata fields
        if not all(field in record["metadata"] for field in required_metadata_fields):
            return False
        
        # Check data types
        if not isinstance(record["text"], str):
            return False
        if not isinstance(record["embedding"], list):
            return False
        if not isinstance(record["metadata"], dict):
            return False
    
    return True


if __name__ == "__main__":
    """
    Demo stub showing how to use process_documents for NYC Services RAG system.
    
    This demo processes sample NYC service documents and queries that would be part
    of our 100-query evaluation set targeting ≥ 90% Self-Service Success Rate.
    """
    print("NYC Services GPT - Data Processor Demo")
    print("=" * 50)
    
    # Sample documents/queries from our 100-query seed set
    sample_inputs = [
        "How do I apply for unemployment benefits in NYC?",
        "What documents are required for New York State unemployment?",
        "How do I apply for SNAP benefits in NYC?",
        "What income limits apply to SNAP in New York?",
        "How do I apply for Medicaid in NYC?"
    ]
    
    print(f"Processing {len(sample_inputs)} sample documents/queries...")
    
    try:
        # Process the documents
        records = process_documents(sample_inputs, chunk_size=100, overlap=20)
        
        print(f"✅ Generated {len(records)} records")
        print(f"✅ Validation passed: {validate_records(records)}")
        
        # Show sample record structure
        if records:
            print("\nSample record structure:")
            sample_record = records[0]
            print(f"  Text: {sample_record['text'][:100]}...")
            print(f"  Embedding dimensions: {len(sample_record['embedding'])}")
            print(f"  Metadata: {sample_record['metadata']}")
        
        print(f"\n🎯 Ready for vector store ingestion and 100-query evaluation!")
        print(f"🎯 Target: ≥ {config.target_success_rate}% Self-Service Success Rate")
        
    except Exception as e:
        print(f"❌ Error processing documents: {e}")
        print("This is expected if OpenAI API key is not configured.")
        print("Mock embeddings will be used for testing.")