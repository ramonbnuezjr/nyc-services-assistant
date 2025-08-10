#!/usr/bin/env python3
"""
Test script for actual RAG prompting against ChromaDB data.

This script tests real queries through the complete RAG pipeline:
1. Query embedding generation
2. Vector store retrieval
3. LLM response generation
4. Response quality evaluation
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.retrieve.vector_store import init_vector_store, query_vector_store
from src.ingest.data_processor import EmbeddingClient
from src.models.llm_client import create_llm_client


def test_rag_prompting():
    """Test the RAG pipeline with real queries against ChromaDB data."""
    print("🚀 NYC Services GPT - RAG Prompting Test")
    print("=" * 50)
    
    # Initialize components
    print("🔧 Initializing RAG pipeline components...")
    
    # Initialize vector store
    vector_store = init_vector_store()
    if not vector_store:
        print("❌ Failed to initialize vector store")
        return
    
    print(f"✅ Vector store ready with {vector_store.collection.count()} documents")
    
    # Initialize embedding client
    embedding_client = EmbeddingClient()
    print("✅ Embedding client ready")
    
    # Initialize LLM client
    llm_client = create_llm_client()
    print("✅ LLM client ready")
    
    # Test queries covering different NYC services
    test_queries = [
        "How do I apply for unemployment benefits?",
        "What documents do I need for SNAP benefits?",
        "How do I apply for Medicaid?",
        "What are the eligibility requirements for unemployment?",
        "How do I check my SNAP benefits status?",
        "What is the application process for Medicaid?",
        "Where can I apply for unemployment in NYC?",
        "What income limits apply to SNAP benefits?",
        "How do I renew my Medicaid coverage?",
        "What happens if my unemployment claim is denied?"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} queries against ChromaDB data...")
    print("=" * 60)
    
    successful_queries = 0
    total_queries = len(test_queries)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{total_queries}: {query}")
        print("-" * 40)
        
        try:
            # Step 1: Generate query embedding
            print("🔧 Generating query embedding...")
            query_embedding = embedding_client.get_embedding(query)
            print(f"✅ Embedding generated: {len(query_embedding)} dimensions")
            
            # Step 2: Query vector store
            print("🔍 Querying vector store...")
            results = query_vector_store(vector_store, query_embedding, top_k=3)
            
            if not results:
                print("❌ No documents retrieved")
                continue
            
            print(f"✅ Retrieved {len(results)} documents")
            
            # Show retrieved documents
            for j, result in enumerate(results[:2]):  # Show first 2
                service_type = result["metadata"].get("service_type", "unknown")
                source = result["metadata"].get("filename", "unknown")
                distance = result["distance"]
                print(f"  📄 Doc {j+1}: {service_type} ({source}) - Distance: {distance:.3f}")
                print(f"     Preview: {result['text'][:150]}...")
            
            # Step 3: Generate LLM response
            print("🤖 Generating LLM response...")
            llm_response = llm_client.generate_response(query, results)
            
            if llm_response and "response" in llm_response:
                response_text = llm_response["response"]
                confidence = llm_response.get("confidence", 0.0)
                print(f"✅ Response generated (confidence: {confidence:.2f})")
                print(f"🤖 Response: {response_text[:200]}...")
                
                # Check if response is relevant
                if any(service in response_text.lower() for service in ["unemployment", "snap", "medicaid", "benefits", "apply"]):
                    print("✅ Response appears relevant to NYC services")
                    successful_queries += 1
                else:
                    print("⚠️ Response may not be relevant to NYC services")
            else:
                print("❌ Failed to generate LLM response")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        print()
    
    # Final results
    print("🎯 RAG Prompting Test Results")
    print("=" * 50)
    print(f"✅ Successful queries: {successful_queries}/{total_queries}")
    print(f"📊 Success rate: {(successful_queries/total_queries)*100:.1f}%")
    
    if successful_queries > 0:
        print("🎉 RAG pipeline is working with real data!")
    else:
        print("❌ RAG pipeline needs investigation")


def test_specific_service_queries():
    """Test queries specific to each service type."""
    print("\n🔍 Testing Service-Specific Queries")
    print("=" * 50)
    
    vector_store = init_vector_store()
    embedding_client = EmbeddingClient()
    llm_client = create_llm_client()
    
    service_queries = {
        "unemployment": [
            "How do I file for unemployment benefits?",
            "What documents do I need for unemployment?",
            "How long does unemployment last?"
        ],
        "snap": [
            "How do I apply for SNAP benefits?",
            "What is the income limit for SNAP?",
            "How do I check my SNAP balance?"
        ],
        "medicaid": [
            "How do I apply for Medicaid?",
            "What are Medicaid eligibility requirements?",
            "How do I renew my Medicaid?"
        ]
    }
    
    for service, queries in service_queries.items():
        print(f"\n🏥 Testing {service.upper()} queries:")
        print("-" * 30)
        
        for query in queries:
            try:
                # Generate embedding and query
                query_embedding = embedding_client.get_embedding(query)
                results = query_vector_store(vector_store, query_embedding, top_k=2)
                
                if results:
                    # Check if we got relevant results
                    relevant_results = [
                        r for r in results 
                        if service.lower() in r["metadata"].get("service_type", "").lower()
                    ]
                    
                    if relevant_results:
                        print(f"✅ {query} -> Found {len(relevant_results)} relevant results")
                    else:
                        print(f"⚠️ {query} -> Found results but not service-specific")
                else:
                    print(f"❌ {query} -> No results found")
                    
            except Exception as e:
                print(f"❌ {query} -> Error: {e}")


if __name__ == "__main__":
    try:
        test_rag_prompting()
        test_specific_service_queries()
        print("\n🎉 All RAG prompting tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
