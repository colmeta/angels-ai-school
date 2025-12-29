from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, condecimal

from api.services.mobile_money import MobileMoneyService, SUPPORTED_PROVIDERS


class InitiateMobileMoneyRequest(BaseModel):
    school_id: str = Field(..., description="School identifier.")
    provider: str = Field(..., description="Either MTN or Airtel.")
    amount: condecimal(gt=0) = Field(..., description="Amount to collect.")
    currency: str = Field(default="UGX")
    phone_number: str = Field(..., description="Parent or payer MSISDN.")
    student_id: Optional[str] = Field(default=None)
    student_fee_id: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = None
    initiated_by: Optional[str] = Field(default="system")


class CallbackPayload(BaseModel):
    school_id: str
    provider: str
    reference: str
    status: str
    amount: Optional[condecimal(gt=0)] = None
    external_reference: Optional[str] = None
    message: Optional[str] = None


router = APIRouter(prefix="/mobile-money", tags=["Mobile Money"])


@router.post("/initiate")
def initiate_mobile_money(payload: InitiateMobileMoneyRequest):
    try:
        service = MobileMoneyService(payload.school_id)
        return service.initiate_payment(
            provider=payload.provider,
            amount=Decimal(payload.amount),
            currency=payload.currency,
            msisdn=payload.phone_number,
            student_id=payload.student_id,
            student_fee_id=payload.student_fee_id,
            metadata=payload.metadata,
            initiated_by=payload.initiated_by or "system",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/callback")
def mobile_money_callback(payload: CallbackPayload):
    try:
        service = MobileMoneyService(payload.school_id)
        return service.acknowledge_callback(
            provider=payload.provider,
            reference=payload.reference,
            status=payload.status,
            amount=Decimal(payload.amount) if payload.amount is not None else None,
            external_reference=payload.external_reference,
            message=payload.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/transactions")
def list_transactions(
    school_id: str = Query(..., description="School identifier."),
    student_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        service = MobileMoneyService(school_id)
        return {
            "success": True,
            "transactions": service.list_transactions(student_id=student_id, limit=limit),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/status/{reference}")
def poll_status(reference: str, school_id: str = Query(...)):
    try:
        service = MobileMoneyService(school_id)
        transaction = service.poll_transaction(reference)
        return {"success": True, "transaction": transaction}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/report")
def mobile_money_report(school_id: str = Query(...)):
    try:
        service = MobileMoneyService(school_id)
        return service.generate_offline_report()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/providers")
def list_providers():
    return {"providers": sorted(SUPPORTED_PROVIDERS)}
