"""
Experiments API Routes
Manage A/B tests and feature flags via REST API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from api.services.feature_flags import (
    get_feature_flag_service,
    FeatureFlag,
    Experiment,
    ExperimentStatus
)

router = APIRouter(prefix="/api/v1/experiments", tags=["A/B Testing"])


class CreateExperimentRequest(BaseModel):
    name: str
    description: str
    variants: List[str]
    traffic_split: List[int]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UpdateExperimentRequest(BaseModel):
    status: Optional[str] = None
    traffic_split: Optional[List[int]] = None


class CheckFeatureFlagRequest(BaseModel):
    flag_name: str
    user_id: int
    school_id: Optional[int] = None
    role: Optional[str] = None


class GetVariantRequest(BaseModel):
    experiment_name: str
    user_id: int


class TrackEventRequest(BaseModel):
    experiment_name: str
    user_id: int
    event_type: str  # "exposure" or "conversion"
    metric_name: Optional[str] = None
    value: Optional[Any] = None


@router.get("/list")
async def list_experiments():
    """Get all experiments"""
    service = get_feature_flag_service()
    return {
        "experiments": service.get_all_experiments(),
        "flags": service.get_all_flags()
    }


@router.post("/create")
async def create_experiment(request: CreateExperimentRequest):
    """Create a new A/B test experiment"""
    try:
        experiment = Experiment(
            name=request.name,
            description=request.description,
            variants=request.variants,
            traffic_split=request.traffic_split,
            status=ExperimentStatus.DRAFT,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        service = get_feature_flag_service()
        service.register_experiment(experiment)
        
        return {
            "success": True,
            "experiment_name": request.name,
            "message": "Experiment created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{experiment_name}/activate")
async def activate_experiment(experiment_name: str):
    """Activate an experiment"""
    service = get_feature_flag_service()
    
    if experiment_name not in service.experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = service.experiments[experiment_name]
    experiment.status = ExperimentStatus.ACTIVE
    
    return {
        "success": True,
        "message": f"Experiment '{experiment_name}' activated"
    }


@router.post("/{experiment_name}/pause")
async def pause_experiment(experiment_name: str):
    """Pause an experiment"""
    service = get_feature_flag_service()
    
    if experiment_name not in service.experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = service.experiments[experiment_name]
    experiment.status = ExperimentStatus.PAUSED
    
    return {
        "success": True,
        "message": f"Experiment '{experiment_name}' paused"
    }


@router.post("/{experiment_name}/complete")
async def complete_experiment(experiment_name: str):
    """Mark experiment as completed"""
    service = get_feature_flag_service()
    
    if experiment_name not in service.experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = service.experiments[experiment_name]
    experiment.status = ExperimentStatus.COMPLETED
    
    return {
        "success": True,
        "message": f"Experiment '{experiment_name}' completed"
    }


@router.post("/check-flag")
async def check_feature_flag(request: CheckFeatureFlagRequest):
    """Check if feature flag is enabled for user"""
    service = get_feature_flag_service()
    
    is_enabled = service.is_enabled(
        request.flag_name,
        request.user_id,
        request.school_id,
        request.role
    )
    
    return {
        "flag_name": request.flag_name,
        "enabled": is_enabled,
        "user_id": request.user_id
    }


@router.post("/get-variant")
async def get_variant(request: GetVariantRequest):
    """Get experiment variant for user"""
    service = get_feature_flag_service()
    
    variant = service.get_variant(
        request.experiment_name,
        request.user_id
    )
    
    # Track exposure
    service.track_exposure(
        request.experiment_name,
        request.user_id,
        variant
    )
    
    return {
        "experiment_name": request.experiment_name,
        "variant": variant,
        "user_id": request.user_id
    }


@router.post("/track")
async def track_event(request: TrackEventRequest):
    """Track experiment event (exposure/conversion)"""
    service = get_feature_flag_service()
    
    if request.event_type == "exposure":
        variant = service.get_variant(request.experiment_name, request.user_id)
        service.track_exposure(
            request.experiment_name,
            request.user_id,
            variant
        )
    elif request.event_type == "conversion":
        service.track_conversion(
            request.experiment_name,
            request.user_id,
            request.metric_name or "default",
            request.value
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid event_type")
    
    return {
        "success": True,
        "message": "Event tracked successfully"
    }


@router.get("/{experiment_name}/analytics")
async def get_experiment_analytics(experiment_name: str):
    """Get analytics for experiment"""
    service = get_feature_flag_service()
    
    if experiment_name not in service.experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # In production, this would query analytics database
    # For now, return placeholder data
    return {
        "experiment_name": experiment_name,
        "total_participants": 0,
        "variant_breakdown": {},
        "conversion_rates": {},
        "message": "Analytics collection in progress"
    }
