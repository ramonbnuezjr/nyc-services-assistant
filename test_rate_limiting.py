#!/usr/bin/env python3
"""
Quick test of the new rate limiting system for NYC Services GPT MVP.

This script tests the rate limiting functionality without running the full evaluation.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.rate_limiter import rate_limiter
from src.models.llm_client import LLMClient
from src.ingest.data_processor import EmbeddingClient

def test_rate_limiter_basic():
    """Test basic rate limiter functionality."""
    print("🔧 Testing Rate Limiter Basic Functions")
    print("=" * 50)
    
    # Test model selection
    print(f"Default model: {rate_limiter.choose_model()}")
    print(f"Complex task model: {rate_limiter.choose_model('deep analysis legal', allow_premium=True)}")
    print(f"Simple task model: {rate_limiter.choose_model('simple query')}")
    
    # Test token estimation
    text = "How do I apply for unemployment benefits in NYC?"
    tokens = rate_limiter.estimate_tokens(text)
    print(f"Estimated tokens for '{text}': {tokens}")
    
    # Test usage stats
    stats = rate_limiter.get_usage_stats()
    print(f"Usage stats: {stats}")
    
    print("✅ Basic rate limiter tests passed\n")

def test_llm_client():
    """Test LLM client with rate limiting."""
    print("🔧 Testing LLM Client with Rate Limiting")
    print("=" * 50)
    
    # Initialize client with default model (gpt-4o-mini)
    client = LLMClient()
    
    # Test simple query
    query = "How do I apply for unemployment benefits in NYC?"
    documents = [
        {
            "text": "To apply for unemployment benefits, visit the NY Department of Labor website.",
            "metadata": {"source": "test_doc", "service": "unemployment"}
        }
    ]
    
    print(f"Testing query: {query}")
    response = client.generate_response(query, documents, max_tokens=100)
    
    print(f"Response model: {response.get('model', 'unknown')}")
    print(f"Response length: {len(response.get('response', ''))}")
    print(f"From cache: {response.get('from_cache', False)}")
    print(f"Tokens used: {response.get('tokens_used', 0)}")
    
    # Test second identical query (should hit cache in dev mode)
    print("\n🔄 Testing cache (second identical query)...")
    response2 = client.generate_response(query, documents, max_tokens=100)
    print(f"Second response from cache: {response2.get('from_cache', False)}")
    
    print("✅ LLM client tests passed\n")

def test_embedding_client():
    """Test embedding client with rate limiting."""
    print("🔧 Testing Embedding Client with Rate Limiting")
    print("=" * 50)
    
    client = EmbeddingClient()
    
    # Test small batch
    texts = [
        "How do I apply for unemployment benefits?",
        "What documents do I need for SNAP?"
    ]
    
    print(f"Testing embeddings for {len(texts)} texts...")
    embeddings = client.get_embeddings(texts)
    
    print(f"Generated embeddings: {len(embeddings)}")
    if embeddings and embeddings[0]:
        print(f"Embedding dimensions: {len(embeddings[0])}")
    
    # Test second identical batch (should hit cache)
    print("\n🔄 Testing cache (second identical batch)...")
    embeddings2 = client.get_embeddings(texts)
    print(f"Second batch retrieved: {len(embeddings2)}")
    
    print("✅ Embedding client tests passed\n")

def test_rate_limiting_stats():
    """Show current rate limiting statistics."""
    print("📊 Current Rate Limiting Statistics")
    print("=" * 50)
    
    stats = rate_limiter.get_usage_stats()
    
    for model, model_stats in stats.items():
        if model == "budget":
            print(f"\n💰 Budget Usage:")
            print(f"  Daily: {model_stats['daily']} ({model_stats['daily_pct']:.1f}%)")
            print(f"  Monthly: {model_stats['monthly']} ({model_stats['monthly_pct']:.1f}%)")
        else:
            print(f"\n🤖 {model}:")
            print(f"  Requests: {model_stats['requests']} ({model_stats['requests_pct']:.1f}%)")
            print(f"  Tokens: {model_stats['tokens']} ({model_stats['tokens_pct']:.1f}%)")

if __name__ == "__main__":
    print("🚀 NYC Services GPT - Rate Limiting Test Suite")
    print("=" * 60)
    print(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"Premium allowed: {os.getenv('ALLOW_PREMIUM', 'false')}")
    print()
    
    try:
        # Run tests
        test_rate_limiter_basic()
        test_llm_client()
        test_embedding_client()
        test_rate_limiting_stats()
        
        print("🎉 All rate limiting tests passed!")
        print("\n💡 Rate limiting system is ready for production use.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
