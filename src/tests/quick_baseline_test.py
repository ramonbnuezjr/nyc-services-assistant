"""
Quick Baseline Test for NYC Services GPT RAG System

This script runs a quick baseline evaluation with just 10 queries
to test the rate limiting and retry logic in the full pipeline.
"""

import time
import tempfile
from typing import List, Dict
from src.tests.baseline_evaluation import BaselineEvaluator


def run_quick_baseline():
    """Run a quick baseline evaluation with 10 queries."""
    print("🚀 NYC Services GPT - Quick Baseline Test")
    print("=" * 60)
    print("🎯 Testing rate limiting with 10 queries")
    print("🎯 Target: ≥ 90.0% Self-Service Success Rate")
    print("=" * 60)
    
    # Create evaluator
    evaluator = BaselineEvaluator()
    
    # Take first 10 queries for quick test
    test_queries = evaluator.queries[:10]
    print(f"📝 Testing {len(test_queries)} queries...")
    
    # Set up pipeline
    if not evaluator.setup_pipeline():
        print("❌ Pipeline setup failed")
        return
    
    # Evaluate queries
    results = []
    start_time = time.time()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}/{len(test_queries)}: {query['text'][:50]}...")
        
        try:
            result = evaluator.evaluate_query(query)
            results.append(result)
            
            status = "✅ Success" if result["is_successful"] else "❌ Failed"
            print(f"  {status}")
            
            if result["is_successful"]:
                print(f"  📊 Confidence: {result['llm_response']['confidence']:.2f}")
            else:
                print(f"  🎯 Expected: {result['expected_service']}, Got: {result['retrieved_service']}")
                
        except Exception as e:
            print(f"  ❌ Query failed: {e}")
            results.append({
                "query_text": query["text"],
                "expected_service": query["service"],
                "is_successful": False,
                "error": str(e)
            })
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate results
    successful = sum(1 for r in results if r.get("is_successful", False))
    success_rate = (successful / len(results)) * 100
    
    print(f"\n📊 QUICK BASELINE RESULTS")
    print("=" * 40)
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    print(f"📊 Average Time per Query: {total_time/len(results):.1f}s")
    
    # Service breakdown
    service_results = {}
    for result in results:
        service = result.get("expected_service", "unknown")
        if service not in service_results:
            service_results[service] = {"total": 0, "successful": 0}
        
        service_results[service]["total"] += 1
        if result.get("is_successful", False):
            service_results[service]["successful"] += 1
    
    print(f"\n🔍 Service Breakdown:")
    for service, stats in service_results.items():
        service_rate = (stats["successful"] / stats["total"]) * 100
        print(f"  {service.title()}: {service_rate:.1f}% ({stats['successful']}/{stats['total']})")
    
    print(f"\n🎯 Gap to Target: {90.0 - success_rate:.1f} percentage points")
    
    if success_rate >= 90.0:
        print("🎉 SUCCESS: Target achieved!")
    else:
        print("⚠️  Need improvements to reach 90% target")
    
    return {
        "success_rate": success_rate,
        "total_queries": len(results),
        "successful_queries": successful,
        "total_time": total_time,
        "service_breakdown": service_results
    }


if __name__ == "__main__":
    run_quick_baseline() 