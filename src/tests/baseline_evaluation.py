"""
Baseline Evaluation for NYC Services GPT RAG System

This module runs the 100-query baseline evaluation to measure the current
Self-Service Success Rate. It uses the synthetic queries from PROJECT_SPEC.md
across 5 NYC services: Unemployment, SNAP, Medicaid, Cash Assistance, Child Care.

The evaluation measures retrieval accuracy and provides insights for achieving
the ≥ 90% Self-Service Success Rate KPI.
"""

import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd

from src.ingest.data_processor import process_documents, EmbeddingClient
from src.retrieve.vector_store import init_vector_store, add_documents, query_vector_store
from src.config import config


class BaselineEvaluator:
    """
    Evaluates the RAG pipeline using the 100-query seed set from PROJECT_SPEC.md.
    
    Measures Self-Service Success Rate by testing retrieval accuracy across
    5 NYC services: Unemployment, SNAP, Medicaid, Cash Assistance, Child Care.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the baseline evaluator.
        
        Args:
            db_path: Path for vector database (defaults to temp directory)
        """
        self.db_path = db_path or tempfile.mkdtemp()
        self.vector_store = None
        self.evaluation_results = []
        
        # Load the 100 synthetic queries from PROJECT_SPEC.md
        self.queries = self._load_synthetic_queries()
        
        # Load corresponding documents for each service
        self.documents = self._load_service_documents()
    
    def _load_synthetic_queries(self) -> List[Dict]:
        """
        Load the 100 synthetic queries from PROJECT_SPEC.md.
        
        Returns:
            List of query dictionaries with text and expected service
        """
        queries = []
        
        # Unemployment Benefits (20 queries)
        unemployment_queries = [
            "How do I apply for unemployment benefits in NYC?",
            "What documents are required for New York State unemployment?",
            "Can I file an unemployment claim online from Staten Island?",
            "What's the processing time for unemployment insurance?",
            "Who qualifies for partial unemployment benefits?",
            "How do I check my weekly unemployment payment status?",
            "What happens if my unemployment claim is denied?",
            "How do I appeal an unemployment benefits decision?",
            "Are gig workers eligible for unemployment benefits?",
            "How do I update my address on my unemployment account?",
            "What is the maximum unemployment benefit amount in NYC?",
            "Can I work part-time while receiving unemployment?",
            "How do I report earnings while on unemployment?",
            "What's 'Extended Duration Benefits' and who qualifies?",
            "How do I submit my weekly certification for benefits?",
            "Are independent contractors covered?",
            "Do I need an SSN to apply?",
            "Can I get retroactive unemployment payments?",
            "Where can I find phone support for unemployment issues?",
            "How long do I have to file after losing my job?"
        ]
        
        for query in unemployment_queries:
            queries.append({
                "text": query,
                "service": "unemployment",
                "category": "Unemployment Benefits"
            })
        
        # SNAP (Food Stamps) (20 queries)
        snap_queries = [
            "How do I apply for SNAP benefits in NYC?",
            "What income limits apply to SNAP in New York?",
            "Can I pre-screen for SNAP eligibility online?",
            "What documents do I need for a SNAP interview?",
            "How long does SNAP application processing take?",
            "How do I check my EBT balance?",
            "Can I use EBT at local farmers' markets?",
            "How do I report a change in household size?",
            "What happens if my SNAP case is closed?",
            "How do I reapply for SNAP after denial?",
            "Are college students eligible for SNAP?",
            "How do I appeal a SNAP decision?",
            "Can mixed-status families apply?",
            "What expenses count toward SNAP income deductions?",
            "How do I find my SNAP case worker's contact?",
            "How do I request replacement EBT card?",
            "Can I use my SNAP benefits on groceries delivered?",
            "Are benefits loaded monthly or biweekly?",
            "What outreach programs exist for seniors on SNAP?",
            "How do I report lost SNAP benefits?"
        ]
        
        for query in snap_queries:
            queries.append({
                "text": query,
                "service": "snap",
                "category": "SNAP (Food Stamps)"
            })
        
        # Medicaid (Health Coverage) (20 queries)
        medicaid_queries = [
            "How do I apply for Medicaid in NYC?",
            "What income qualifies me for Medicaid?",
            "Can I enroll in Medicaid year-round?",
            "How do I check my Medicaid application status?",
            "What documents are required for Medicaid?",
            "How do I renew my Medicaid coverage?",
            "What happens if I miss my renewal deadline?",
            "Can I switch from Emergency Medicaid to full coverage?",
            "How do I add a newborn to my Medicaid plan?",
            "What providers accept Medicaid in Brooklyn?",
            "How do I request a Medicaid ID card replacement?",
            "Are dental services covered?",
            "How do I appeal a Medicaid denial?",
            "Can I have Medicaid and marketplace insurance?",
            "How do I report a change in income?",
            "What long-term care services are covered?",
            "How do I find transportation services under Medicaid?",
            "What behavioral health services are included?",
            "How do I get language interpretation for Medicaid services?",
            "Can I keep Medicaid if I start working?"
        ]
        
        for query in medicaid_queries:
            queries.append({
                "text": query,
                "service": "medicaid",
                "category": "Medicaid (Health Coverage)"
            })
        
        # Cash Assistance (20 queries)
        cash_assistance_queries = [
            "How do I apply for Cash Assistance in NYC?",
            "What's the income cutoff for Family Assistance?",
            "How does Safety Net Assistance differ?",
            "What documents are needed for a cash assistance interview?",
            "How long does approval take?",
            "Can I work while on cash assistance?",
            "How do I report earnings?",
            "What are the work requirements?",
            "How do I check my cash assistance payment status?",
            "How do I change my bank account for direct deposit?",
            "Can I receive cash assistance for non-citizen household members?",
            "How do I appeal a cash assistance denial?",
            "What sanctions apply for missed appointments?",
            "How do I request an emergency cash grant?",
            "Can I get cash assistance if I'm homeless?",
            "How do I add a child to my case?",
            "Are utilities included in the budget?",
            "How do I find my cash assistance worker's contact?",
            "What budget deductions apply (e.g. shelter, childcare)?",
            "How do I renew my case after closure?"
        ]
        
        for query in cash_assistance_queries:
            queries.append({
                "text": query,
                "service": "cash_assistance",
                "category": "Cash Assistance"
            })
        
        # Child Care Subsidy (20 queries)
        childcare_queries = [
            "How do I apply for child care subsidy in NYC?",
            "What income qualifies for child care assistance?",
            "How do I find approved daycare providers?",
            "What documents are required for application?",
            "How long does the approval process take?",
            "Can I keep subsidy if I change providers?",
            "How do I report a change in work hours?",
            "What if my income increases mid-year?",
            "How do I check my subsidy payment status?",
            "Can I use subsidy for after-school programs?",
            "How do I appeal a subsidy denial?",
            "Are summer camps covered?",
            "How do I enroll my child under age 2?",
            "What co‑payments apply?",
            "How do I find caseworker contact info?",
            "Can I get emergency child care assistance?",
            "Is transportation to daycare covered?",
            "How do I renew my subsidy annually?",
            "What if my provider stops accepting subsidies?",
            "Are there priority slots for special‑needs children?"
        ]
        
        for query in childcare_queries:
            queries.append({
                "text": query,
                "service": "childcare",
                "category": "Child Care Subsidy"
            })
        
        return queries
    
    def _load_service_documents(self) -> List[Dict]:
        """
        Load sample documents for each NYC service with proper metadata.
        
        Returns:
            List of document dictionaries with text and service metadata
        """
        documents = [
            # Unemployment Benefits
            {
                "text": "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website. You'll need your Social Security number, driver's license, and employment history. The application process typically takes 30 minutes to complete.",
                "service": "unemployment"
            },
            {
                "text": "What documents are required for New York State unemployment? You need proof of identity, employment history, and reason for separation from your job. This includes your Social Security card, driver's license, and information about your previous employers.",
                "service": "unemployment"
            },
            {
                "text": "Can I file an unemployment claim online from Staten Island? Yes, you can file online from anywhere in New York State. The online system is available 24/7 and is the fastest way to apply for unemployment benefits.",
                "service": "unemployment"
            },
            {
                "text": "What's the processing time for unemployment insurance? Initial claims typically take 2-3 weeks to process. You should receive a determination letter in the mail within this timeframe.",
                "service": "unemployment"
            },
            {
                "text": "Who qualifies for partial unemployment benefits? Workers whose hours have been reduced may qualify for partial benefits. You must work less than full-time and earn less than your weekly benefit amount.",
                "service": "unemployment"
            },
            
            # SNAP (Food Stamps)
            {
                "text": "How do I apply for SNAP benefits in NYC? You can apply online, by phone, or in person at a local office. The online application is available 24/7 and is the fastest method.",
                "service": "snap"
            },
            {
                "text": "What income limits apply to SNAP in New York? Income limits vary by household size and are updated annually. For a family of four, the gross monthly income limit is approximately $3,250.",
                "service": "snap"
            },
            {
                "text": "Can I pre-screen for SNAP eligibility online? Yes, you can use the pre-screening tool on the NYS website to check if you might qualify before applying.",
                "service": "snap"
            },
            {
                "text": "What documents do I need for a SNAP interview? You need proof of income, identity, and residency. This includes pay stubs, utility bills, and photo identification.",
                "service": "snap"
            },
            {
                "text": "How long does SNAP application processing take? Applications are typically processed within 30 days. You may receive benefits retroactively from your application date.",
                "service": "snap"
            },
            
            # Medicaid (Health Coverage)
            {
                "text": "How do I apply for Medicaid in NYC? You can apply online through the NY State of Health marketplace, by phone, or in person. The online application is available year-round.",
                "service": "medicaid"
            },
            {
                "text": "What income qualifies me for Medicaid? Income limits depend on household size and other factors. For a family of four, the monthly income limit is approximately $3,200.",
                "service": "medicaid"
            },
            {
                "text": "Can I enroll in Medicaid year-round? Yes, Medicaid enrollment is available year-round. You can apply at any time, not just during open enrollment periods.",
                "service": "medicaid"
            },
            {
                "text": "How do I check my Medicaid application status? You can check online through the NY State of Health website or call the helpline at 1-855-355-5777.",
                "service": "medicaid"
            },
            {
                "text": "What documents are required for Medicaid? You need proof of income, identity, and residency. This includes pay stubs, tax returns, and utility bills.",
                "service": "medicaid"
            },
            
            # Cash Assistance
            {
                "text": "How do I apply for Cash Assistance in NYC? You can apply online or in person at a local office. The application process includes an interview and documentation review.",
                "service": "cash_assistance"
            },
            {
                "text": "What's the income cutoff for Family Assistance? Income limits vary by household size and composition. The limits are updated annually and depend on your family's specific circumstances.",
                "service": "cash_assistance"
            },
            {
                "text": "How does Safety Net Assistance differ? Safety Net Assistance is for those who don't qualify for Family Assistance. It provides temporary financial support for individuals and families.",
                "service": "cash_assistance"
            },
            {
                "text": "What documents are needed for a cash assistance interview? You need proof of income, identity, and residency. This includes pay stubs, birth certificates, and utility bills.",
                "service": "cash_assistance"
            },
            {
                "text": "How long does approval take? Initial applications are typically processed within 30 days. Emergency grants may be available for urgent situations.",
                "service": "cash_assistance"
            },
            
            # Child Care Subsidy
            {
                "text": "How do I apply for child care subsidy in NYC? You can apply online or contact your local child care resource and referral agency. The application process includes income verification and provider selection.",
                "service": "childcare"
            },
            {
                "text": "What income qualifies for child care assistance? Income limits depend on family size and child care costs. Generally, families earning up to 200% of the federal poverty level may qualify.",
                "service": "childcare"
            },
            {
                "text": "How do I find approved daycare providers? You can search the online provider database or contact your local child care resource agency for a list of approved providers in your area.",
                "service": "childcare"
            },
            {
                "text": "What documents are required for application? You need proof of income, employment, and child care costs. This includes pay stubs, work schedules, and provider contracts.",
                "service": "childcare"
            },
            {
                "text": "How long does the approval process take? Applications are typically processed within 30 days. You may receive benefits retroactively from your application date.",
                "service": "childcare"
            }
        ]
        
        return documents
    
    def setup_pipeline(self) -> bool:
        """
        Set up the RAG pipeline with documents and vector store.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            print("🔧 Setting up RAG pipeline for baseline evaluation...")
            
            # Process documents through data processor
            print(f"📚 Processing {len(self.documents)} service documents...")
            
            # Extract text from documents and create records with service metadata
            document_texts = [doc["text"] for doc in self.documents]
            records = process_documents(document_texts, chunk_size=200, overlap=50)
            
            # Add service metadata to records
            for i, record in enumerate(records):
                # Find which document this chunk came from
                doc_index = i // 2  # Rough mapping (each doc might produce multiple chunks)
                if doc_index < len(self.documents):
                    record["metadata"]["service"] = self.documents[doc_index]["service"]
            
            if not records:
                print("❌ No records generated from documents")
                return False
            
            print(f"✅ Generated {len(records)} document chunks")
            
            # Initialize vector store
            print("🔧 Initializing vector store...")
            self.vector_store = init_vector_store(db_path=self.db_path)
            
            if not self.vector_store:
                print("❌ Failed to initialize vector store")
                return False
            
            # Add documents to vector store
            print("📚 Adding documents to vector store...")
            success = add_documents(self.vector_store, records)
            
            if not success:
                print("❌ Failed to add documents to vector store")
                return False
            
            print(f"✅ Pipeline setup complete. Ready for {len(self.queries)} queries.")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline setup failed: {e}")
            return False
    
    def evaluate_query(self, query: Dict) -> Dict:
        """
        Evaluate a single query against the RAG pipeline.
        
        Args:
            query: Query dictionary with text and expected service
            
        Returns:
            Evaluation result dictionary
        """
        try:
            # Generate query embedding using real OpenAI embeddings
            embedding_client = EmbeddingClient()
            query_embedding = embedding_client.get_embedding(query["text"])
            
            # Query vector store
            results = query_vector_store(self.vector_store, query_embedding, top_k=3)
            
            # Determine if retrieval was successful
            retrieved_service = None
            if results:
                # Check if any retrieved document matches expected service
                for result in results:
                    metadata = result.get("metadata", {})
                    if metadata.get("service") == query["service"]:
                        retrieved_service = query["service"]
                        break
                
                # If no exact match, use the first result's service
                if not retrieved_service and results:
                    retrieved_service = results[0]["metadata"].get("service", "unknown")
            
            # Calculate success
            is_successful = retrieved_service == query["service"]
            
            return {
                "query_text": query["text"],
                "expected_service": query["service"],
                "retrieved_service": retrieved_service,
                "is_successful": is_successful,
                "num_results": len(results),
                "results": results[:2] if results else []  # Store first 2 results for analysis
            }
            
        except Exception as e:
            print(f"❌ Error evaluating query '{query['text']}': {e}")
            return {
                "query_text": query["text"],
                "expected_service": query["service"],
                "retrieved_service": "error",
                "is_successful": False,
                "num_results": 0,
                "results": [],
                "error": str(e)
            }
    
    def run_baseline_evaluation(self) -> Dict:
        """
        Run the complete 100-query baseline evaluation.
        
        Returns:
            Evaluation results summary
        """
        print("🎯 Starting 100-query baseline evaluation...")
        print("=" * 60)
        
        # Setup pipeline
        if not self.setup_pipeline():
            return {"error": "Pipeline setup failed"}
        
        # Evaluate each query
        successful_queries = 0
        total_queries = len(self.queries)
        
        print(f"🔍 Evaluating {total_queries} queries...")
        
        for i, query in enumerate(self.queries, 1):
            print(f"Query {i}/{total_queries}: {query['text'][:50]}...")
            
            result = self.evaluate_query(query)
            self.evaluation_results.append(result)
            
            if result["is_successful"]:
                successful_queries += 1
                print(f"  ✅ Success")
            else:
                print(f"  ❌ Failed (expected: {query['service']}, got: {result['retrieved_service']})")
        
        # Calculate success rate
        success_rate = (successful_queries / total_queries) * 100
        
        # Generate summary
        summary = {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": total_queries - successful_queries,
            "success_rate": success_rate,
            "target_success_rate": config.target_success_rate,
            "evaluation_date": datetime.now().isoformat(),
            "service_breakdown": self._calculate_service_breakdown(),
            "detailed_results": self.evaluation_results
        }
        
        return summary
    
    def _calculate_service_breakdown(self) -> Dict:
        """
        Calculate success rate breakdown by service.
        
        Returns:
            Dictionary with success rates by service
        """
        service_stats = {}
        
        for result in self.evaluation_results:
            service = result["expected_service"]
            if service not in service_stats:
                service_stats[service] = {"total": 0, "successful": 0}
            
            service_stats[service]["total"] += 1
            if result["is_successful"]:
                service_stats[service]["successful"] += 1
        
        # Calculate success rates
        for service, stats in service_stats.items():
            stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
        
        return service_stats
    
    def print_evaluation_summary(self, summary: Dict):
        """
        Print a formatted evaluation summary.
        
        Args:
            summary: Evaluation results summary
        """
        print("\n" + "=" * 60)
        print("📊 BASELINE EVALUATION SUMMARY")
        print("=" * 60)
        
        print(f"🎯 Self-Service Success Rate: {summary['success_rate']:.1f}%")
        print(f"📈 Target Success Rate: {summary['target_success_rate']}%")
        print(f"✅ Successful Queries: {summary['successful_queries']}/{summary['total_queries']}")
        print(f"❌ Failed Queries: {summary['failed_queries']}/{summary['total_queries']}")
        
        print(f"\n📅 Evaluation Date: {summary['evaluation_date']}")
        
        # Service breakdown
        print(f"\n🔍 Success Rate by Service:")
        for service, stats in summary["service_breakdown"].items():
            service_name = service.replace("_", " ").title()
            print(f"  {service_name}: {stats['success_rate']:.1f}% ({stats['successful']}/{stats['total']})")
        
        # Gap analysis
        gap = summary['target_success_rate'] - summary['success_rate']
        if gap > 0:
            print(f"\n⚠️  Gap to Target: {gap:.1f} percentage points")
            print(f"🎯 Need to improve by {gap:.1f}% to reach {summary['target_success_rate']}% target")
        else:
            print(f"\n🎉 Target achieved! Exceeding by {abs(gap):.1f} percentage points")
        
        print("=" * 60)
    
    def save_evaluation_results(self, summary: Dict, output_path: str = "baseline_evaluation_results.json"):
        """
        Save evaluation results to file.
        
        Args:
            summary: Evaluation results summary
            output_path: Path to save results
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"💾 Results saved to {output_path}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")


