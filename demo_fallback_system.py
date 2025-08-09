#!/usr/bin/env python3
"""
Demonstration of the Automatic Mock Fallback System

This script demonstrates how the NYC Services GPT MVP automatically switches to
intelligent mock responses when rate limits or budget limits are hit, ensuring
the system never crashes and you can keep iterating without extra API costs.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.llm_client import LLMClient
from src.ingest.data_processor import EmbeddingClient
from src.models.rate_limiter import rate_limiter
from src.models.mock_fallback import mock_fallback

def demo_budget_protection():
    """Demonstrate automatic fallback when budget limits are hit."""
    print("🔧 Demo: Budget Protection with Automatic Fallback")
    print("=" * 60)
    
    # Simulate hitting budget limit by setting very low limits
    original_daily = rate_limiter.daily_budget
    original_monthly = rate_limiter.monthly_budget
    
    # Set extremely low budgets to trigger fallback
    rate_limiter.daily_budget = 10  # 10 tokens
    rate_limiter.monthly_budget = 100  # 100 tokens
    
    print(f"📊 Set low budget limits for demo:")
    print(f"   Daily: {rate_limiter.daily_budget} tokens")
    print(f"   Monthly: {rate_limiter.monthly_budget} tokens")
    print()
    
    # Try to make a request that exceeds budget
    client = LLMClient()
    query = "How do I apply for unemployment benefits in NYC?"
    documents = [
        {
            "text": "To apply for unemployment benefits, visit the NY Department of Labor website.",
            "metadata": {"source": "test_doc", "service": "unemployment"}
        }
    ]
    
    print(f"🔍 Testing query: {query}")
    print("💡 This should trigger budget protection and activate mock fallback...")
    print()
    
    response = client.generate_response(query, documents, max_tokens=200)
    
    print("📋 Response Details:")
    print(f"   Model used: {response.get('model', 'unknown')}")
    print(f"   Response length: {len(response.get('response', ''))}")
    print(f"   Fallback reason: {response.get('fallback_reason', 'N/A')}")
    print(f"   Tokens used: {response.get('tokens_used', 0)}")
    print()
    
    # Show fallback status
    status = mock_fallback.get_status_info()
    print("🔄 Fallback Status:")
    print(f"   Active: {status['fallback_active']}")
    print(f"   Reason: {status['fallback_reason']}")
    print(f"   Mock responses generated: {status['fallback_count']}")
    print()
    
    # Show that system continues working
    print("✅ System continues working normally with mock responses!")
    print("💰 Zero additional API costs incurred!")
    
    # Restore original budgets
    rate_limiter.daily_budget = original_daily
    rate_limiter.monthly_budget = original_monthly
    mock_fallback.deactivate_fallback()
    print()

def demo_rate_limit_protection():
    """Demonstrate automatic fallback when rate limits are hit."""
    print("🔧 Demo: Rate Limit Protection with Intelligent Mocks")
    print("=" * 60)
    
    # The system is already hitting rate limits, so let's show the fallback
    client = EmbeddingClient()
    
    texts = [
        "How do I apply for SNAP benefits in NYC?",
        "What documents do I need for Medicaid?",
        "How do I check my cash assistance status?"
    ]
    
    print(f"🔍 Testing embedding generation for {len(texts)} texts:")
    for i, text in enumerate(texts, 1):
        print(f"   {i}. {text}")
    print()
    
    print("💡 This will likely hit rate limits and activate mock fallback...")
    print()
    
    embeddings = client.get_embeddings(texts)
    
    print("📋 Embedding Results:")
    print(f"   Generated embeddings: {len(embeddings)}")
    if embeddings and embeddings[0]:
        print(f"   Embedding dimensions: {len(embeddings[0])}")
        print(f"   First embedding sample: [{embeddings[0][0]:.3f}, {embeddings[0][1]:.3f}, ...]")
    print()
    
    # Show fallback status
    status = mock_fallback.get_status_info()
    print("🔄 Fallback Status:")
    print(f"   Active: {status['fallback_active']}")
    print(f"   Reason: {status['fallback_reason']}")
    print(f"   Mock responses generated: {status['fallback_count']}")
    print()
    
    print("✅ Embeddings generated successfully (mock or real)!")
    print("🔄 System never crashed, evaluation can continue!")
    print()

def demo_service_aware_responses():
    """Demonstrate service-aware mock responses."""
    print("🔧 Demo: Service-Aware Intelligent Mock Responses")
    print("=" * 60)
    
    # Force fallback mode for demonstration
    mock_fallback.activate_fallback("demo_mode")
    
    client = LLMClient()
    
    # Test different service queries
    test_cases = [
        {
            "query": "How do I apply for unemployment benefits?",
            "service": "unemployment",
            "docs": [{"metadata": {"service": "unemployment"}}]
        },
        {
            "query": "What documents do I need for SNAP?",
            "service": "snap", 
            "docs": [{"metadata": {"service": "snap"}}]
        },
        {
            "query": "How do I renew my Medicaid coverage?",
            "service": "medicaid",
            "docs": [{"metadata": {"service": "medicaid"}}]
        },
        {
            "query": "Can I work while receiving cash assistance?",
            "service": "cash_assistance",
            "docs": [{"metadata": {"service": "cash_assistance"}}]
        },
        {
            "query": "How do I find approved daycare providers?",
            "service": "childcare",
            "docs": [{"metadata": {"service": "childcare"}}]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['service'].upper()}")
        print(f"   Query: {test_case['query']}")
        
        response = client.generate_response(
            test_case['query'], 
            test_case['docs'], 
            max_tokens=150
        )
        
        print(f"   Model: {response.get('model', 'unknown')}")
        print(f"   Response: {response.get('response', '')[:100]}...")
        print(f"   Confidence: {response.get('confidence', 0)}")
        print()
    
    # Deactivate fallback
    mock_fallback.deactivate_fallback()
    print("✅ All services handled intelligently with appropriate mock responses!")
    print("🎯 Maintains evaluation compatibility and system flow!")
    print()

def demo_continuous_operation():
    """Demonstrate continuous operation during rate limit issues."""
    print("🔧 Demo: Continuous Operation During Rate Limit Issues")
    print("=" * 60)
    
    print("💡 Simulating a full evaluation run with rate limit protection...")
    print()
    
    # Simulate running multiple queries like in baseline evaluation
    queries = [
        "How do I apply for unemployment benefits in NYC?",
        "What income limits apply to SNAP in New York?", 
        "How do I check my Medicaid application status?",
        "What documents are needed for a cash assistance interview?",
        "How do I find approved daycare providers?",
        "Can I work part-time while receiving unemployment?",
        "How do I report a change in household size for SNAP?",
        "What happens if I miss my Medicaid renewal deadline?",
        "How long does cash assistance approval take?",
        "What co-payments apply for child care subsidies?"
    ]
    
    client = LLMClient()
    successful_responses = 0
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i:2d}/10: {query[:50]}...")
        
        # Mock documents for the query
        docs = [{"text": "Mock document content", "metadata": {"source": "test"}}]
        
        try:
            response = client.generate_response(query, docs, max_tokens=100)
            
            if response and response.get('response'):
                successful_responses += 1
                status = "✅ Success"
                if 'fallback' in response.get('model', ''):
                    status += " (Mock)"
            else:
                status = "❌ Failed"
                
        except Exception as e:
            status = f"❌ Error: {str(e)[:30]}"
        
        print(f"         Result: {status}")
    
    print()
    print(f"📊 Results Summary:")
    print(f"   Total queries: {len(queries)}")
    print(f"   Successful responses: {successful_responses}")
    print(f"   Success rate: {(successful_responses/len(queries)*100):.1f}%")
    print()
    
    # Show final fallback status
    status = mock_fallback.get_status_info()
    print("🔄 Final Fallback Status:")
    print(f"   Active: {status['fallback_active']}")
    print(f"   Total mock responses: {status['fallback_count']}")
    print()
    
    print("✅ System maintained operation throughout!")
    print("🎯 Evaluation could continue without interruption!")
    print("💰 API costs minimized through intelligent fallbacks!")

if __name__ == "__main__":
    print("🚀 NYC Services GPT - Automatic Mock Fallback System Demo")
    print("=" * 70)
    print("💡 This demo shows how the system automatically switches to intelligent")
    print("   mock responses when rate limits or budgets are hit, ensuring the")
    print("   MVP never crashes and you can keep iterating without extra costs.")
    print()
    
    try:
        # Run all demonstrations
        demo_budget_protection()
        demo_rate_limit_protection() 
        demo_service_aware_responses()
        demo_continuous_operation()
        
        print("🎉 All fallback system demos completed successfully!")
        print()
        print("💡 Key Benefits:")
        print("   ✅ System never crashes from rate limits or budget overruns")
        print("   ✅ Intelligent service-aware mock responses maintain quality")
        print("   ✅ Zero additional API costs when fallback is active")
        print("   ✅ Evaluation and development can continue uninterrupted")
        print("   ✅ Automatic reactivation when API access is restored")
        print()
        print("🚀 Your MVP is now bulletproof against API limitations!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
