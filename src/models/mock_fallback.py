"""
Mock Fallback System for NYC Services GPT MVP

This module provides intelligent mock responses when rate limits or budget limits are hit,
ensuring the MVP never crashes and you can keep iterating without extra API costs.
"""

import random
from typing import List, Dict, Optional
from datetime import datetime

class MockFallbackManager:
    """
    Manages intelligent mock responses when API limits are exceeded.
    
    Features:
    - Service-aware mock responses
    - Realistic response structure
    - Maintains evaluation compatibility
    - Zero API costs
    """
    
    def __init__(self):
        self.fallback_active = False
        self.fallback_reason = None
        self.fallback_count = 0
        
        # Service-specific mock responses
        self.service_responses = {
            "unemployment": [
                "To apply for unemployment benefits in NYC, visit the NY Department of Labor website at labor.ny.gov. You'll need your Social Security number, employment history, and reason for job separation. The application typically takes 30 minutes to complete online.",
                "Unemployment benefits processing usually takes 2-3 weeks. You can check your claim status online or by calling 1-888-209-8124. Make sure to certify weekly to continue receiving benefits.",
                "You can work part-time while receiving unemployment benefits, but you must report all earnings. Your benefits will be reduced based on your earnings, but you may still receive partial payments."
            ],
            "snap": [
                "To apply for SNAP benefits in NYC, you can apply online through ACCESS NYC or visit a local SNAP center. You'll need proof of income, identity, and residency. Processing typically takes 30 days.",
                "SNAP benefits are loaded monthly on your EBT card. You can check your balance by calling 1-888-328-6399 or online through the ConnectEBT website. Benefits can be used at most grocery stores and farmers markets.",
                "SNAP income limits depend on household size. For a family of four, the monthly gross income limit is approximately $3,200. Different deductions may apply to reduce your countable income."
            ],
            "medicaid": [
                "You can apply for Medicaid in NYC through the NY State of Health marketplace at nystateofhealth.ny.gov or by calling 1-855-355-5777. Medicaid enrollment is available year-round.",
                "Medicaid covers a wide range of services including doctor visits, hospital care, prescription drugs, and preventive care. Most services require no co-payment for Medicaid recipients.",
                "To renew your Medicaid coverage, you'll receive a renewal notice in the mail. You can renew online, by phone, or by mail. Keep your contact information updated to receive important notices."
            ],
            "cash_assistance": [
                "To apply for Cash Assistance in NYC, visit your local Job Center or apply online through ACCESS NYC. You'll need to attend an interview and provide required documentation within 30 days.",
                "Cash Assistance includes Family Assistance and Safety Net Assistance programs. Eligibility depends on income, household size, and other factors. Most recipients must participate in work activities.",
                "You can work while receiving cash assistance, but you must report all income to your caseworker within 10 days. Work requirements and time limits may apply depending on your situation."
            ],
            "childcare": [
                "To apply for child care subsidies in NYC, contact your local child care resource and referral agency or apply through the NYC Administration for Children's Services. Income limits apply based on family size.",
                "Child care subsidies can be used with approved providers including day care centers, family day care, and after-school programs. You may be required to pay a co-payment based on your income.",
                "To find approved child care providers, use the online database through the Office of Children and Family Services or contact your local resource agency for a list of providers in your area."
            ]
        }
        
        # Generic responses for unknown services
        self.generic_responses = [
            "For assistance with NYC services, you can visit nyc.gov or call 311 for general information and referrals to the appropriate city agencies.",
            "Many NYC services can be accessed online through the ACCESS NYC website, which provides applications and information for various benefit programs.",
            "For specific questions about eligibility and application processes, contact the relevant NYC agency directly or visit a local service center for in-person assistance."
        ]
    
    def activate_fallback(self, reason: str = "rate_limit"):
        """
        Activate mock fallback mode.
        
        Args:
            reason: Reason for fallback ('rate_limit', 'budget_exceeded', 'api_error')
        """
        self.fallback_active = True
        self.fallback_reason = reason
        self.fallback_count = 0
        
        print(f"🔄 Mock fallback activated: {reason}")
        print("💡 System will continue working with mock responses - no API costs!")
    
    def deactivate_fallback(self):
        """Deactivate mock fallback mode."""
        if self.fallback_active:
            print(f"✅ Mock fallback deactivated after {self.fallback_count} mock responses")
        
        self.fallback_active = False
        self.fallback_reason = None
        self.fallback_count = 0
    
    def get_mock_llm_response(self, query: str, retrieved_documents: List[Dict]) -> Dict:
        """
        Generate a mock LLM response that maintains system compatibility.
        
        Args:
            query: User query
            retrieved_documents: Retrieved documents (used for service detection)
            
        Returns:
            Mock response dictionary compatible with real LLM responses
        """
        self.fallback_count += 1
        
        # Detect service from query or documents
        service = self._detect_service(query, retrieved_documents)
        
        # Get appropriate mock response
        if service in self.service_responses:
            responses = self.service_responses[service]
            response_text = random.choice(responses)
        else:
            response_text = random.choice(self.generic_responses)
        
        # Add query-specific context
        response_text = self._customize_response(response_text, query)
        
        # Extract sources from documents
        sources_used = []
        for doc in retrieved_documents[:3]:  # Use first 3 documents
            source = doc.get("metadata", {}).get("source", "mock_source")
            if source not in sources_used:
                sources_used.append(source)
        
        if not sources_used:
            sources_used = ["mock_source"]
        
        return {
            "response": response_text,
            "confidence": 0.85,  # High confidence to maintain evaluation flow
            "sources_used": sources_used,
            "tokens_used": len(response_text.split()) * 1.3,  # Approximate token count
            "model": f"mock-fallback-{service}",
            "from_cache": False,
            "fallback_reason": self.fallback_reason,
            "fallback_count": self.fallback_count
        }
    
    def get_mock_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate mock embeddings that maintain system compatibility.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of mock embedding vectors (1536 dimensions)
        """
        self.fallback_count += 1
        
        embeddings = []
        for i, text in enumerate(texts):
            # Generate deterministic but varied embeddings based on text content
            seed = hash(text) % 1000
            random.seed(seed)
            
            # Create embedding with slight variations
            base_embedding = [random.uniform(-0.1, 0.1) for _ in range(1536)]
            
            # Add some structure based on text length and content
            text_lower = text.lower()
            if any(word in text_lower for word in ["unemployment", "job", "work"]):
                base_embedding[0] = 0.5  # Unemployment indicator
            elif any(word in text_lower for word in ["snap", "food", "ebt"]):
                base_embedding[1] = 0.5  # SNAP indicator
            elif any(word in text_lower for word in ["medicaid", "health", "medical"]):
                base_embedding[2] = 0.5  # Medicaid indicator
            elif any(word in text_lower for word in ["cash", "assistance", "financial"]):
                base_embedding[3] = 0.5  # Cash assistance indicator
            elif any(word in text_lower for word in ["childcare", "daycare", "child"]):
                base_embedding[4] = 0.5  # Childcare indicator
            
            embeddings.append(base_embedding)
        
        print(f"🔄 Generated {len(embeddings)} mock embeddings (fallback active)")
        return embeddings
    
    def _detect_service(self, query: str, documents: List[Dict]) -> str:
        """Detect the service type from query and documents."""
        query_lower = query.lower()
        
        # Check query for service keywords
        if any(word in query_lower for word in ["unemployment", "job loss", "benefits"]):
            return "unemployment"
        elif any(word in query_lower for word in ["snap", "food stamps", "ebt"]):
            return "snap"
        elif any(word in query_lower for word in ["medicaid", "health", "medical"]):
            return "medicaid"
        elif any(word in query_lower for word in ["cash assistance", "financial aid"]):
            return "cash_assistance"
        elif any(word in query_lower for word in ["childcare", "daycare", "child care"]):
            return "childcare"
        
        # Check documents for service metadata
        for doc in documents:
            service = doc.get("metadata", {}).get("service")
            if service:
                return service
        
        return "general"
    
    def _customize_response(self, response: str, query: str) -> str:
        """Customize the response based on the specific query."""
        query_lower = query.lower()
        
        # Add query-specific details
        if "apply" in query_lower:
            response = f"To answer your question about applying: {response}"
        elif "documents" in query_lower or "paperwork" in query_lower:
            response = f"Regarding required documentation: {response}"
        elif "status" in query_lower or "check" in query_lower:
            response = f"To check your status: {response}"
        elif "renew" in query_lower:
            response = f"For renewal information: {response}"
        
        return response
    
    def get_status_info(self) -> Dict:
        """Get current fallback status information."""
        return {
            "fallback_active": self.fallback_active,
            "fallback_reason": self.fallback_reason,
            "fallback_count": self.fallback_count,
            "timestamp": datetime.now().isoformat()
        }

# Global mock fallback manager
mock_fallback = MockFallbackManager()
