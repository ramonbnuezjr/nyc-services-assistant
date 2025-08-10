"""
Provider Router for NYC Services GPT RAG System

This module provides intelligent provider routing for the MVP UI,
leveraging existing LLMClient infrastructure for optimal performance.
"""

import time
from typing import List, Dict, Optional
from .llm_client import LLMClient
from .mock_fallback import mock_fallback
from ..retrieve.vector_store import init_vector_store
from ..ingest.data_processor import EmbeddingClient
from ..config import config


def answer_with_rag(
    question: str, 
    top_k: int = 5, 
    filters: Optional[Dict] = None,
    provider: str = "openai"
) -> Dict:
    """
    Main RAG function that routes queries through the appropriate provider.
    
    Args:
        question: User's question about NYC services
        top_k: Number of document chunks to retrieve
        filters: Optional metadata filters (e.g., {"service_type": "SNAP"})
        provider: Provider to use ("openai", "gemini", "mock")
        
    Returns:
        Dictionary with answer, sources, and metadata:
        {
            "answer": str,           # Generated response
            "sources": List[Dict],   # Source documents used
            "meta": {                # Performance metadata
                "latency_ms": int,
                "provider": str,
                "top_k": int,
                "re_ranked": bool,
                "tokens_used": int,
                "cost_estimate": float
            }
        }
    """
    start_time = time.time()
    
    # Initialize vector store
    vs = init_vector_store()
    if not vs:
        return {
            "answer": "❌ Failed to initialize vector store. Please try again.",
            "sources": [],
            "meta": {
                "latency_ms": int((time.time() - start_time) * 1000),
                "provider": "error",
                "top_k": top_k,
                "re_ranked": False,
                "tokens_used": 0,
                "cost_estimate": 0.0
            }
        }
    
    try:
        # Generate embedding for the question
        embedding_client = EmbeddingClient()
        question_embedding = embedding_client.get_embedding(question)
        
        # Retrieve relevant documents
        retrieved_docs = vs.query_vector_store(
            query_embedding=question_embedding,
            top_k=top_k,
            filter_metadata=filters
        )
        
        if not retrieved_docs:
            return {
                "answer": "I couldn't find specific information about that. Please try rephrasing your question about NYC services.",
                "sources": [],
                "meta": {
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "provider": "no_results",
                    "top_k": top_k,
                    "re_ranked": False,
                    "tokens_used": 0,
                    "cost_estimate": 0.0
                }
            }
        
        # Route to appropriate provider
        if provider == "mock" or not config.use_real_llm:
            response = _generate_mock_response(question, retrieved_docs)
            provider_used = "mock"
        elif provider == "openai":
            response = _generate_openai_response(question, retrieved_docs)
            provider_used = "openai"
        elif provider == "gemini":
            response = _generate_gemini_response(question, retrieved_docs)
            provider_used = "gemini"
        else:
            # Fallback to OpenAI
            response = _generate_openai_response(question, retrieved_docs)
            provider_used = "openai"
        
        # Calculate metadata
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "answer": response.get("response", "No response generated"),
            "sources": _format_sources(retrieved_docs),
            "meta": {
                "latency_ms": latency_ms,
                "provider": provider_used,
                "top_k": top_k,
                "re_ranked": False,  # TODO: implement re-ranking in future
                "tokens_used": response.get("tokens_used", 0),
                "cost_estimate": _estimate_cost(response.get("tokens_used", 0), provider_used)
            }
        }
        
    except Exception as e:
        return {
            "answer": f"❌ An error occurred: {str(e)}. Please try again.",
            "sources": [],
            "meta": {
                "latency_ms": int((time.time() - start_time) * 1000),
                "provider": "error",
                "top_k": top_k,
                "re_ranked": False,
                "tokens_used": 0,
                "cost_estimate": 0.0
            }
        }


def _generate_openai_response(question: str, retrieved_docs: List[Dict]) -> Dict:
    """Generate response using OpenAI LLM"""
    try:
        llm_client = LLMClient()
        return llm_client.generate_response(
            query=question,
            retrieved_documents=retrieved_docs,
            max_tokens=300
        )
    except Exception as e:
        print(f"OpenAI error: {e}")
        return _generate_mock_response(question, retrieved_docs)


def _generate_gemini_response(question: str, retrieved_docs: List[Dict]) -> Dict:
    """Generate response using Google Gemini (placeholder for future implementation)"""
    # TODO: Implement Gemini integration
    print("Gemini not yet implemented, falling back to mock")
    return _generate_mock_response(question, retrieved_docs)


def _generate_mock_response(question: str, retrieved_docs: List[Dict]) -> Dict:
    """Generate response using mock fallback system"""
    try:
        # Use the existing mock fallback system
        return mock_fallback.generate_response(question, retrieved_docs)
    except Exception as e:
        print(f"Mock fallback error: {e}")
        return {
            "response": "I'm currently in maintenance mode. Please try again later.",
            "tokens_used": 0
        }


def _format_sources(retrieved_docs: List[Dict]) -> List[Dict]:
    """Format retrieved documents for display"""
    sources = []
    for doc in retrieved_docs:
        source_info = {
            "text": doc.get("text", "")[:200] + "..." if len(doc.get("text", "")) > 200 else doc.get("text", ""),
            "service": doc.get("metadata", {}).get("service_type", "Unknown"),
            "source": doc.get("metadata", {}).get("source", "Unknown document"),
            "score": doc.get("score", 0.0)
        }
        sources.append(source_info)
    return sources


def _estimate_cost(tokens_used: int, provider: str) -> float:
    """Estimate cost based on tokens used and provider"""
    if provider == "openai":
        # gpt-4o-mini pricing: $0.15 per 1K input, $0.60 per 1K output
        # Assuming 70% input, 30% output tokens
        input_cost = (tokens_used * 0.7 * 0.15) / 1000
        output_cost = (tokens_used * 0.3 * 0.60) / 1000
        return input_cost + output_cost
    elif provider == "gemini":
        # TODO: Add Gemini pricing
        return 0.0
    else:
        return 0.0
