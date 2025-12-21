"""
Circuit Breaker for AI Services
===============================
Prevents cascading failures when external AI services (Clarity/OpenAI) are down or slow.
Optimized for 512MB RAM environments (lightweight in-memory state if Redis unavailable).
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
import asyncio

from api.core.config import get_settings

logger = logging.getLogger("angels.circuit")

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit is open (safety mode active)."""
    pass

class CircuitBreaker:
    """
    Manages state of connection to external AI services.
    States: CLOSED (Normal), OPEN (Failing/Safe Mode), HALF-OPEN (Testing recovery)
    """
    
    _failures: int = 0
    _last_failure_time: float = 0
    _state: str = "CLOSED"
    
    # Configuration
    FAILURE_THRESHOLD = 3
    RECOVERY_TIMEOUT = 300  # 5 minutes in "Safe Mode"
    CALL_TIMEOUT = 5  # 5 seconds max for AI call
    
    @classmethod
    def get_state(cls) -> Dict[str, Any]:
        return {
            "state": cls._state,
            "failures": cls._failures,
            "last_failure": cls._last_failure_time
        }

    @classmethod
    def reset(cls):
        cls._failures = 0
        cls._state = "CLOSED"
        logger.info("✅ Circuit Breaker RESET. AI Services active.")

    @classmethod
    async def call(cls, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with circuit breaker protection.
        """
        now = time.time()
        
        # Check if we are in Safe Mode (OPEN state)
        if cls._state == "OPEN":
            if now - cls._last_failure_time > cls.RECOVERY_TIMEOUT:
                logger.info("🌤️ Circuit Breaker HALF-OPEN: Testing service recovery...")
                cls._state = "HALF-OPEN"
            else:
                remaining = int(cls.RECOVERY_TIMEOUT - (now - cls._last_failure_time))
                raise CircuitBreakerOpenException(f"System in Safe Mode. Retry in {remaining}s")

        try:
            # Execute with strict timeout
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=cls.CALL_TIMEOUT)
            
            # Application-level success - reset if previously failing
            if cls._state != "CLOSED":
                cls.reset()
                
            return result
            
        except (asyncio.TimeoutError, Exception) as e:
            cls._failures += 1
            cls._last_failure_time = now
            
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"⚠️ AI Call Failed ({cls._failures}/{cls.FAILURE_THRESHOLD}): {error_msg}")
            
            if cls._failures >= cls.FAILURE_THRESHOLD:
                cls._state = "OPEN"
                logger.error("🚨 Circuit Breaker TRIPPED. Entering Safe Mode (SQL Only).")
            
            raise e

def safe_ai_analytics(fallback_value: Any = None):
    """
    Decorator for AI analysis methods.
    If Circuit Breaker trips or call fails, returns fallback_value instead of crashing.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await CircuitBreaker.call(func, *args, **kwargs)
            except (CircuitBreakerOpenException, asyncio.TimeoutError, Exception) as e:
                logger.warning(f"🛡️ Safe Mode Fallback triggered for {func.__name__}")
                return fallback_value
        return wrapper
    return decorator
