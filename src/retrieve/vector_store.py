"""
Vector Store for NYC Services GPT RAG System

This module provides a storage-agnostic interface for vector storage and retrieval,
designed to support the Self-Service Success Rate KPI by ensuring accurate document
retrieval for the 100-query evaluation set across 5 NYC services.

The interface is designed to be easily switchable between different vector stores
(ChromaDB, Weaviate, FAISS) without requiring changes to the RAG pipeline logic.
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings

from ..config import config


class VectorStore:
    """
    Storage-agnostic vector store interface for NYC Services GPT RAG system.
    
    Designed to support ≥ 90% Self-Service Success Rate by providing accurate
    document retrieval for the 100-query evaluation set across 5 NYC services:
    Unemployment Benefits, SNAP, Medicaid, Cash Assistance, and Child Care Subsidy.
    
    Currently implements ChromaDB backend but designed for easy migration to
    other vector stores (Weaviate, FAISS, etc.) without RAG pipeline changes.
    """
    
    def __init__(self, db_path: Optional[str] = None, collection_name: str = "nyc_services"):
        """
        Initialize vector store with configurable backend.
        
        Args:
            db_path: Path to vector database (defaults to config)
            collection_name: Name of document collection
        """
        self.db_path = db_path or config.vector_db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Ensure database directory exists
        Path(self.db_path).mkdir(parents=True, exist_ok=True)
    
    def init_vector_store(self) -> bool:
        """
        Initialize the vector store connection and collection.
        
        This function sets up the vector database for storing and retrieving
        NYC service documents. Accurate retrieval is critical for achieving
        the ≥ 90% Self-Service Success Rate KPI.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "NYC Services GPT RAG Collection",
                    "target_success_rate": config.target_success_rate,
                    "synthetic_query_count": config.synthetic_query_count
                }
            )
            
            print(f"✅ Vector store initialized at {self.db_path}")
            print(f"✅ Collection '{self.collection_name}' ready for NYC services documents")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize vector store: {e}")
            return False
    
    def add_documents(self, records: List[Dict]) -> bool:
        """
        Add document records to the vector store.
        
        Stores text chunks with their embeddings and metadata for retrieval.
        Document quality directly impacts the Self-Service Success Rate KPI
        by ensuring relevant content surfaces for user queries.
        
        Args:
            records: List of document records with structure:
                {
                    "text": str,
                    "embedding": List[float],
                    "metadata": Dict
                }
        
        Returns:
            True if documents added successfully, False otherwise
            
        Example:
            >>> records = [
            ...     {"text": "How to apply for unemployment", "embedding": [0.1, 0.2], "metadata": {"source": "unemployment.txt"}}
            ... ]
            >>> vector_store.add_documents(records)
            True
        """
        if not self.collection:
            print("❌ Vector store not initialized. Call init_vector_store() first.")
            return False
        
        if not records:
            print("⚠️ No records to add")
            return True
        
        try:
            # Prepare data for ChromaDB
            texts = [record["text"] for record in records]
            embeddings = [record["embedding"] for record in records]
            metadatas = [record["metadata"] for record in records]
            ids = [f"doc_{i}" for i in range(len(records))]
            
            # Add documents to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Added {len(records)} documents to vector store")
            print(f"📊 Total documents in collection: {self.collection.count()}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            return False
    
    def query_vector_store(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query the vector store for most relevant documents.
        
        This function is critical for the Self-Service Success Rate KPI as it
        determines which documents are retrieved for user queries. Accurate
        retrieval ensures users get relevant information without human intervention.
        
        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of most relevant documents to return (default: 5)
            filter_metadata: Optional metadata filters for targeted retrieval
            
        Returns:
            List of document records with structure:
            {
                "text": str,
                "metadata": Dict,
                "distance": float,
                "id": str
            }
            
        Example:
            >>> query_embedding = [0.1, 0.2, 0.3]
            >>> results = vector_store.query_vector_store(query_embedding, top_k=3)
            >>> len(results)  # Number of retrieved documents
            3
            >>> all("text" in result for result in results)  # All have text
            True
        """
        if not self.collection:
            print("❌ Vector store not initialized. Call init_vector_store() first.")
            return []
        
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    doc = {
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "id": results["ids"][0][i] if "ids" in results else f"result_{i}"
                    }
                    documents.append(doc)
            
            print(f"🔍 Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            print(f"❌ Failed to query vector store: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Useful for monitoring document coverage and ensuring adequate
        representation of NYC services for the 100-query evaluation.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            return {"error": "Vector store not initialized"}
        
        try:
            count = self.collection.count()
            
            # Get sample documents to analyze metadata
            sample_results = self.collection.query(
                query_embeddings=[[0.0] * 1536],  # Dummy embedding
                n_results=min(100, count)
            )
            
            # Analyze source distribution
            sources = {}
            if sample_results["metadatas"] and sample_results["metadatas"][0]:
                for metadata in sample_results["metadatas"][0]:
                    source = metadata.get("source", "unknown")
                    sources[source] = sources.get(source, 0) + 1
            
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "source_distribution": sources,
                "target_success_rate": config.target_success_rate,
                "synthetic_query_count": config.synthetic_query_count
            }
            
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Useful for testing and resetting the vector store.
        
        Returns:
            True if collection cleared successfully, False otherwise
        """
        if not self.collection:
            return False
        
        try:
            self.collection.delete(where={})
            print(f"🗑️ Cleared collection '{self.collection_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to clear collection: {e}")
            return False


def init_vector_store(db_path: Optional[str] = None, collection_name: str = "nyc_services") -> Optional[VectorStore]:
    """
    Initialize and return a vector store instance.
    
    Convenience function for creating a vector store with default settings.
    Designed to support the Self-Service Success Rate KPI by providing
    reliable document storage and retrieval capabilities.
    
    Args:
        db_path: Path to vector database (defaults to config)
        collection_name: Name of document collection
        
    Returns:
        Initialized VectorStore instance or None if initialization failed
    """
    vector_store = VectorStore(db_path, collection_name)
    if vector_store.init_vector_store():
        return vector_store
    return None


def add_documents(vector_store: VectorStore, records: List[Dict]) -> bool:
    """
    Add documents to the vector store.
    
    Convenience function for adding document records to a vector store.
    Document quality directly impacts retrieval accuracy and thus the
    Self-Service Success Rate KPI.
    
    Args:
        vector_store: Initialized VectorStore instance
        records: List of document records to add
        
    Returns:
        True if documents added successfully, False otherwise
    """
    return vector_store.add_documents(records)


def query_vector_store(
    vector_store: VectorStore, 
    query_embedding: List[float], 
    top_k: int = 5,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """
    Query the vector store for relevant documents.
    
    Convenience function for querying a vector store. Retrieval accuracy
    is critical for achieving the ≥ 90% Self-Service Success Rate KPI
    by ensuring users get relevant information without human intervention.
    
    Args:
        vector_store: Initialized VectorStore instance
        query_embedding: Vector embedding of the query
        top_k: Number of most relevant documents to return
        filter_metadata: Optional metadata filters
        
    Returns:
        List of relevant document records
    """
    return vector_store.query_vector_store(query_embedding, top_k, filter_metadata)


if __name__ == "__main__":
    """
    Demo stub showing how to use the vector store for NYC Services RAG system.
    
    This demo initializes a vector store, adds sample documents, and performs
    a test query to demonstrate the retrieval pipeline for the 100-query evaluation.
    """
    print("NYC Services GPT - Vector Store Demo")
    print("=" * 50)
    
    # Initialize vector store
    print("🔧 Initializing vector store...")
    vector_store = init_vector_store()
    
    if not vector_store:
        print("❌ Failed to initialize vector store")
        exit(1)
    
    # Sample documents from our 100-query seed set
    sample_records = [
        {
            "text": "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website.",
            "embedding": [0.1] * 1536,  # Mock embedding
            "metadata": {
                "source": "unemployment_guide.txt",
                "service": "unemployment",
                "chunk_index": 0,
                "token_count": 15
            }
        },
        {
            "text": "What documents are required for SNAP benefits? You need proof of income, identity, and residency.",
            "embedding": [0.2] * 1536,  # Mock embedding
            "metadata": {
                "source": "snap_requirements.txt",
                "service": "snap",
                "chunk_index": 0,
                "token_count": 12
            }
        },
        {
            "text": "Medicaid application process in NYC requires completing the application form and providing required documentation.",
            "embedding": [0.3] * 1536,  # Mock embedding
            "metadata": {
                "source": "medicaid_process.txt",
                "service": "medicaid",
                "chunk_index": 0,
                "token_count": 14
            }
        }
    ]
    
    # Add documents to vector store
    print(f"📚 Adding {len(sample_records)} sample documents...")
    success = add_documents(vector_store, sample_records)
    
    if not success:
        print("❌ Failed to add documents")
        exit(1)
    
    # Test query
    print("🔍 Testing query retrieval...")
    test_query_embedding = [0.15] * 1536  # Similar to unemployment doc
    results = query_vector_store(vector_store, test_query_embedding, top_k=2)
    
    print(f"✅ Retrieved {len(results)} documents")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['text'][:80]}...")
        print(f"     Distance: {result['distance']:.4f}")
        print(f"     Source: {result['metadata']['source']}")
    
    # Show collection stats
    stats = vector_store.get_collection_stats()
    print(f"\n📊 Collection Statistics:")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Target success rate: {stats['target_success_rate']}%")
    print(f"  Synthetic query count: {stats['synthetic_query_count']}")
    
    print(f"\n🎯 Ready for 100-query evaluation targeting ≥ {config.target_success_rate}% Self-Service Success Rate!") 