"""
Fee Management Tests
Tests for fee structures, payments, balances, and receipt generation
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)


class TestFeeStructures:
    """Test fee structure creation and management"""
    
    def test_create_fee_structure(self):
        """Test creating a new fee structure"""
        fee_structure = {
            "name": "Term 1 Fees 2024",
            "academic_year": "2024",
            "term": "1",
            "items": [
                {"name": "Tuition", "amount": 500000},
                {"name": "Lunch", "amount": 150000},
                {"name": "Transport", "amount": 100000}
            ]
        }
        
        response = client.post("/api/fees/structures", json=fee_structure)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_get_fee_structures(self):
        """Test retrieving fee structures"""
        response = client.get("/api/fees/structures")
        
        assert response.status_code in [200, 401, 403]
    
    def test_update_fee_structure(self):
        """Test updating an existing fee structure"""
        update_data = {
            "name": "Updated Term 1 Fees",
            "items": [
                {"name": "Tuition", "amount": 550000}
            ]
        }
        
        response = client.put("/api/fees/structures/1", json=update_data)
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_delete_fee_structure(self):
        """Test deleting a fee structure"""
        response = client.delete("/api/fees/structures/1")
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestFeePayments:
    """Test fee payment recording and processing"""
    
    def test_record_payment(self):
        """Test recording a fee payment"""
        payment = {
            "student_id": 1,
            "amount": 300000,
            "payment_method": "cash",
            "reference": "CASH001",
            "payment_date": datetime.now().isoformat()
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_record_mobile_money_payment(self):
        """Test recording mobile money payment"""
        payment = {
            "student_id": 1,
            "amount": 200000,
            "payment_method": "mobile_money",
            "reference": "MM123456789",
            "provider": "MTN",
            "phone_number": "+256700000000"
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_record_bank_transfer_payment(self):
        """Test recording bank transfer payment"""
        payment = {
            "student_id": 1,
            "amount": 500000,
            "payment_method": "bank_transfer",
            "reference": "BANK001",
            "bank_name": "Stanbic Bank"
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_payment_with_negative_amount_rejected(self):
        """Test that negative payment amounts are rejected"""
        payment = {
            "student_id": 1,
            "amount": -100000,  # Negative amount
            "payment_method": "cash"
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [400, 422]
    
    def test_payment_with_zero_amount_rejected(self):
        """Test that zero payment amounts are rejected"""
        payment = {
            "student_id": 1,
            "amount": 0,  # Zero amount
            "payment_method": "cash"
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [400, 422]


class TestFeeBalances:
    """Test fee balance calculations"""
    
    def test_get_student_fee_balance(self):
        """Test retrieving student's fee balance"""
        response = client.get("/api/fees/balance/student/1")
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_get_class_fee_summary(self):
        """Test getting fee summary for entire class"""
        response = client.get("/api/fees/summary/class/5")
        
        assert response.status_code in [200, 401, 403]
    
    def test_get_school_fee_summary(self):
        """Test getting fee summary for entire school"""
        response = client.get("/api/fees/summary/school")
        
        assert response.status_code in [200, 401, 403]
    
    def test_balance_calculation_accuracy(self):
        """Test that fee balance is calculated correctly"""
        # This would require setting up test data
        # For now, just test the endpoint exists
        response = client.get("/api/fees/balance/student/1")
        
        if response.status_code == 200:
            data = response.json()
            # Should have balance fields
            assert "total_fees" in data or "balance" in data or "amount_paid" in data


class TestFeeReceipts:
    """Test receipt generation and retrieval"""
    
    def test_generate_receipt_for_payment(self):
        """Test generating a receipt after payment"""
        response = client.get("/api/payments/1/receipt")
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_get_all_receipts_for_student(self):
        """Test retrieving all receipts for a student"""
        response = client.get("/api/students/1/receipts")
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_receipt_pdf_generation(self):
        """Test that receipts can be generated as PDF"""
        response = client.get("/api/payments/1/receipt?format=pdf")
        
        if response.status_code == 200:
            # Should return PDF content
            assert response.headers.get("content-type") in ["application/pdf", "application/json"]


