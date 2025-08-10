"""
Configuration management for NYC Services GPT RAG System
TODO: implement configuration loading for API keys and settings as specified in PROJECT_SPEC.md
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for NYC Services GPT RAG system"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key = self._get_api_key("OPENAI_API_KEY")
        self.google_gemini_api_key = self._get_api_key("GOOGLE_GEMINI_API_KEY")
        self.elevenlabs_api_key = self._get_api_key("ELEVENLABS_API_KEY")
        
        # RAG System Settings
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4")
        
        # Evaluation Settings
        self.target_success_rate = float(os.getenv("TARGET_SUCCESS_RATE", "90.0"))
        self.synthetic_query_count = int(os.getenv("SYNTHETIC_QUERY_COUNT", "100"))
        
        # API Settings
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "5000"))
        self.debug_mode = os.getenv("DEBUG_MODE", "True").lower() == "true"
        
        # Feature Flags for MVP UI
        self.use_real_llm = os.getenv("USE_REAL_LLM", "true").lower() == "true"
        self.default_provider = os.getenv("DEFAULT_PROVIDER", "openai")
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_rps = int(os.getenv("RATE_LIMIT_RPS", "5"))
        self.allowlist = os.getenv("ALLOWLIST", "127.0.0.1,::1").split(",")
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """Safely get API key from environment"""
        api_key = os.getenv(key_name)
        if not api_key:
            print(f"Warning: {key_name} not found in environment variables")
        return api_key
    
    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present"""
        required_keys = ["openai_api_key"]
        missing_keys = [key for key in required_keys if not getattr(self, key)]
        
        if missing_keys:
            print(f"Missing required API keys: {missing_keys}")
            return False
        
        return True
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration"""
        return {
            "api_key": self.openai_api_key,
            "model": self.llm_model,
            "embedding_model": self.embedding_model
        }
    
    def get_gemini_config(self) -> dict:
        """Get Google Gemini configuration"""
        return {
            "api_key": self.google_gemini_api_key,
            "model": "gemini-1.5-pro"
        }
    
    def get_elevenlabs_config(self) -> dict:
        """Get ElevenLabs configuration"""
        return {
            "api_key": self.elevenlabs_api_key
        }
    
    def get_rag_config(self) -> dict:
        """Get RAG system configuration"""
        return {
            "vector_db_path": self.vector_db_path,
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "target_success_rate": self.target_success_rate
        }
    
    def get_api_config(self) -> dict:
        """Get API server configuration"""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "debug": self.debug_mode
        }
    
    def get_ui_config(self) -> dict:
        """Get UI configuration with feature flags"""
        return {
            "use_real_llm": self.use_real_llm,
            "default_provider": self.default_provider,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_rps": self.rate_limit_rps,
            "allowlist": self.allowlist
        }

# Global configuration instance
config = Config()

# Export commonly used settings
OPENAI_API_KEY = config.openai_api_key
GOOGLE_GEMINI_API_KEY = config.google_gemini_api_key
ELEVENLABS_API_KEY = config.elevenlabs_api_key
TARGET_SUCCESS_RATE = config.target_success_rate
SYNTHETIC_QUERY_COUNT = config.synthetic_query_count 