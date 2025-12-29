"""
Inventory & Asset Management Service
====================================
Manages School Assets (Fixed & Consumable).
Key Feature: Accounting-grade Depreciation Calculation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from api.services.database import get_db_manager

class InventoryService:
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()

    def add_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new Fixed Asset (e.g., School Bus, Generator).
        """
        query = """
        INSERT INTO assets (
            school_id, name, category, purchase_date, 
            purchase_cost, depreciation_rate, serial_number, 
            location, condition, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        RETURNING id
        """
        cost = float(data.get('purchase_cost', 0))
        rate = float(data.get('depreciation_rate', 0.2)) # Default 20%
        
        result = self.db.execute_query(
            query,
            (self.school_id, data['name'], data['category'], data['purchase_date'], 
             cost, rate, data.get('serial_number'),
             data.get('location'), "new"),
            fetch=True
        )
        return {"success": True, "asset_id": result[0]['id']}

    def get_asset_valuation(self, asset_id: str = None) -> Dict[str, Any]:
        """
        Calculate Current Book Value of Assets using Straight Line Depreciation.
        Formula: Current Value = Cost - (Cost * Rate * Years_Owned)
        """
        # If asset_id provided, get one, else get all for school
        if asset_id:
            query = "SELECT * FROM assets WHERE id = %s AND school_id = %s"
            params = (asset_id, self.school_id)
        else:
            query = "SELECT * FROM assets WHERE school_id = %s AND status = 'active'"
            params = (self.school_id,)

        assets = self.db.execute_query(query, params, fetch=True)
        
        total_original_value = 0
        total_current_value = 0
        evaluated_assets = []
        
        now = datetime.now()
        
        for asset in assets:
            purchase_date = asset['purchase_date']
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
            
            # Calculate Age in Years
            age_days = (now.date() - purchase_date).days if hasattr(purchase_date, 'date') else (now - purchase_date).days
            age_years = max(0, age_days / 365.25)
            
            original_cost = float(asset['purchase_cost'])
            rate = float(asset['depreciation_rate'])
            
            # Calculate Depreciation
            depreciation_amount = original_cost * rate * age_years
            current_value = max(0, original_cost - depreciation_amount)
            
            evaluated_assets.append({
                "id": asset['id'],
                "name": asset['name'],
                "original_cost": original_cost,
                "current_value": round(current_value, 2),
                "age_years": round(age_years, 1),
                "condition": asset['condition']
            })
            
            total_original_value += original_cost
            total_current_value += current_value
            
        return {
            "success": True,
            "total_assets": len(evaluated_assets),
            "total_original_value": round(total_original_value, 2),
            "total_current_value": round(total_current_value, 2),
            "assets": evaluated_assets
        }

    def add_maintenance_log(self, asset_id: str, description: str, cost: float, served_by: str) -> Dict[str, Any]:
        """Log a maintenance event (repair/service)"""
        query = """
        INSERT INTO asset_maintenance (
            school_id, asset_id, description, cost, 
            service_date, serviced_by
        ) VALUES (%s, %s, %s, %s, CURRENT_DATE, %s)
        RETURNING id
        """
        self.db.execute_query(query, (self.school_id, asset_id, description, cost, served_by))
        
        # Update asset condition if needed (optional logic could be added here)
        return {"success": True}
        
    def check_stock_levels(self) -> List[Dict]:
        """Check for low stock items (Consumables)"""
        query = """
        SELECT name, quantity, min_quantity, unit 
        FROM inventory_stock 
        WHERE school_id = %s AND quantity <= min_quantity
        """
        low_stock = self.db.execute_query(query, (self.school_id,), fetch=True)
        return low_stock
