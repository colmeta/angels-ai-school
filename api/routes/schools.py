from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from api.services.database import get_school_ops


class BrandingPayload(BaseModel):
    display_name: str = Field(..., description="Human-friendly school name.")
    primary_color: str = Field(..., description="Primary brand hex color, e.g., #0B69FF.")
    accent_color: str = Field(..., description="Accent brand hex color.")
    logo_url: HttpUrl | None = Field(default=None, description="Public logo URL.")
    favicon_url: HttpUrl | None = Field(default=None, description="Optional favicon URL.")
    hero_image_url: HttpUrl | None = Field(
        default=None, description="Hero image for landing pages (optional)."
    )
    updated_by: str = Field(default="system", description="User or agent making the change.")


class FeatureFlagsPayload(BaseModel):
    enable_parent_chatbot: bool = Field(default=True)
    enable_background_sync: bool = Field(default=True)
    enable_mobile_money_mtn: bool = Field(default=True)
    enable_mobile_money_airtel: bool = Field(default=True)
    enable_student_portal: bool = Field(default=True)
    enable_staff_portal: bool = Field(default=True)
    updated_by: str = Field(default="system")


router = APIRouter(prefix="/{school_id}", tags=["School Configuration"])


@router.get("/branding", summary="Fetch school branding details")
def get_branding(school_id: str) -> Dict[str, Any]:
    ops = get_school_ops()
    return ops.get_branding(school_id)


@router.put("/branding", summary="Update school branding")
def update_branding(school_id: str, payload: BrandingPayload) -> Dict[str, Any]:
    ops = get_school_ops()
    try:
        return ops.upsert_branding(school_id, payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/feature-flags", summary="Fetch school feature flags")
def get_feature_flags(school_id: str) -> Dict[str, Any]:
    ops = get_school_ops()
    return ops.get_feature_flags(school_id)


@router.put("/feature-flags", summary="Update school feature flags")
def update_feature_flags(school_id: str, payload: FeatureFlagsPayload) -> Dict[str, Any]:
    ops = get_school_ops()
    try:
        return ops.upsert_feature_flags(school_id, payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
