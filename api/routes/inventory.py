"""
Inventory API Routes
====================
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from api.services.inventory import InventoryService

router = APIRouter()

class AssetCreate(BaseModel):
    name: str
    category: str
    purchase_date: str # YYYY-MM-DD
    purchase_cost: float
    depreciation_rate: float = 0.20
    serial_number: Optional[str] = None
    location: Optional[str] = None

@router.post("/{school_id}/inventory/assets")
async def register_asset(school_id: str, asset: AssetCreate):
    """Register a new fixed asset"""
    service = InventoryService(school_id)
    return service.add_asset(asset.dict())

@router.get("/{school_id}/inventory/valuation")
async def get_valuation_report(school_id: str):
    """Get full asset valuation report with depreciation"""
    service = InventoryService(school_id)
    return service.get_asset_valuation()

@router.get("/{school_id}/inventory/alerts")
async def get_stock_alerts(school_id: str):
    """Get low stock alerts"""
    service = InventoryService(school_id)
    alerts = service.check_stock_levels()
    return {"success": True, "alerts": alerts}
