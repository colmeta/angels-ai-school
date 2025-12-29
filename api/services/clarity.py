from __future__ import annotations

from typing import Any, Dict, Optional, List

import httpx

from api.core.config import get_settings
from api.core.mcp import MCPClient, MCPAgentRequest, MCPAgentResponse


class ClarityMCPClient(MCPClient):
    """
    Implementation of MCPClient that uses the official Clarity Cloud API.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.clarity_api_key
        self.base_url = (base_url or str(settings.clarity_base_url)).rstrip("/")
        
        # Validation
        if not self.api_key:
            print("⚠️ WARNING: Clarity API Key not found. ClarityMCPClient may fail.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(45.0, read=90.0), # Increased timeout for complex thoughts
        )

    def analyze(self, request: MCPAgentRequest) -> MCPAgentResponse:
        """
        Translates the MCP request into a specific Clarity API call.
        """
        payload: Dict[str, Any] = {
            "directive": request.directive,
            "domain": request.domain,
            "context": request.context
        }
        if request.files:
            payload["files"] = request.files

        try:
            # Call the actual external API
            response = self._client.post("/instant/analyze", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Map external format to MCP Standard Response
            return MCPAgentResponse(
                success=True,
                content=data, # Clarity returns raw JSON usually
                provider="Clarity Cloud",
                metadata={"status_code": response.status_code}
            )
            
        except httpx.HTTPError as e:
            # Graceful error handling via MCP
            return MCPAgentResponse(
                success=False,
                content=f"Clarity Connection Error: {str(e)}",
                provider="Clarity Cloud (Error)",
                metadata={"error_type": "HttpError"}
            )
        except Exception as e:
             return MCPAgentResponse(
                success=False,
                content=f"Unexpected Error: {str(e)}",
                provider="Clarity Cloud (Error)",
                metadata={"error_type": "Exception"}
            )

    def get_domains(self) -> Dict[str, Any]:
        """Legacy helper specific to Clarity capabilities"""
        try:
            response = self._client.get("/instant/domains")
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"domains": []}

    def health(self) -> Dict[str, Any]:
        try:
            response = self._client.get("/instant/health")
            return {"status": "healthy" if response.is_success else "unhealthy", "code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def close(self) -> None:
        self._client.close()


# ==========================================
# Singleton Setup
# ==========================================
from api.core.mcp import set_mcp_provider

def get_clarity_client() -> ClarityMCPClient:
    """
    Compat helper. Creates the client and ALSO registers it as the global MCP provider.
    This ensures backward compatibility while enforcing the new pattern.
    """
    client = ClarityMCPClient()
    set_mcp_provider(client)
    return client

# Backward alias for generic naming
ClarityClient = ClarityMCPClient
