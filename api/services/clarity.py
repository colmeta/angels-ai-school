from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from api.core.config import get_settings


class ClarityClient:
    """HTTP client for interacting with the Clarity Engine."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.clarity_api_key
        self.base_url = (base_url or str(settings.clarity_base_url)).rstrip("/")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(30.0, read=60.0),
        )

    def analyze(self, directive: str, domain: str, files: Optional[list] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "directive": directive,
            "domain": domain,
        }
        if files:
            payload["files"] = files

        response = self._client.post("/instant/analyze", json=payload)
        response.raise_for_status()
        return response.json()

    def get_domains(self) -> Dict[str, Any]:
        response = self._client.get("/instant/domains")
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        response = self._client.get("/instant/health")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()


def get_clarity_client() -> ClarityClient:
    """Helper to create a Clarity client when needed."""
    return ClarityClient()
