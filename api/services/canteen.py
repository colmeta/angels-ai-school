"""
Canteen/Tuck Shop Service
Student accounts, purchases, balances, item inventory
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from api.services.database import get_db_manager


class CanteenService:
    """Service for canteen/tuck shop management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # ITEM INVENTORY MANAGEMENT
    # ============================================================================
    
    def add_item(
        self,
        item_name: str,
        price: float,
        category: str,  # food, drinks, snacks, stationery, uniform
        stock_quantity: int = 0,
        reorder_level: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Add item to canteen inventory"""
        query = """
        INSERT INTO canteen_items (
            school_id, item_name, price, category, stock_quantity, reorder_level
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, item_name, price, category, stock_quantity, reorder_level),
            fetch=True
        )
        
        return {
            "success": True,
            "item_id": result[0]['id'],
            "item_name": item_name,
            "price": price
        }
    
    def update_item_price(self, item_id: str, new_price: float) -> Dict[str, Any]:
        """Update item price"""
        query = """
        UPDATE canteen_items
        SET price = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        self.db.execute_query(query, (new_price, item_id, self.school_id))
        
        return {"success": True, "item_id": item_id, "new_price": new_price}
    
    def update_stock(
        self,
        item_id: str,
        quantity_change: int,
        operation: str = 'add'  # add or subtract
    ) -> Dict[str, Any]:
        """Update item stock"""
        if operation == 'add':
            query = """
            UPDATE canteen_items
            SET stock_quantity = stock_quantity + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND school_id = %s
            RETURNING stock_quantity
            """
        else:  # subtract
            query = """
            UPDATE canteen_items
            SET stock_quantity = stock_quantity - %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND school_id = %s AND stock_quantity >= %s
            RETURNING stock_quantity
            """
        
        params = (quantity_change, item_id, self.school_id, quantity_change) if operation == 'subtract' else (quantity_change, item_id, self.school_id)
        result = self.db.execute_query(query, params, fetch=True)
        
        if not result:
            return {"success": False, "error": "Insufficient stock"}
        
        return {
            "success": True,
            "item_id": item_id,
            "new_stock": result[0]['stock_quantity']
        }
    
    def get_items(
        self,
        category: Optional[str] = None,
        in_stock_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all canteen items"""
        query = """
        SELECT 
            id, item_name, price, category, stock_quantity, reorder_level, is_active
        FROM canteen_items
        WHERE school_id = %s
        """
        
        params = [self.school_id]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if in_stock_only:
            query += " AND stock_quantity > 0"
        
        query += " ORDER BY category, item_name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get items below reorder level"""
        query = """
        SELECT 
            id, item_name, category, stock_quantity, reorder_level
        FROM canteen_items
        WHERE school_id = %s
        AND is_active = true
        AND stock_quantity <= reorder_level
        ORDER BY stock_quantity ASC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    # ============================================================================
    # STUDENT ACCOUNTS
    # ============================================================================
    
    def create_student_account(
        self,
        student_id: str,
        initial_balance: float = 0.0
    ) -> Dict[str, Any]:
        """Create canteen account for student"""
        query = """
        INSERT INTO student_canteen_accounts (school_id, student_id, balance)
        VALUES (%s, %s, %s)
        ON CONFLICT (student_id) DO NOTHING
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, initial_balance),
            fetch=True
        )
        
        return {
            "success": True,
            "account_id": result[0]['id'] if result else None,
            "student_id": student_id,
            "balance": initial_balance
        }
    
    def add_funds(
        self,
        student_id: str,
        amount: float,
        payment_method: str = 'cash'
    ) -> Dict[str, Any]:
        """Add funds to student account (top-up)"""
        # Update balance
        query = """
        UPDATE student_canteen_accounts
        SET balance = balance + %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = %s
        RETURNING balance
        """
        
        result = self.db.execute_query(query, (amount, student_id), fetch=True)
        
        if not result:
            return {"success": False, "error": "Account not found"}
        
        new_balance = float(result[0]['balance'])
        
        return {
            "success": True,
            "student_id": student_id,
            "amount_added": amount,
            "new_balance": new_balance,
            "payment_method": payment_method
        }
    
    def get_student_balance(self, student_id: str) -> Dict[str, Any]:
        """Get student canteen balance"""
        query = """
        SELECT balance FROM student_canteen_accounts WHERE student_id = %s
        """
        
        result = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not result:
            return {"success": False, "error": "Account not found"}
        
        return {
            "success": True,
            "student_id": student_id,
            "balance": float(result[0]['balance'])
        }
    
    # ============================================================================
    # PURCHASES
    # ============================================================================
    
    def record_purchase(
        self,
        student_id: str,
        items: List[Dict[str, Any]]  # [{item_id: "abc", quantity: 2}]
    ) -> Dict[str, Any]:
        """Record canteen purchase"""
        # Get student balance
        balance_query = """
        SELECT balance FROM student_canteen_accounts WHERE student_id = %s
        """
        balance_result = self.db.execute_query(balance_query, (student_id,), fetch=True)
        
        if not balance_result:
            return {"success": False, "error": "Student account not found"}
        
        current_balance = float(balance_result[0]['balance'])
        
        # Calculate total cost and check stock
        total_cost = 0.0
        purchase_items = []
        
        for item in items:
            item_query = """
            SELECT id, item_name, price, stock_quantity
            FROM canteen_items
            WHERE id = %s AND school_id = %s
            """
            item_result = self.db.execute_query(item_query, (item['item_id'], self.school_id), fetch=True)
            
            if not item_result:
                return {"success": False, "error": f"Item {item['item_id']} not found"}
            
            item_data = item_result[0]
            quantity = item['quantity']
            
            if item_data['stock_quantity'] < quantity:
                return {
                    "success": False,
                    "error": f"Insufficient stock for {item_data['item_name']}. Available: {item_data['stock_quantity']}"
                }
            
            item_total = float(item_data['price']) * quantity
            total_cost += item_total
            
            purchase_items.append({
                "item_id": item['item_id'],
                "item_name": item_data['item_name'],
                "quantity": quantity,
                "unit_price": float(item_data['price']),
                "total": item_total
            })
        
        # Check if student has enough balance
        if current_balance < total_cost:
            return {
                "success": False,
                "error": "Insufficient balance",
                "required": total_cost,
                "available": current_balance,
                "shortfall": total_cost - current_balance
            }
        
        # Record purchase
        for item in purchase_items:
            purchase_query = """
            INSERT INTO canteen_purchases (
                school_id, student_id, item_id, quantity, unit_price, total_amount
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_query(
                purchase_query,
                (self.school_id, student_id, item['item_id'], item['quantity'],
                 item['unit_price'], item['total'])
            )
            
            # Update stock
            self.update_stock(item['item_id'], item['quantity'], 'subtract')
        
        # Deduct from balance
        deduct_query = """
        UPDATE student_canteen_accounts
        SET balance = balance - %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = %s
        RETURNING balance
        """
        
        new_balance_result = self.db.execute_query(
            deduct_query,
            (total_cost, student_id),
            fetch=True
        )
        
        new_balance = float(new_balance_result[0]['balance'])
        
        return {
            "success": True,
            "student_id": student_id,
            "items_purchased": purchase_items,
            "total_cost": total_cost,
            "previous_balance": current_balance,
            "new_balance": new_balance
        }
    
    def get_student_purchase_history(
        self,
        student_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get purchase history for a student"""
        query = """
        SELECT 
            cp.id,
            cp.purchased_at,
            ci.item_name,
            cp.quantity,
            cp.unit_price,
            cp.total_amount
        FROM canteen_purchases cp
        JOIN canteen_items ci ON ci.id = cp.item_id
        WHERE cp.student_id = %s
        ORDER BY cp.purchased_at DESC
        LIMIT %s
        """
        
        return self.db.execute_query(query, (student_id, limit), fetch=True)
    
    # ============================================================================
    # ANALYTICS & REPORTS
    # ============================================================================
    
    def get_daily_sales(self, date: str) -> Dict[str, Any]:
        """Get daily sales summary"""
        query = """
        SELECT 
            COUNT(DISTINCT student_id) as unique_customers,
            COUNT(*) as total_transactions,
            SUM(total_amount) as total_sales
        FROM canteen_purchases
        WHERE school_id = %s
        AND DATE(purchased_at) = %s
        """
        
        result = self.db.execute_query(query, (self.school_id, date), fetch=True)
        
        return {
            "success": True,
            "date": date,
            "statistics": result[0] if result else {}
        }
    
    def get_popular_items(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get most popular items"""
        query = """
        SELECT 
            ci.item_name,
            ci.category,
            SUM(cp.quantity) as total_sold,
            SUM(cp.total_amount) as revenue
        FROM canteen_purchases cp
        JOIN canteen_items ci ON ci.id = cp.item_id
        WHERE cp.school_id = %s
        AND cp.purchased_at >= CURRENT_DATE - %s
        GROUP BY ci.id, ci.item_name, ci.category
        ORDER BY total_sold DESC
        LIMIT 10
        """
        
        return self.db.execute_query(query, (self.school_id, days), fetch=True)
    
    def get_students_with_low_balance(self, threshold: float = 5000.0) -> List[Dict[str, Any]]:
        """Get students with low canteen balance"""
        query = """
        SELECT 
            sca.student_id,
            sca.balance,
            s.first_name,
            s.last_name,
            s.class_name
        FROM student_canteen_accounts sca
        JOIN students s ON s.id = sca.student_id
        WHERE sca.school_id = %s
        AND sca.balance < %s
        ORDER BY sca.balance ASC
        """
        
        return self.db.execute_query(query, (self.school_id, threshold), fetch=True)


def get_canteen_service(school_id: str) -> CanteenService:
    """Helper to get canteen service instance"""
    return CanteenService(school_id)
