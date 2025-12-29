"""
Memory monitoring middleware for 512MB RAM optimization
"""
import psutil
import gc
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class MemoryMonitorMiddleware(BaseHTTPMiddleware):
    """Monitor and optimize memory usage for Render 512MB free tier"""
    
    def __init__(self, app, max_memory_mb: int = 400):
        super().__init__(app)
        self.max_memory_mb = max_memory_mb
        self.request_count = 0
        
    async def dispatch(self, request: Request, call_next):
        # Check memory before processing
        memory_mb = self._get_memory_usage()
        
        # Auto garbage collect if memory is high
        if memory_mb > self.max_memory_mb * 0.8:  # 80% threshold
            logger.warning(f"High memory usage: {memory_mb}MB, running GC")
            gc.collect()
        
        # Process request
        response = await call_next(request)
        
        # Periodic GC every 100 requests
        self.request_count += 1
        if self.request_count % 100 == 0:
            gc.collect()
            logger.info(f"Periodic GC at request {self.request_count}, memory: {self._get_memory_usage()}MB")
        
        # Add memory header for monitoring
        response.headers["X-Memory-Usage-MB"] = str(int(memory_mb))
        
        # Emergency GC if memory is critical
        if memory_mb > self.max_memory_mb:
            logger.error(f"CRITICAL: Memory at {memory_mb}MB, forcing GC")
            gc.collect()
        
        return response
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert to MB
        except:
            return 0.0

def get_memory_stats():
    """Get detailed memory statistics"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": round(memory_info.rss / (1024 * 1024), 2),
            "vms_mb": round(memory_info.vms / (1024 * 1024), 2),
            "percent": round(process.memory_percent(), 2),
            "available_mb": round(psutil.virtual_memory().available / (1024 * 1024), 2)
        }
    except:
        return {"error": "Unable to get memory stats"}