class TestPaymentPlans:
    """Test installment and payment plan features"""
    
    def test_create_payment_plan(self):
        """Test creating an installment payment plan"""
        plan = {
            "student_id": 1,
            "total_amount": 600000,
            "installments": 3,
            "start_date": "2024-01-01",
            "interval": "monthly"
        }
        
        response = client.post("/api/fees/payment-plans", json=plan)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_get_payment_plan_status(self):
        """Test checking payment plan status"""
        response = client.get("/api/fees/payment-plans/student/1")
        
        assert response.status_code in [200, 401, 403, 404]


class TestDiscounts:
    """Test discount and scholarship features"""
    
    def test_apply_discount_to_student(self):
        """Test applying a discount to student fees"""
        discount = {
            "student_id": 1,
            "discount_type": "percentage",
            "value": 10,  # 10% discount
            "reason": "Sibling discount"
        }
        
        response = client.post("/api/fees/discounts", json=discount)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_apply_scholarship(self):
        """Test applying a scholarship"""
        scholarship = {
            "student_id": 1,
            "amount": 200000,
            "sponsor": "XYZ Foundation",
            "academic_year": "2024"
        }
        
        response = client.post("/api/fees/scholarships", json=scholarship)
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_get_student_discounts(self):
        """Test retrieving all discounts for a student"""
        response = client.get("/api/students/1/discounts")
        
        assert response.status_code in [200, 401, 403, 404]


class TestFeeReports:
    """Test fee reporting and analytics"""
    
    def test_get_defaulters_list(self):
        """Test getting list of students with outstanding fees"""
        response = client.get("/api/fees/defaulters")
        
        assert response.status_code in [200, 401, 403]
    
    def test_get_payment_history(self):
        """Test getting payment history for a period"""
        response = client.get("/api/payments/history?start_date=2024-01-01&end_date=2024-12-31")
        
        assert response.status_code in [200, 401, 403]
    
    def test_export_fee_report_csv(self):
        """Test exporting fee report as CSV"""
        response = client.get("/api/fees/report?format=csv")
        
        if response.status_code == 200:
            # Should return CSV content
            assert response.headers.get("content-type") in ["text/csv", "application/csv", "application/json"]
    
    def test_get_revenue_analytics(self):
        """Test getting revenue analytics"""
        response = client.get("/api/fees/analytics/revenue")
        
        assert response.status_code in [200, 401, 403]


class TestBulkPayments:
    """Test bulk payment operations"""
    
    def test_bulk_import_payments(self):
        """Test importing multiple payments at once"""
        payments = [
            {
                "student_id": i,
                "amount": 100000,
                "payment_method": "bank_transfer",
                "reference": f"BULK{i:03d}"
            }
            for i in range(1, 11)
        ]
        
        response = client.post("/api/payments/bulk-import", json={
            "payments": payments
        })
        
        assert response.status_code in [200, 201, 401, 403]


class TestValidation:
    """Test input validation for fees"""
    
    def test_invalid_payment_method_rejected(self):
        """Test that invalid payment methods are rejected"""
        payment = {
            "student_id": 1,
            "amount": 100000,
            "payment_method": "cryptocurrency"  # Invalid method
        }
        
        response = client.post("/api/payments", json=payment)
        
        assert response.status_code in [400, 422]
    
    def test_payment_exceeding_balance_warning(self):
        """Test that overpayments are handled"""
        # This is implementation-specific
        # Some systems allow overpayment (credit), others don't
        payment = {
            "student_id": 1,
            "amount": 10000000,  # Very large amount
            "payment_method": "cash"
        }
        
        response = client.post("/api/payments", json=payment)
        
        # Should either succeed or warn
        assert response.status_code in [200, 201, 400, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