def run_baseline_evaluation():
    """
    Run the 100-query baseline evaluation.
    
    This function executes the complete baseline evaluation and provides
    insights for achieving the ≥ 90% Self-Service Success Rate KPI.
    """
    print("NYC Services GPT - 100-Query Baseline Evaluation")
    print("=" * 60)
    print(f"🎯 Target: ≥ {config.target_success_rate}% Self-Service Success Rate")
    print(f"📊 Evaluating {config.synthetic_query_count} synthetic queries")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = BaselineEvaluator()
    
    # Run evaluation
    summary = evaluator.run_baseline_evaluation()
    
    if "error" in summary:
        print(f"❌ Evaluation failed: {summary['error']}")
        return
    
    # Print summary
    evaluator.print_evaluation_summary(summary)
    
    # Save results
    evaluator.save_evaluation_results(summary)
    
    # Cleanup
    if evaluator.vector_store:
        evaluator.vector_store.clear_collection()
    shutil.rmtree(evaluator.db_path, ignore_errors=True)
    
    print("\n✅ Baseline evaluation complete!")
    print("📈 Use these results to guide improvements toward the 90% target.")


if __name__ == "__main__":
    """
    Run the baseline evaluation to measure current Self-Service Success Rate.
    
    This provides the baseline measurement needed to track progress toward
    the ≥ 90% Self-Service Success Rate KPI.
    """
    run_baseline_evaluation() 