"""
LLM Client for NYC Services GPT RAG System

This module provides LLM integration for generating responses from retrieved documents.
Uses OpenAI models with comprehensive rate limiting for MVP deployment.
Supports the Self-Service Success Rate KPI by providing complete answers without human intervention.
"""

import openai
import time
import random
from typing import List, Dict, Optional
from ..config import config
from .rate_limiter import rate_limiter
from .mock_fallback import mock_fallback


class LLMClient:
    """
    OpenAI LLM client for generating responses from retrieved documents.
    
    Designed to support the Self-Service Success Rate KPI by providing
    accurate, helpful responses to NYC service queries without human intervention.
    """
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-4o-mini"):
        """
        Initialize the LLM client with rate limiting.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            default_model: Default model to use (gpt-4o-mini for MVP)
        """
        self.api_key = api_key or config.openai_api_key
        self.default_model = default_model
        
        if self.api_key:
            openai.api_key = self.api_key
            print(f"✅ LLM client initialized - Default: {self.default_model}, Rate limiting: enabled")
        else:
            print("⚠️ No OpenAI API key found. Using mock responses for testing.")
    
    def generate_response(
        self, 
        query: str, 
        retrieved_documents: List[Dict],
        max_tokens: int = 300,
        task_hint: str = "",
        allow_premium: bool = False
    ) -> Dict:
        """
        Generate a response to a user query based on retrieved documents.
        
        Uses intelligent model selection and rate limiting for MVP deployment.
        
        Args:
            query: User's original query
            retrieved_documents: List of relevant documents from vector store
            max_tokens: Maximum tokens for response (reduced for MVP)
            task_hint: Hint for model selection (e.g., "complex analysis")
            allow_premium: Allow premium model usage
            
        Returns:
            Dictionary with response and metadata:
            {
                "response": str,           # Generated response
                "confidence": float,       # Confidence score (0-1)
                "sources_used": List[str], # Document sources used
                "tokens_used": int,        # Tokens consumed
                "model": str,              # Model used for generation
                "from_cache": bool         # Whether response came from cache
            }
        """
        if not self.api_key:
            return self._generate_mock_response(query, retrieved_documents)
        
        # Choose appropriate model based on task complexity
        model = rate_limiter.choose_model(task_hint, allow_premium)
        
        return self._generate_response_with_rate_limiting(
            query, retrieved_documents, max_tokens, model
        )
    
    def _generate_response_with_rate_limiting(
        self, 
        query: str, 
        retrieved_documents: List[Dict],
        max_tokens: int = 300,
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """
        Generate response with comprehensive rate limiting and caching.
        
        Args:
            query: User query
            retrieved_documents: Retrieved documents
            max_tokens: Maximum tokens for response
            model: Model to use for generation
            
        Returns:
            Response dictionary with rate limiting metadata
        """
        # Prepare context and prompts
        context = self._prepare_context(retrieved_documents)
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(query, context)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": system_prompt[:2000]},  # Limit system prompt
            {"role": "user", "content": user_prompt}
        ]
        
        # Check cache first (development only)
        cache_key = rate_limiter.get_cache_key(model, messages, max_tokens=max_tokens)
        cached_response = rate_limiter.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Estimate token usage
        estimated_tokens = sum(rate_limiter.estimate_tokens(msg["content"]) for msg in messages)
        estimated_tokens += max_tokens  # Add expected output tokens
        
        # Wait for capacity if needed
        rate_limiter.wait_for_capacity(model, estimated_tokens)
        
        # Attempt API call with exponential backoff
        for attempt in range(rate_limiter.max_retries + 1):
            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    top_p=0.9
                )
                
                # Extract response data
                generated_response = response.choices[0].message.content
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else estimated_tokens - max_tokens
                output_tokens = usage.completion_tokens if usage else rate_limiter.estimate_tokens(generated_response)
                
                # Record usage for rate limiting
                rate_limiter.record_usage(model, input_tokens, output_tokens)
                
                # Extract sources and calculate confidence
                sources_used = [doc.get("metadata", {}).get("source", "unknown") 
                              for doc in retrieved_documents]
                confidence = self._calculate_confidence(retrieved_documents)
                
                result = {
                    "response": generated_response,
                    "confidence": confidence,
                    "sources_used": sources_used,
                    "tokens_used": input_tokens + output_tokens,
                    "model": model,
                    "from_cache": False
                }
                
                # Cache the response (development only)
                rate_limiter.cache_response(cache_key, result)
                
                return result
                
            except openai.RateLimitError as e:
                if attempt < rate_limiter.max_retries:
                    # Use rate limiter's exponential backoff
                    wait_time = rate_limiter.exponential_backoff(attempt + 1)
                    print(f"⚠️ Rate limit hit, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{rate_limiter.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Rate limit exceeded after {rate_limiter.max_retries} retries")
                    mock_fallback.activate_fallback("rate_limit_exceeded")
                    return mock_fallback.get_mock_llm_response(query, retrieved_documents)
                    
            except Exception as e:
                print(f"❌ Failed to generate response: {e}")
                if attempt < rate_limiter.max_retries:
                    wait_time = rate_limiter.exponential_backoff(attempt + 1)
                    print(f"⚠️ Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{rate_limiter.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    mock_fallback.activate_fallback("api_error")
                    return mock_fallback.get_mock_llm_response(query, retrieved_documents)
        
        # Final fallback
        mock_fallback.activate_fallback("unknown_error")
        return mock_fallback.get_mock_llm_response(query, retrieved_documents)
    
    def _create_system_prompt(self) -> str:
        """
        Create system prompt for NYC services assistant.
        
        Returns:
            System prompt string
        """
        return """You are a helpful assistant for NYC government services. Your role is to provide accurate, clear, and actionable information about NYC services including:

- Unemployment Benefits
- SNAP (Food Stamps) 
- Medicaid (Health Coverage)
- Cash Assistance
- Child Care Subsidy

Guidelines:
1. Base your responses ONLY on the provided context documents
2. If the context doesn't contain enough information, say so clearly
3. Provide step-by-step instructions when possible
4. Include relevant contact information or next steps
5. Be concise but comprehensive
6. Use plain, accessible language
7. If you're unsure about something, acknowledge the limitation

Your goal is to help users self-serve without needing human intervention."""
    
    def _create_user_prompt(self, query: str, context: str) -> str:
        """
        Create user prompt with query and context.
        
        Args:
            query: User's original query
            context: Retrieved document context
            
        Returns:
            User prompt string
        """
        return f"""User Query: {query}

Relevant Information:
{context}

Please provide a helpful, accurate response based on the information above. If the information is insufficient, clearly state what additional information would be needed."""
    
    def _prepare_context(self, retrieved_documents: List[Dict]) -> str:
        """
        Prepare context from retrieved documents.
        
        Args:
            retrieved_documents: List of document dictionaries
            
        Returns:
            Formatted context string
        """
        if not retrieved_documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_documents, 1):
            text = doc.get("text", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            service = doc.get("metadata", {}).get("service", "unknown")
            
            context_parts.append(f"Document {i} (Source: {source}, Service: {service}):\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, retrieved_documents: List[Dict]) -> float:
        """
        Calculate confidence score based on document relevance.
        
        Args:
            retrieved_documents: List of retrieved documents
            
        Returns:
            Confidence score between 0 and 1
        """
        if not retrieved_documents:
            return 0.0
        
        # Simple confidence calculation based on number and quality of documents
        num_docs = len(retrieved_documents)
        
        # Check if documents have service metadata (indicates better retrieval)
        has_service_metadata = any(
            doc.get("metadata", {}).get("service") 
            for doc in retrieved_documents
        )
        
        # Base confidence on document count and metadata quality
        base_confidence = min(num_docs / 3.0, 1.0)  # Cap at 1.0 for 3+ docs
        
        if has_service_metadata:
            base_confidence *= 1.2  # Boost confidence if service metadata present
        
        return min(base_confidence, 1.0)
    
    def _generate_mock_response(self, query: str, retrieved_documents: List[Dict]) -> Dict:
        """
        Generate mock response for testing when no API key is available.
        
        Args:
            query: User query
            retrieved_documents: Retrieved documents
            
        Returns:
            Mock response dictionary
        """
        if not retrieved_documents:
            return {
                "response": "I don't have enough information to answer your question about NYC services. Please contact the relevant NYC service office for assistance.",
                "confidence": 0.0,
                "sources_used": [],
                "tokens_used": 0,
                "model": "mock"
            }
        
        # Generate a simple mock response based on the query
        query_lower = query.lower()
        
        if "unemployment" in query_lower:
            response = "Based on the available information, you can apply for unemployment benefits online through the New York State Department of Labor website. You'll need your Social Security number, driver's license, and employment history."
        elif "snap" in query_lower or "food stamps" in query_lower:
            response = "For SNAP benefits, you can apply online, by phone, or in person. You'll need proof of income, identity, and residency."
        elif "medicaid" in query_lower:
            response = "You can apply for Medicaid online through the NY State of Health marketplace. Income limits depend on household size."
        elif "cash assistance" in query_lower:
            response = "Cash assistance applications can be submitted online or in person. You'll need to provide proof of income and residency."
        elif "child care" in query_lower or "childcare" in query_lower:
            response = "For child care subsidies, contact your local child care resource agency. Income limits depend on family size and child care costs."
        else:
            response = "I found some relevant information about NYC services. Please contact the appropriate NYC service office for specific guidance."
        
        return {
            "response": response,
            "confidence": 0.6,
            "sources_used": [doc.get("metadata", {}).get("source", "unknown") for doc in retrieved_documents],
            "tokens_used": 0,
            "model": "mock"
        }
    
    def validate_response(self, response: Dict) -> bool:
        """
        Validate that a response has the required structure.
        
        Args:
            response: Response dictionary to validate
            
        Returns:
            True if response is valid, False otherwise
        """
        required_fields = ["response", "confidence", "sources_used", "tokens_used", "model"]
        
        if not all(field in response for field in required_fields):
            return False
        
        # Check data types
        if not isinstance(response["response"], str):
            return False
        if not isinstance(response["confidence"], (int, float)):
            return False
        if not isinstance(response["sources_used"], list):
            return False
        if not isinstance(response["tokens_used"], int):
            return False
        if not isinstance(response["model"], str):
            return False
        
        # Check confidence range
        if not (0 <= response["confidence"] <= 1):
            return False
        
        return True


def create_llm_client(api_key: Optional[str] = None, model: str = "gpt-4") -> LLMClient:
    """
    Create and return an LLM client instance.
    
    Args:
        api_key: OpenAI API key (defaults to config)
        model: LLM model to use
        
    Returns:
        Initialized LLMClient instance
    """
    return LLMClient(api_key, model)


if __name__ == "__main__":
    """
    Demo stub showing how to use the LLM client for NYC Services RAG system.
    
    This demonstrates response generation from retrieved documents for the
    100-query evaluation set targeting ≥ 90% Self-Service Success Rate.
    """
    print("NYC Services GPT - LLM Client Demo")
    print("=" * 50)
    
    # Create LLM client
    llm_client = create_llm_client()
    
    # Sample query and retrieved documents
    sample_query = "How do I apply for unemployment benefits in NYC?"
    sample_documents = [
        {
            "text": "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website. You'll need your Social Security number, driver's license, and employment history.",
            "metadata": {
                "source": "unemployment_guide.txt",
                "service": "unemployment"
            }
        }
    ]
    
    print(f"Query: {sample_query}")
    print(f"Retrieved {len(sample_documents)} documents")
    
    # Generate response
    response = llm_client.generate_response(sample_query, sample_documents)
    
    print(f"\nGenerated Response:")
    print(f"Response: {response['response']}")
    print(f"Confidence: {response['confidence']:.2f}")
    print(f"Sources: {response['sources_used']}")
    print(f"Model: {response['model']}")
    
    print(f"\n🎯 Ready for integration with RAG pipeline!")
    print(f"🎯 Target: ≥ {config.target_success_rate}% Self-Service Success Rate") 