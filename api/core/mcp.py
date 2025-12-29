"""
Model Context Protocol (MCP) Core Abstraction
=============================================
This module defines the standard interface for all AI/Intelligence providers.
By coding to this interface (MCPClient), the rest of the application becomes
agnostic to whether we are using Clarity Cloud, a Local LLM, or OpenAI.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# ==========================================
# Domain Definitions
# ==========================================
class MCPAgentRequest(BaseModel):
    """
    Standardizes the input for any AI agent request.
    """
    directive: str = Field(..., description="The natural language instruction or query.")
    domain: str = Field(..., description="The context domain (e.g., 'financial', 'education').")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional structured data context.")
    files: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional files for analysis.")

class MCPAgentResponse(BaseModel):
    """
    Standardizes the output from any AI agent.
    """
    success: bool = True
    content: Union[Dict[str, Any], str, List[Any]] = Field(..., description="The structured or unstructured result.")
    provider: str = Field(..., description="The name of the provider that handled this request (e.g. 'Clarity', 'LocalLlama').")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Usage stats, confidence scores, etc.")

# ==========================================
# The Contract (Interface)
# ==========================================
class MCPClient(ABC):
    """
    The Model Context Protocol Client Interface.
    All AI providers MUST implement this class.
    """
    
    @abstractmethod
    def analyze(self, request: MCPAgentRequest) -> MCPAgentResponse:
        """
        Process a directive and return intelligence.
        This is the single blocking call for all AI operations.
        """
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Check if the intelligence provider is alive.
        """
        pass
    
    @abstractmethod
    def close(self):
        """
        Cleanup resources.
        """
        pass

# ==========================================
# Factory / Registry
# ==========================================
# This will be populated in main.py or config
_current_provider: Optional[MCPClient] = None

def get_mcp_client() -> MCPClient:
    """
    Returns the currently active MCP Client.
    This creates a singleton-like access pattern for the active AI brain.
    """
    global _current_provider
    if _current_provider is None:
        raise RuntimeError("MCP Provider has not been initialized. Call initialize_mcp() first.")
    return _current_provider

def set_mcp_provider(provider: MCPClient):
    """
    Switches the active brain of the application.
    This is how we switch from 'Clarity' to 'Local' dynamically.
    """
    global _current_provider
    _current_provider = provider
