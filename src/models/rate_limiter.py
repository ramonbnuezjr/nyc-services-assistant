"""
Rate Limiting System for NYC Services GPT MVP

Implements comprehensive rate limiting for OpenAI APIs with:
- Leaky bucket queue for RPM/TPM limits
- Exponential backoff with jitter
- Token budget tracking
- Model selection logic
- Request caching for development
"""

import os
import time
import math
import json
import random
import hashlib
from typing import Dict, Optional, Any, List
from datetime import datetime, date
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ModelConfig:
    rpm: int  # Requests per minute
    tpm: int  # Tokens per minute
    input_cost: float  # Cost per 1K input tokens
    output_cost: float  # Cost per 1K output tokens

class RateLimiter:
    """
    Production-ready rate limiter for OpenAI APIs in MVP environment.
    
    Features:
    - Leaky bucket queue with sliding window
    - Token budget tracking (daily/monthly)
    - Request caching for development
    - Model selection with premium escalation
    - Exponential backoff with jitter
    """
    
    def __init__(self):
        self.models = {
            "gpt-4o-mini": ModelConfig(
                rpm=int(os.getenv("RPM_MINI", "300")),
                tpm=int(os.getenv("TPM_MINI", "180000")),
                input_cost=0.15,
                output_cost=0.60
            ),
            "gpt-4": ModelConfig(
                rpm=int(os.getenv("RPM_41", "60")),
                tpm=int(os.getenv("TPM_41", "30000")),
                input_cost=5.0,
                output_cost=15.0
            ),
            "text-embedding-ada-002": ModelConfig(
                rpm=int(os.getenv("RPM_EMBED", "3000")),
                tpm=int(os.getenv("TPM_EMBED", "1000000")),
                input_cost=0.10,
                output_cost=0.0
            )
        }
        
        # Usage tracking with sliding window
        self.usage = {model: {"requests": [], "tokens": []} for model in self.models}
        
        # Budget tracking
        self.daily_budget = int(os.getenv("DAILY_TOKEN_BUDGET", "200000"))
        self.monthly_budget = int(os.getenv("MONTHLY_TOKEN_BUDGET", "2000000"))
        self.daily_usage = 0
        self.monthly_usage = 0
        self.current_day = str(date.today())
        self.current_month = datetime.now().strftime("%Y-%m")
        
        # Caching for development
        self.cache = {}
        self.cache_ttl = int(os.getenv("DEV_CACHE_TTL_MS", "600000")) / 1000
        self.is_dev = os.getenv("NODE_ENV", "development") != "production"
        
        # Configuration
        self.allow_premium = os.getenv("ALLOW_PREMIUM", "false").lower() == "true"
        self.max_retries = int(os.getenv("MAX_RETRIES", "4"))
        self.base_delay = float(os.getenv("BASE_RETRY_DELAY", "0.3"))
        self.max_delay = float(os.getenv("MAX_RETRY_DELAY", "60"))
        
        print(f"🔧 Rate limiter initialized - Premium: {self.allow_premium}, Dev mode: {self.is_dev}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        return math.ceil(len(text) / 4)
    
    def choose_model(self, task_hint: str = "", allow_premium: bool = None) -> str:
        """
        Choose appropriate model based on task complexity and premium allowance.
        
        Args:
            task_hint: Hint about task complexity
            allow_premium: Override for premium model usage
            
        Returns:
            Model name to use
        """
        use_premium = (allow_premium if allow_premium is not None else self.allow_premium)
        
        if use_premium and task_hint:
            # Use premium model for complex tasks
            complex_keywords = ["deep", "legal", "multi-step", "strategy", "analysis", "complex"]
            if any(keyword in task_hint.lower() for keyword in complex_keywords):
                return "gpt-4"
        
        return "gpt-4o-mini"
    
    def _rotate_usage_window(self):
        """Clean up usage tracking for sliding window."""
        now = time.time()
        minute_ago = now - 60
        
        for model in self.usage:
            # Remove requests/tokens older than 1 minute
            self.usage[model]["requests"] = [
                ts for ts in self.usage[model]["requests"] if ts > minute_ago
            ]
            self.usage[model]["tokens"] = [
                (ts, count) for ts, count in self.usage[model]["tokens"] if ts > minute_ago
            ]
    
    def _update_budget_tracking(self):
        """Update daily/monthly budget tracking."""
        today = str(date.today())
        this_month = datetime.now().strftime("%Y-%m")
        
        # Reset daily usage if new day
        if today != self.current_day:
            self.current_day = today
            self.daily_usage = 0
        
        # Reset monthly usage if new month
        if this_month != self.current_month:
            self.current_month = this_month
            self.monthly_usage = 0
    
    def can_make_request(self, model: str, estimated_tokens: int) -> bool:
        """
        Check if request can be made within rate limits and budget.
        
        Args:
            model: Model to check
            estimated_tokens: Estimated token usage
            
        Returns:
            True if request can be made
        """
        self._rotate_usage_window()
        self._update_budget_tracking()
        
        if model not in self.models:
            return False
        
        config = self.models[model]
        current_requests = len(self.usage[model]["requests"])
        current_tokens = sum(count for _, count in self.usage[model]["tokens"])
        
        # Check rate limits
        if current_requests >= config.rpm:
            return False
        
        if current_tokens + estimated_tokens > config.tpm:
            return False
        
        # Check budget limits
        if self.daily_usage + estimated_tokens > self.daily_budget:
            print(f"⚠️ Daily token budget ({self.daily_budget}) would be exceeded")
            # Activate mock fallback for budget protection
            from .mock_fallback import mock_fallback
            mock_fallback.activate_fallback("daily_budget_exceeded")
            return False
        
        if self.monthly_usage + estimated_tokens > self.monthly_budget:
            print(f"⚠️ Monthly token budget ({self.monthly_budget}) would be exceeded")
            # Activate mock fallback for budget protection
            from .mock_fallback import mock_fallback
            mock_fallback.activate_fallback("monthly_budget_exceeded")
            return False
        
        return True
    
    def wait_for_capacity(self, model: str, estimated_tokens: int, max_wait: float = 60):
        """
        Wait until capacity is available for the request.
        
        Args:
            model: Model to wait for
            estimated_tokens: Estimated token usage
            max_wait: Maximum time to wait in seconds
        """
        start_time = time.time()
        
        while not self.can_make_request(model, estimated_tokens):
            if time.time() - start_time > max_wait:
                raise Exception(f"Rate limit wait timeout for {model}")
            
            time.sleep(0.1)  # Short sleep between checks
            self._rotate_usage_window()
    
    def record_usage(self, model: str, input_tokens: int, output_tokens: int):
        """
        Record actual API usage for rate limiting and budget tracking.
        
        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated
        """
        now = time.time()
        total_tokens = input_tokens + output_tokens
        
        # Record for rate limiting
        self.usage[model]["requests"].append(now)
        self.usage[model]["tokens"].append((now, total_tokens))
        
        # Update budget tracking
        self.daily_usage += total_tokens
        self.monthly_usage += total_tokens
        
        # Calculate cost
        config = self.models[model]
        cost = (input_tokens * config.input_cost + output_tokens * config.output_cost) / 1000
        
        print(f"📊 API Usage - {model}: {input_tokens}+{output_tokens} tokens, ${cost:.4f}")
    
    def get_cache_key(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Generate cache key for request."""
        cache_data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired."""
        if not self.is_dev or cache_key not in self.cache:
            return None
        
        cached = self.cache[cache_key]
        if time.time() > cached["expires"]:
            del self.cache[cache_key]
            return None
        
        return {**cached["response"], "from_cache": True}
    
    def cache_response(self, cache_key: str, response: Dict):
        """Cache response for development."""
        if self.is_dev:
            self.cache[cache_key] = {
                "response": response,
                "expires": time.time() + self.cache_ttl
            }
    
    def exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        if attempt <= 0:
            return 0
        
        # Exponential backoff: base^attempt
        delay = min(self.max_delay, self.base_delay * (2 ** attempt))
        
        # Add jitter (±20%)
        jitter = random.uniform(-0.2, 0.2) * delay
        
        return max(0, delay + jitter)
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        self._rotate_usage_window()
        self._update_budget_tracking()
        
        stats = {}
        for model, config in self.models.items():
            current_requests = len(self.usage[model]["requests"])
            current_tokens = sum(count for _, count in self.usage[model]["tokens"])
            
            stats[model] = {
                "requests": f"{current_requests}/{config.rpm}",
                "tokens": f"{current_tokens}/{config.tpm}",
                "requests_pct": (current_requests / config.rpm) * 100,
                "tokens_pct": (current_tokens / config.tpm) * 100
            }
        
        stats["budget"] = {
            "daily": f"{self.daily_usage}/{self.daily_budget}",
            "monthly": f"{self.monthly_usage}/{self.monthly_budget}",
            "daily_pct": (self.daily_usage / self.daily_budget) * 100,
            "monthly_pct": (self.monthly_usage / self.monthly_budget) * 100
        }
        
        return stats

# Global rate limiter instance
rate_limiter = RateLimiter()
