"""
Fee Management Endpoints
"""
from fastapi import APIRouter, HTTPException
from financial_operations_service import FinancialOperationsService

router = APIRouter()

@router.get("/ooda-loop/{school_id}")
async def run_financial_ooda_loop(school_id: str):
    """Run Financial OODA Loop"""
    try:
        service = FinancialOperationsService(school_id)
        result = service.run_ooda_loop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{school_id}")
async def get_financial_report(school_id: str):
    """Get financial report"""
    try:
        service = FinancialOperationsService(school_id)
        report = service.generate_daily_financial_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection-summary/{school_id}")
async def get_collection_summary(school_id: str):
    """Get fee collection summary"""
    try:
        service = FinancialOperationsService(school_id)
        summary = service.fee_ops.get_fee_collection_summary(school_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
