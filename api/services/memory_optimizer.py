# Memory Optimization for Render Free Tier (512MB)

import gc
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# Optimize Python memory usage
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Limit worker memory
WORKER_MEMORY_LIMIT = 400  # MB (leave 112MB for system)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager with memory optimization"""
    print("🚀 Starting Angels AI (Memory Optimized for 512MB)")
    
    # Force garbage collection on startup
    gc.collect()
    
    # Configure connection pools to use less memory
    configure_minimal_pools()
    
    yield
    
    # Cleanup on shutdown
    print("🛑 Shutting down...")
    gc.collect()

def configure_minimal_pools():
    """Configure database and HTTP pools for minimal memory"""
    # Database pool: 5 connections max (instead of 20)
    os.environ['DB_POOL_SIZE'] = '5'
    os.environ['DB_MAX_OVERFLOW'] = '2'
    
    # HTTP client pool: 10 connections max
    os.environ['HTTP_POOL_SIZE'] = '10'

def optimize_imports():
    """Lazy import heavy dependencies only when needed"""
    # Don't import pandas/openpyxl until actually used
    # Import them in the route handler, not at module level
    pass

# Uvicorn config for 512MB
def get_uvicorn_config():
    return {
        'host': '0.0.0.0',
        'port': int(os.getenv('PORT', 8000)),
        'workers': 1,  # CRITICAL: Only 1 worker for 512MB
        'limit_concurrency': 50,  # Limit concurrent requests
        'limit_max_requests': 1000,  # Restart worker after 1000 requests (prevent memory leaks)
        'timeout_keep_alive': 5,  # Short keepalive
        'log_level': 'warning',  # Less logging = less memory
        'access_log': False,  # Disable access logging (saves memory)
    }

# Memory monitoring middleware
from starlette.middleware.base import BaseHTTPMiddleware
import psutil

class MemoryMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check memory before request
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        if memory_mb > WORKER_MEMORY_LIMIT:
            # Force garbage collection
            gc.collect()
            print(f"⚠️  Memory high: {memory_mb:.1f}MB - GC triggered")
        
        response = await call_next(request)
        return response

# Optimize pandas usage (lazy loading)
def import_pandas_only_when_needed():
    """Import pandas only in import route, not globally"""
    import pandas as pd
    return pd

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_expensive_operation(key):
    """Cache results to avoid recomputation"""
    pass
