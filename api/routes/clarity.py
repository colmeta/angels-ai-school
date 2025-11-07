from typing import Any, Dict, Optional

import httpx

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.services.clarity import ClarityClient, get_clarity_client


class AnalyzeRequest(BaseModel):
    directive: str = Field(..., description="The instruction or brief for Clarity to analyze.")
    domain: str = Field(
        ...,
        description="Clarity domain to target (e.g., financial, education, legal, security).",
    )
    files: Optional[list[Dict[str, Any]]] = Field(
        default=None,
        description="Optional file payloads for document analysis.",
    )


router = APIRouter()


@router.get("/health", summary="Check Clarity availability")
def clarity_health(client: ClarityClient = Depends(get_clarity_client)) -> Dict[str, Any]:
    try:
        return client.health()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Clarity health check failed: {exc}") from exc
    finally:
        client.close()


@router.get("/domains", summary="List supported Clarity domains")
def clarity_domains(client: ClarityClient = Depends(get_clarity_client)) -> Dict[str, Any]:
    try:
        return client.get_domains()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch domains: {exc}") from exc
    finally:
        client.close()


@router.post("/analyze", summary="Proxy analyze requests to Clarity")
def clarity_analyze(
    payload: AnalyzeRequest,
    client: ClarityClient = Depends(get_clarity_client),
) -> Dict[str, Any]:
    try:
        return client.analyze(payload.directive, payload.domain, files=payload.files)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json() if exc.response else str(exc)
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Clarity analyze failed: {exc}") from exc
    finally:
        client.close()
