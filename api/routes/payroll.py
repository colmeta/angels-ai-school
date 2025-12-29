"""
Staff Payroll API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from api.services.payroll import get_payroll_service


router = APIRouter()


class SalaryStructureCreate(BaseModel):
    staff_id: str
    basic_salary: float
    housing_allowance: float = 0.0
    transport_allowance: float = 0.0
    other_allowances: float = 0.0


class PayrollProcess(BaseModel):
    staff_id: str
    month: str
    year: int
    bonus: float = 0.0
    deductions: float = 0.0
    deduction_reason: Optional[str] = None


@router.post("/payroll/salary/create")
async def create_salary_structure(school_id: str, data: SalaryStructureCreate):
    """Create or update salary structure"""
    service = get_payroll_service(school_id)
    return service.create_salary_structure(
        staff_id=data.staff_id,
        basic_salary=data.basic_salary,
        housing_allowance=data.housing_allowance,
        transport_allowance=data.transport_allowance,
        other_allowances=data.other_allowances
    )


@router.post("/payroll/process")
async def process_payroll(school_id: str, data: PayrollProcess):
    """Process monthly payroll"""
    service = get_payroll_service(school_id)
    return service.process_payroll(
        staff_id=data.staff_id,
        month=data.month,
        year=data.year,
        bonus=data.bonus,
        deductions=data.deductions,
        deduction_reason=data.deduction_reason
    )


@router.patch("/payroll/{payroll_id}/mark-paid")
async def mark_as_paid(
    school_id: str,
    payroll_id: str,
    payment_method: str = 'bank_transfer',
    payment_date: Optional[str] = None
):
    """Mark payroll as paid"""
    service = get_payroll_service(school_id)
    return service.mark_as_paid(payroll_id, payment_method, payment_date)


@router.get("/payroll/{payroll_id}/payslip")
async def get_payslip(school_id: str, payroll_id: str):
    """Get payslip"""
    service = get_payroll_service(school_id)
    payslip = service.get_payslip(payroll_id)
    
    if not payslip:
        return {"success": False, "error": "Payslip not found"}
    
    return {"success": True, "payslip": payslip}


@router.get("/payroll/staff/{staff_id}/history")
async def get_payroll_history(school_id: str, staff_id: str, year: Optional[int] = None):
    """Get payroll history for staff"""
    service = get_payroll_service(school_id)
    return {
        "success": True,
        "history": service.get_staff_payroll_history(staff_id, year)
    }


@router.get("/payroll/summary/{month}/{year}")
async def get_monthly_summary(school_id: str, month: str, year: int):
    """Get monthly payroll summary"""
    service = get_payroll_service(school_id)
    return service.get_monthly_payroll_summary(month, year)
