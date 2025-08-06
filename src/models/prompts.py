"""
LLM Prompts for NYC Services GPT
TODO: implement prompt engineering to achieve ≥ 90% Self-Service Success Rate as specified in PROJECT_SPEC.md
"""

from typing import Dict, List
from ..config import config

class PromptManager:
    """Manage prompts for NYC services RAG system"""
    
    def __init__(self):
        # TODO: initialize prompt templates for 5 NYC services
        pass
    
    def get_system_prompt(self) -> str:
        """Get system prompt for NYC services assistant"""
        # TODO: implement system prompt for Maria the Micro-Entrepreneur persona
        return """
        You are a helpful NYC services assistant. Provide clear, accurate answers 
        about NYC government services in plain language. Always include relevant 
        steps and links when available.
        """
    
    def get_query_prompt(self, query: str, context: str) -> str:
        """Format query prompt with context"""
        # TODO: implement query prompt formatting for 100 synthetic queries
        pass
    
    def get_evaluation_prompt(self) -> str:
        """Get prompt for evaluating response quality"""
        # TODO: implement evaluation prompt for baseline measurement
        pass

class ResponseFormatter:
    """Format RAG responses for NYC services"""
    
    def __init__(self):
        pass
    
    def format_steps(self, steps: List[str]) -> str:
        """Format response with numbered steps"""
        # TODO: implement step formatting with 3 relevant steps
        pass
    
    def add_links(self, response: str, links: List[str]) -> str:
        """Add relevant links to response"""
        # TODO: implement link addition for NYC service resources
        pass
    
    def format_for_persona(self, response: str) -> str:
        """Format response for Maria the Micro-Entrepreneur persona"""
        # TODO: implement persona-specific formatting
        pass

if __name__ == '__main__':
    prompt_manager = PromptManager()
    formatter = ResponseFormatter() 