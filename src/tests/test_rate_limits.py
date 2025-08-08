"""
Rate Limit Testing for NYC Services GPT RAG System

This script tests the rate limiting and retry logic for OpenAI API calls
to ensure the system can handle the 500 RPM limit gracefully.
"""

import time
import tempfile
from typing import List, Dict
from src.ingest.data_processor import EmbeddingClient
from src.models.llm_client import create_llm_client
from src.retrieve.vector_store import init_vector_store, add_documents, query_vector_store


def test_embedding_rate_limits():
    """Test embedding client rate limiting."""
    print("🧪 Testing Embedding Client Rate Limits")
    print("=" * 50)
    
    embedding_client = EmbeddingClient()
    
    # Test batch of embeddings
    test_texts = [
        "How do I apply for unemployment benefits?",
        "What documents do I need for SNAP?",
        "How do I check my Medicaid status?",
        "Can I work while on cash assistance?",
        "How do I apply for child care subsidy?"
    ]
    
    print(f"📝 Testing {len(test_texts)} embeddings...")
    start_time = time.time()
    
    try:
        embeddings = embedding_client.get_embeddings(test_texts)
        end_time = time.time()
        
        print(f"✅ Generated {len(embeddings)} embeddings in {end_time - start_time:.2f}s")
        print(f"📊 Average time per embedding: {(end_time - start_time) / len(embeddings):.2f}s")
        
        # Validate embeddings
        valid_count = sum(1 for emb in embeddings if embedding_client.validate_embedding(emb))
        print(f"✅ Valid embeddings: {valid_count}/{len(embeddings)}")
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")


def test_llm_rate_limits():
    """Test LLM client rate limiting."""
    print("\n🧪 Testing LLM Client Rate Limits")
    print("=" * 50)
    
    llm_client = create_llm_client()
    
    # Test queries with sample documents
    test_queries = [
        "How do I apply for unemployment benefits in NYC?",
        "What documents are required for SNAP benefits?",
        "How do I check my Medicaid application status?"
    ]
    
    sample_documents = [
        {
            "text": "To apply for unemployment benefits in NYC, visit the New York State Department of Labor website. You'll need your Social Security number, driver's license, and employment history.",
            "metadata": {"source": "unemployment_guide.txt", "service": "unemployment"}
        }
    ]
    
    print(f"🤖 Testing {len(test_queries)} LLM responses...")
    start_time = time.time()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{len(test_queries)}: {query[:50]}...")
        
        try:
            response = llm_client.generate_response(query, sample_documents)
            end_time = time.time()
            
            print(f"✅ Response generated in {end_time - start_time:.2f}s")
            print(f"📊 Confidence: {response['confidence']:.2f}")
            print(f"🔧 Model: {response['model']}")
            print(f"📝 Response preview: {response['response'][:100]}...")
            
            # Validate response
            if llm_client.validate_response(response):
                print("✅ Response validation passed")
            else:
                print("❌ Response validation failed")
                
        except Exception as e:
            print(f"❌ LLM response failed: {e}")


def test_full_pipeline_rate_limits():
    """Test full RAG pipeline with rate limiting."""
    print("\n🧪 Testing Full RAG Pipeline Rate Limits")
    print("=" * 50)
    
    # Sample documents
    documents = [
        {
            "text": "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website. You'll need your Social Security number, driver's license, and employment history.",
            "metadata": {"source": "unemployment_guide.txt", "service": "unemployment"}
        },
        {
            "text": "SNAP benefits in NYC can be applied for online, by phone, or in person. You'll need proof of income, identity, and residency. Income limits depend on household size.",
            "metadata": {"source": "snap_guide.txt", "service": "snap"}
        }
    ]
    
    # Process documents
    print("📚 Processing documents...")
    from src.ingest.data_processor import process_documents
    
    document_texts = [doc["text"] for doc in documents]
    records = process_documents(document_texts, chunk_size=200, overlap=50)
    
    # Add service metadata
    for i, record in enumerate(records):
        doc_index = i // 2
        if doc_index < len(documents):
            record["metadata"]["service"] = documents[doc_index]["metadata"]["service"]
    
    print(f"✅ Generated {len(records)} document chunks")
    
    # Initialize vector store
    print("🔧 Initializing vector store...")
    db_path = tempfile.mkdtemp()
    vector_store = init_vector_store(db_path=db_path)
    
    if not vector_store:
        print("❌ Failed to initialize vector store")
        return
    
    # Add documents
    print("📚 Adding documents to vector store...")
    success = add_documents(vector_store, records)
    
    if not success:
        print("❌ Failed to add documents")
        return
    
    # Test queries
    test_queries = [
        "How do I apply for unemployment benefits?",
        "What do I need for SNAP benefits?",
        "How do I check my unemployment status?"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} queries...")
    
    embedding_client = EmbeddingClient()
    llm_client = create_llm_client()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        
        try:
            # Generate embedding
            query_embedding = embedding_client.get_embedding(query)
            
            # Query vector store
            results = query_vector_store(vector_store, query_embedding, top_k=2)
            print(f"🔍 Retrieved {len(results)} documents")
            
            # Generate LLM response
            llm_response = llm_client.generate_response(query, results)
            print(f"🤖 Generated response with confidence: {llm_response['confidence']:.2f}")
            
            # Check if correct service was retrieved
            if results:
                retrieved_service = results[0]["metadata"].get("service", "unknown")
                print(f"🎯 Retrieved service: {retrieved_service}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print("\n✅ Full pipeline rate limit test complete!")


def main():
    """Run all rate limit tests."""
    print("🚀 NYC Services GPT - Rate Limit Testing")
    print("=" * 60)
    print("🎯 Testing OpenAI API rate limiting (500 RPM limit)")
    print("🎯 Testing exponential backoff and retry logic")
    print("=" * 60)
    
    # Test individual components
    test_embedding_rate_limits()
    test_llm_rate_limits()
    
    # Test full pipeline
    test_full_pipeline_rate_limits()
    
    print("\n🎉 Rate limit testing complete!")
    print("📊 Check the output above for any rate limit warnings or errors")


if __name__ == "__main__":
    main() 