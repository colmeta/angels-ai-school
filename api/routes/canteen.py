"""
Canteen/Tuck Shop API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.services.canteen import get_canteen_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ItemAdd(BaseModel):
    item_name: str
    price: float
    category: str  # food, drinks, snacks, stationery, uniform
    stock_quantity: int = 0
    reorder_level: Optional[int] = 10


class StockUpdate(BaseModel):
    quantity_change: int
    operation: str = 'add'  # add or subtract


class FundsAdd(BaseModel):
    student_id: str
    amount: float
    payment_method: str = 'cash'


class PurchaseRecord(BaseModel):
    student_id: str
    items: List[Dict[str, Any]]  # [{item_id: "abc", quantity: 2}]


# ============================================================================
# ITEM INVENTORY
# ============================================================================

@router.post("/canteen/items/add")
async def add_item(school_id: str, data: ItemAdd):
    """Add item to canteen inventory"""
    service = get_canteen_service(school_id)
    return service.add_item(
        item_name=data.item_name,
        price=data.price,
        category=data.category,
        stock_quantity=data.stock_quantity,
        reorder_level=data.reorder_level
    )


@router.patch("/canteen/items/{item_id}/price")
async def update_price(school_id: str, item_id: str, new_price: float):
    """Update item price"""
    service = get_canteen_service(school_id)
    return service.update_item_price(item_id, new_price)


@router.patch("/canteen/items/{item_id}/stock")
async def update_stock(school_id: str, item_id: str, data: StockUpdate):
    """Update item stock"""
    service = get_canteen_service(school_id)
    return service.update_stock(item_id, data.quantity_change, data.operation)


@router.get("/canteen/items/list")
async def get_items(
    school_id: str,
    category: Optional[str] = None,
    in_stock_only: bool = False
):
    """Get all canteen items"""
    service = get_canteen_service(school_id)
    return {
        "success": True,
        "items": service.get_items(category, in_stock_only)
    }


@router.get("/canteen/items/low-stock")
async def get_low_stock(school_id: str):
    """Get items below reorder level"""
    service = get_canteen_service(school_id)
    return {
        "success": True,
        "low_stock_items": service.get_low_stock_items()
    }


# ============================================================================
# STUDENT ACCOUNTS
# ============================================================================

@router.post("/canteen/accounts/create")
async def create_account(school_id: str, student_id: str, initial_balance: float = 0.0):
    """Create canteen account for student"""
    service = get_canteen_service(school_id)
    return service.create_student_account(student_id, initial_balance)


@router.post("/canteen/accounts/add-funds")
async def add_funds(school_id: str, data: FundsAdd):
    """Add funds to student account"""
    service = get_canteen_service(school_id)
    return service.add_funds(
        student_id=data.student_id,
        amount=data.amount,
        payment_method=data.payment_method
    )


@router.get("/canteen/accounts/student/{student_id}/balance")
async def get_balance(school_id: str, student_id: str):
    """Get student canteen balance"""
    service = get_canteen_service(school_id)
    return service.get_student_balance(student_id)


# ============================================================================
# PURCHASES
# ============================================================================

@router.post("/canteen/purchases/record")
async def record_purchase(school_id: str, data: PurchaseRecord):
    """
    Record canteen purchase
    
    Example:
    {
      "student_id": "abc",
      "items": [
        {"item_id": "item1", "quantity": 2},
        {"item_id": "item2", "quantity": 1}
      ]
    }
    """
    service = get_canteen_service(school_id)
    return service.record_purchase(data.student_id, data.items)


@router.get("/canteen/purchases/student/{student_id}/history")
async def get_purchase_history(school_id: str, student_id: str, limit: int = 50):
    """Get purchase history for a student"""
    service = get_canteen_service(school_id)
    return {
        "success": True,
        "purchases": service.get_student_purchase_history(student_id, limit)
    }


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/canteen/analytics/daily-sales")
async def get_daily_sales(school_id: str, date: str):
    """Get daily sales summary"""
    service = get_canteen_service(school_id)
    return service.get_daily_sales(date)


@router.get("/canteen/analytics/popular-items")
async def get_popular_items(school_id: str, days: int = 7):
    """Get most popular items"""
    service = get_canteen_service(school_id)
    return {
        "success": True,
        "popular_items": service.get_popular_items(days)
    }


@router.get("/canteen/analytics/low-balance-students")
async def get_low_balance_students(school_id: str, threshold: float = 5000.0):
    """Get students with low balance"""
    service = get_canteen_service(school_id)
    return {
        "success": True,
        "students": service.get_students_with_low_balance(threshold)
    }
