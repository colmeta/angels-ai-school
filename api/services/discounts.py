"""
Sibling Discounts & Payment Plans Service
Automatic discounts for multiple children, installment plans
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from api.services.database import get_db_manager


class DiscountsService:
    """Service for fee discounts and payment plans"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # DISCOUNT RULES MANAGEMENT
    # ============================================================================
    
    def create_discount_rule(
        self,
        rule_name: str,
        discount_type: str,  # sibling, early_payment, scholarship, staff_child
        calculation_method: str,  # percentage, fixed_amount
        discount_value: float,
        conditions: Optional[Dict] = None,
        applicable_to: str = 'all',
        target_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a discount rule
        
        Examples:
        - 2nd child gets 10% discount
        - Pay early get 5% discount
        - Staff children get 50% discount
        """
        query = """
        INSERT INTO fee_discount_rules (
            school_id, rule_name, discount_type, calculation_method,
            discount_value, conditions, applicable_to, target_class
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, rule_name, discount_type, calculation_method,
             discount_value, conditions, applicable_to, target_class),
            fetch=True
        )
        
        return {
            "success": True,
            "rule_id": result[0]['id'],
            "rule_name": rule_name,
            "discount_type": discount_type,
            "discount_value": discount_value
        }
    
    def get_discount_rules(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get all discount rules for school"""
        query = """
        SELECT 
            id, rule_name, discount_type, calculation_method,
            discount_value, conditions, applicable_to, target_class,
            priority, is_active
        FROM fee_discount_rules
        WHERE school_id = %s AND is_active = %s
        ORDER BY priority ASC, created_at DESC
        """
        
        return self.db.execute_query(query, (self.school_id, is_active), fetch=True)
    
    def calculate_sibling_discounts(self, parent_id: str) -> Dict[str, Any]:
        """
        Calculate automatic sibling discounts for a family
        
        Rules:
        - 1st child: 0% discount
        - 2nd child: 10% discount
        - 3rd child: 20% discount
        - 4th+ child: 30% discount
        """
        # Get all children for parent
        children_query = """
        SELECT 
            s.id, s.first_name, s.last_name, s.class_name,
            COALESCE(SUM(sf.balance), 0) as fee_balance
        FROM students s
        JOIN student_parents sp ON sp.student_id = s.id
        LEFT JOIN student_fees sf ON sf.student_id = s.id
        WHERE sp.parent_id = %s AND s.status = 'active'
        GROUP BY s.id, s.first_name, s.last_name, s.class_name
        ORDER BY s.created_at ASC
        """
        
        children = self.db.execute_query(children_query, (parent_id,), fetch=True)
        
        if len(children) <= 1:
            return {
                "success": True,
                "children_count": len(children),
                "total_discount": 0,
                "message": "No sibling discount (only 1 child)"
            }
        
        # Apply discounts
        discounts_applied = []
        total_discount_amount = 0
        
        for i, child in enumerate(children):
            position = i + 1
            discount_percentage = 0
            
            if position == 1:
                discount_percentage = 0
            elif position == 2:
                discount_percentage = 10
            elif position == 3:
                discount_percentage = 20
            else:  # 4th+
                discount_percentage = 30
            
            fee_balance = float(child['fee_balance'])
            discount_amount = fee_balance * (discount_percentage / 100)
            
            if discount_amount > 0:
                # Apply discount to student_fees
                self._apply_discount_to_student(
                    child['id'],
                    discount_amount,
                    f"Sibling discount ({discount_percentage}%) - Child #{position}"
                )
                
                total_discount_amount += discount_amount
            
            discounts_applied.append({
                "student_id": child['id'],
                "student_name": f"{child['first_name']} {child['last_name']}",
                "position": position,
                "discount_percentage": discount_percentage,
                "original_balance": fee_balance,
                "discount_amount": discount_amount,
                "new_balance": fee_balance - discount_amount
            })
        
        return {
            "success": True,
            "children_count": len(children),
            "total_discount_amount": total_discount_amount,
            "discounts_applied": discounts_applied
        }
    
    def apply_early_payment_discount(
        self,
        student_id: str,
        fee_id: str,
        discount_percentage: float = 5.0
    ) -> Dict[str, Any]:
        """
        Apply early payment discount (e.g., 5% if paid before term starts)
        """
        # Get fee details
        fee_query = """
        SELECT balance FROM student_fees WHERE id = %s
        """
        fee = self.db.execute_query(fee_query, (fee_id,), fetch=True)
        
        if not fee:
            return {"success": False, "error": "Fee not found"}
        
        balance = float(fee[0]['balance'])
        discount_amount = balance * (discount_percentage / 100)
        
        # Apply discount
        self._apply_discount_to_student(
            student_id,
            discount_amount,
            f"Early payment discount ({discount_percentage}%)"
        )
        
        return {
            "success": True,
            "discount_amount": discount_amount,
            "new_balance": balance - discount_amount
        }
    
    def _apply_discount_to_student(
        self,
        student_id: str,
        discount_amount: float,
        reason: str
    ) -> None:
        """Apply discount to student's fees"""
        # Record in student_discounts
        query = """
        INSERT INTO student_discounts (
            school_id, student_id, discount_amount, reason
        ) VALUES (%s, %s, %s, %s)
        """
        
        self.db.execute_query(
            query,
            (self.school_id, student_id, discount_amount, reason)
        )
        
        # Update student_fees balance
        update_query = """
        UPDATE student_fees
        SET balance = balance - %s
        WHERE student_id = %s
        """
        
        self.db.execute_query(update_query, (discount_amount, student_id))
    
    # ============================================================================
    # PAYMENT PLANS
    # ============================================================================
    
    def create_payment_plan(
        self,
        student_id: str,
        parent_id: str,
        total_amount: float,
        installment_count: int,
        start_date: str,
        installment_frequency: str = 'monthly'
    ) -> Dict[str, Any]:
        """
        Create installment payment plan
        
        Example: 300,000 UGX in 3 monthly installments
        """
        installment_amount = total_amount / installment_count
        
        # Calculate end date
        if installment_frequency == 'weekly':
            weeks = installment_count
            end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(weeks=weeks)
        elif installment_frequency == 'bi-weekly':
            weeks = installment_count * 2
            end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(weeks=weeks)
        else:  # monthly
            months = installment_count
            end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=months*30)
        
        # Create payment plan
        plan_query = """
        INSERT INTO payment_plans (
            school_id, student_id, parent_id, total_amount, balance,
            installment_count, installment_amount, installment_frequency,
            start_date, end_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            plan_query,
            (self.school_id, student_id, parent_id, total_amount, total_amount,
             installment_count, installment_amount, installment_frequency,
             start_date, end_date.strftime('%Y-%m-%d')),
            fetch=True
        )
        
        plan_id = result[0]['id']
        
        # Create installments
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(1, installment_count + 1):
            # Calculate due date for this installment
            if installment_frequency == 'weekly':
                due_date = current_date + timedelta(weeks=i-1)
            elif installment_frequency == 'bi-weekly':
                due_date = current_date + timedelta(weeks=(i-1)*2)
            else:  # monthly
                due_date = current_date + timedelta(days=(i-1)*30)
            
            installment_query = """
            INSERT INTO payment_plan_installments (
                payment_plan_id, installment_number, due_date, amount_due
            ) VALUES (%s, %s, %s, %s)
            """
            
            self.db.execute_query(
                installment_query,
                (plan_id, i, due_date.strftime('%Y-%m-%d'), installment_amount)
            )
        
        return {
            "success": True,
            "plan_id": plan_id,
            "total_amount": total_amount,
            "installment_count": installment_count,
            "installment_amount": installment_amount,
            "start_date": start_date,
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    
    def get_payment_plans(
        self,
        student_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        status: str = 'active'
    ) -> List[Dict[str, Any]]:
        """Get payment plans"""
        query = """
        SELECT 
            pp.id,
            pp.student_id,
            pp.total_amount,
            pp.amount_paid,
            pp.balance,
            pp.installment_count,
            pp.installment_amount,
            pp.start_date,
            pp.end_date,
            pp.status,
            s.first_name,
            s.last_name
        FROM payment_plans pp
        JOIN students s ON s.id = pp.student_id
        WHERE pp.school_id = %s AND pp.status = %s
        """
        
        params = [self.school_id, status]
        
        if student_id:
            query += " AND pp.student_id = %s"
            params.append(student_id)
        
        if parent_id:
            query += " AND pp.parent_id = %s"
            params.append(parent_id)
        
        query += " ORDER BY pp.created_at DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def record_installment_payment(
        self,
        plan_id: str,
        installment_number: int,
        amount_paid: float
    ) -> Dict[str, Any]:
        """Record payment for an installment"""
        # Update installment
        installment_query = """
        UPDATE payment_plan_installments
        SET amount_paid = amount_paid + %s,
            status = CASE 
                WHEN amount_paid + %s >= amount_due THEN 'paid'
                WHEN amount_paid + %s > 0 THEN 'partial'
                ELSE 'pending'
            END,
            paid_at = CASE 
                WHEN amount_paid + %s >= amount_due THEN CURRENT_TIMESTAMP
                ELSE paid_at
            END
        WHERE payment_plan_id = %s AND installment_number = %s
        RETURNING status
        """
        
        result = self.db.execute_query(
            installment_query,
            (amount_paid, amount_paid, amount_paid, amount_paid, plan_id, installment_number),
            fetch=True
        )
        
        # Update payment plan totals
        plan_query = """
        UPDATE payment_plans
        SET amount_paid = amount_paid + %s,
            balance = balance - %s,
            status = CASE 
                WHEN balance - %s <= 0 THEN 'completed'
                ELSE 'active'
            END
        WHERE id = %s
        """
        
        self.db.execute_query(plan_query, (amount_paid, amount_paid, amount_paid, plan_id))
        
        return {
            "success": True,
            "plan_id": plan_id,
            "installment_number": installment_number,
            "amount_paid": amount_paid,
            "status": result[0]['status'] if result else 'unknown'
        }
    
    def get_overdue_installments(self) -> List[Dict[str, Any]]:
        """Get all overdue installments for reminders"""
        query = """
        SELECT 
            ppi.id,
            ppi.payment_plan_id,
            ppi.installment_number,
            ppi.due_date,
            ppi.amount_due,
            ppi.amount_paid,
            pp.student_id,
            s.first_name,
            s.last_name,
            p.phone as parent_phone
        FROM payment_plan_installments ppi
        JOIN payment_plans pp ON pp.id = ppi.payment_plan_id
        JOIN students s ON s.id = pp.student_id
        JOIN student_parents sp ON sp.student_id = s.id
        JOIN parents p ON p.id = sp.parent_id
        WHERE pp.school_id = %s
        AND ppi.status IN ('pending', 'partial')
        AND ppi.due_date < CURRENT_DATE
        ORDER BY ppi.due_date ASC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)


def get_discounts_service(school_id: str) -> DiscountsService:
    """Helper to get discounts service instance"""
    return DiscountsService(school_id)
