"""
Staff Payroll Service
Salary management, deductions, bonuses, payslips, tax calculation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from api.services.database import get_db_manager


class PayrollService:
    """Service for staff payroll management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    def create_salary_structure(
        self,
        staff_id: str,
        basic_salary: float,
        housing_allowance: float = 0.0,
        transport_allowance: float = 0.0,
        other_allowances: float = 0.0
    ) -> Dict[str, Any]:
        """Create or update salary structure for staff"""
        gross_salary = basic_salary + housing_allowance + transport_allowance + other_allowances
        
        query = """
        INSERT INTO staff_salaries (
            school_id, staff_id, basic_salary, housing_allowance,
            transport_allowance, other_allowances, gross_salary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (staff_id) DO UPDATE
        SET basic_salary = EXCLUDED.basic_salary,
            housing_allowance = EXCLUDED.housing_allowance,
            transport_allowance = EXCLUDED.transport_allowance,
            other_allowances = EXCLUDED.other_allowances,
            gross_salary = EXCLUDED.gross_salary,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, staff_id, basic_salary, housing_allowance,
             transport_allowance, other_allowances, gross_salary),
            fetch=True
        )
        
        return {
            "success": True,
            "salary_id": result[0]['id'],
            "staff_id": staff_id,
            "gross_salary": gross_salary
        }
    
    def process_payroll(
        self,
        staff_id: str,
        month: str,
        year: int,
        bonus: float = 0.0,
        deductions: float = 0.0,
        deduction_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process monthly payroll for a staff member"""
        from api.services.tax_engine import TaxEngine
        
        # Get salary structure
        salary_query = """
        SELECT gross_salary FROM staff_salaries WHERE staff_id = %s
        """
        salary_result = self.db.execute_query(salary_query, (staff_id,), fetch=True)
        
        if not salary_result:
            return {"success": False, "error": "Salary structure not found"}
        
        gross_salary = float(salary_result[0]['gross_salary'])
        taxable_income = gross_salary + bonus # Bonuses are taxable
        
        # Use Enterprise Tax Engine
        engine = TaxEngine() # Defaults to UG config
        
        # 1. Calculate NSSF (5% Employee, 10% Employer)
        nssf_breakdown = engine.calculate_nssf(gross_salary) # NSSF usually on basic+allowances (gross)
        nssf_employee = nssf_breakdown["employee"]
        nssf_employer = nssf_breakdown["employer"]
        
        # 2. Calculate PAYE
        paye = engine.calculate_paye(taxable_income)
        
        # 3. Net Salary
        # Net = (Gross + Bonus) - (PAYE + NSSF_Employee + Other Deductions)
        net_salary = taxable_income - paye - nssf_employee - deductions
        
        # Record transaction (Now storing employer NSSF too if schema supports, else just log)
        # We will stick to the existing schema for now but update logic
        query = """
        INSERT INTO payroll_transactions (
            school_id, staff_id, month, year, gross_salary, bonus,
            deductions, deduction_reason, paye_tax, nssf, net_salary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, staff_id, month, year, gross_salary, bonus,
             deductions, deduction_reason, paye, nssf_employee, net_salary),
            fetch=True
        )
        
        return {
            "success": True,
            "payroll_id": result[0]['id'],
            "staff_id": staff_id,
            "month": month,
            "year": year,
            "breakdown": {
                "gross_salary": gross_salary,
                "bonus": bonus,
                "gross_taxable": taxable_income,
                "deductions": deductions,
                "paye_tax": paye,
                "nssf_employee": nssf_employee,
                "nssf_employer": nssf_employer, # Bonus info
                "net_salary": net_salary
            }
        }
    
    def mark_as_paid(
        self,
        payroll_id: str,
        payment_method: str = 'bank_transfer',
        payment_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark payroll as paid"""
        query = """
        UPDATE payroll_transactions
        SET payment_status = 'paid',
            payment_method = %s,
            payment_date = COALESCE(%s, CURRENT_DATE)
        WHERE id = %s
        """
        
        self.db.execute_query(query, (payment_method, payment_date, payroll_id))
        
        return {"success": True, "payroll_id": payroll_id, "status": "paid"}
    
    def get_payslip(self, payroll_id: str) -> Optional[Dict[str, Any]]:
        """Get payslip details"""
        query = """
        SELECT 
            pt.*,
            t.first_name,
            t.last_name,
            t.employee_id
        FROM payroll_transactions pt
        JOIN teachers t ON t.id = pt.staff_id
        WHERE pt.id = %s
        """
        
        result = self.db.execute_query(query, (payroll_id,), fetch=True)
        return result[0] if result else None
    
    def get_staff_payroll_history(
        self,
        staff_id: str,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get payroll history for a staff member"""
        query = """
        SELECT 
            id, month, year, gross_salary, bonus, deductions,
            paye_tax, nssf, net_salary, payment_status, payment_date
        FROM payroll_transactions
        WHERE staff_id = %s
        """
        
        params = [staff_id]
        
        if year:
            query += " AND year = %s"
            params.append(year)
        
        query += " ORDER BY year DESC, month DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_monthly_payroll_summary(self, month: str, year: int) -> Dict[str, Any]:
        """Get payroll summary for a month"""
        query = """
        SELECT 
            COUNT(*) as staff_count,
            SUM(gross_salary) as total_gross,
            SUM(bonus) as total_bonus,
            SUM(deductions) as total_deductions,
            SUM(paye_tax) as total_paye,
            SUM(nssf) as total_nssf,
            SUM(net_salary) as total_net,
            COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) as paid_count,
            COUNT(CASE WHEN payment_status = 'pending' THEN 1 END) as pending_count
        FROM payroll_transactions
        WHERE school_id = %s AND month = %s AND year = %s
        """
        
        result = self.db.execute_query(query, (self.school_id, month, year), fetch=True)
        
        return {
            "success": True,
            "month": month,
            "year": year,
            "summary": result[0] if result else {}
        }


def get_payroll_service(school_id: str) -> PayrollService:
    """Helper to get payroll service instance"""
    return PayrollService(school_id)
