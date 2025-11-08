"""
Sibling Discounts & Payment Plans API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.services.discounts import get_discounts_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class DiscountRuleCreate(BaseModel):
    rule_name: str
    discount_type: str  # sibling, early_payment, scholarship, staff_child
    calculation_method: str  # percentage, fixed_amount
    discount_value: float
    conditions: Optional[Dict[str, Any]] = None
    applicable_to: str = 'all'
    target_class: Optional[str] = None


class PaymentPlanCreate(BaseModel):
    student_id: str
    parent_id: str
    total_amount: float
    installment_count: int
    start_date: str
    installment_frequency: str = 'monthly'


class InstallmentPayment(BaseModel):
    plan_id: str
    installment_number: int
    amount_paid: float


# ============================================================================
# DISCOUNT RULES
# ============================================================================

@router.post("/discounts/rules/create")
async def create_discount_rule(school_id: str, data: DiscountRuleCreate):
    """Create a new discount rule"""
    service = get_discounts_service(school_id)
    return service.create_discount_rule(
        rule_name=data.rule_name,
        discount_type=data.discount_type,
        calculation_method=data.calculation_method,
        discount_value=data.discount_value,
        conditions=data.conditions,
        applicable_to=data.applicable_to,
        target_class=data.target_class
    )


@router.get("/discounts/rules/list")
async def get_discount_rules(school_id: str, is_active: bool = True):
    """Get all discount rules"""
    service = get_discounts_service(school_id)
    return {
        "success": True,
        "rules": service.get_discount_rules(is_active=is_active)
    }


@router.post("/discounts/sibling/calculate")
async def calculate_sibling_discounts(school_id: str, parent_id: str):
    """
    Calculate and apply automatic sibling discounts
    
    Example:
    POST /discounts/sibling/calculate?school_id=abc&parent_id=xyz
    """
    service = get_discounts_service(school_id)
    return service.calculate_sibling_discounts(parent_id)


@router.post("/discounts/early-payment/apply")
async def apply_early_payment_discount(
    school_id: str,
    student_id: str,
    fee_id: str,
    discount_percentage: float = 5.0
):
    """Apply early payment discount"""
    service = get_discounts_service(school_id)
    return service.apply_early_payment_discount(student_id, fee_id, discount_percentage)


# ============================================================================
# PAYMENT PLANS
# ============================================================================

@router.post("/payment-plans/create")
async def create_payment_plan(school_id: str, data: PaymentPlanCreate):
    """
    Create installment payment plan
    
    Example:
    {
      "student_id": "abc",
      "parent_id": "xyz",
      "total_amount": 300000,
      "installment_count": 3,
      "start_date": "2025-02-01",
      "installment_frequency": "monthly"
    }
    """
    service = get_discounts_service(school_id)
    return service.create_payment_plan(
        student_id=data.student_id,
        parent_id=data.parent_id,
        total_amount=data.total_amount,
        installment_count=data.installment_count,
        start_date=data.start_date,
        installment_frequency=data.installment_frequency
    )


@router.get("/payment-plans/list")
async def get_payment_plans(
    school_id: str,
    student_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    status: str = 'active'
):
    """Get payment plans"""
    service = get_discounts_service(school_id)
    return {
        "success": True,
        "plans": service.get_payment_plans(student_id, parent_id, status)
    }


@router.post("/payment-plans/pay-installment")
async def pay_installment(school_id: str, data: InstallmentPayment):
    """
    Record payment for an installment
    
    Example:
    {
      "plan_id": "abc",
      "installment_number": 2,
      "amount_paid": 100000
    }
    """
    service = get_discounts_service(school_id)
    return service.record_installment_payment(
        plan_id=data.plan_id,
        installment_number=data.installment_number,
        amount_paid=data.amount_paid
    )


@router.get("/payment-plans/overdue")
async def get_overdue_installments(school_id: str):
    """Get all overdue installments for sending reminders"""
    service = get_discounts_service(school_id)
    return {
        "success": True,
        "overdue": service.get_overdue_installments()
    }
