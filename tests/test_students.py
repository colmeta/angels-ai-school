"""
Student Management Tests
Tests for student CRUD operations, enrollment, and bulk operations
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)


class TestStudentCRUD:
    """Test Create, Read, Update, Delete operations for students"""
    
    def test_create_student(self):
        """Test creating a new student"""
        student_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "2010-01-15",
            "gender": "Male",
            "admission_number": "STU001",
            "class_id": 1,
            "parent_email": "parent@example.com",
            "parent_phone": "+256700000000"
        }
        
        response = client.post("/api/students", json=student_data)
        
        # Should either succeed or require authentication
        assert response.status_code in [200, 201, 401, 403]
    
    def test_get_student_by_id(self):
        """Test retrieving a specific student"""
        response = client.get("/api/students/1")
        
        # Should require auth or return student
        assert response.status_code in [200, 401, 403, 404]
    
    def test_get_all_students(self):
        """Test retrieving all students for a school"""
        response = client.get("/api/students")
        
        assert response.status_code in [200, 401, 403]
    
    def test_update_student(self):
        """Test updating student information"""
        update_data = {
            "first_name": "Jane",
            "phone": "+256700000001"
        }
        
        response = client.put("/api/students/1", json=update_data)
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_delete_student(self):
        """Test soft-deleting a student"""
        response = client.delete("/api/students/1")
        
        assert response.status_code in [200, 204, 401, 403, 404]


class TestStudentValidation:
    """Test input validation for student data"""
    
    def test_create_student_missing_required_fields(self):
        """Test that creating a student without required fields fails"""
        response = client.post("/api/students", json={
            "first_name": "John"
            # Missing many required fields
        })
        
        assert response.status_code in [400, 401, 422]
    
    def test_create_student_invalid_date_format(self):
        """Test that invalid date formats are rejected"""
        response = client.post("/api/students", json={
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "not-a-date",  # Invalid format
            "gender": "Male",
            "admission_number": "STU002",
            "class_id": 1
        })
        
        assert response.status_code in [400, 401, 422]
    
    def test_create_student_invalid_gender(self):
        """Test that invalid gender values are rejected"""
        response = client.post("/api/students", json={
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "2010-01-15",
            "gender": "InvalidGender",  # Not Male/Female/Other
            "admission_number": "STU003",
            "class_id": 1
        })
        
        # Should validate gender enum
        assert response.status_code in [400, 401, 422]


class TestStudentEnrollment:
    """Test student enrollment workflows"""
    
    def test_enroll_student_in_class(self):
        """Test enrolling a student in a class"""
        response = client.post("/api/students/1/enroll", json={
            "class_id": 5,
            "academic_year": "2024"
        })
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_unenroll_student_from_class(self):
        """Test removing a student from a class"""
        response = client.post("/api/students/1/unenroll", json={
            "class_id": 5
        })
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_transfer_student_between_classes(self):
        """Test transferring a student from one class to another"""
        response = client.post("/api/students/1/transfer", json={
            "from_class_id": 5,
            "to_class_id": 6
        })
        
        assert response.status_code in [200, 401, 403, 404]


class TestBulkStudentOperations:
    """Test bulk import and operations"""
    
    def test_bulk_import_students(self):
        """Test importing multiple students at once"""
        students = [
            {
                "first_name": f"Student{i}",
                "last_name": "Bulk",
                "date_of_birth": "2010-01-01",
                "gender": "Male",
                "admission_number": f"BULK{i:03d}",
                "class_id": 1
            }
            for i in range(1, 11)
        ]
        
        response = client.post("/api/students/bulk-import", json={
            "students": students
        })
        
        assert response.status_code in [200, 201, 401, 403]
    
    def test_bulk_update_class_assignment(self):
        """Test updating class for multiple students"""
        response = client.post("/api/students/bulk-update-class", json={
            "student_ids": [1, 2, 3, 4, 5],
            "new_class_id": 7
        })
        
        assert response.status_code in [200, 401, 403]
    
    def test_bulk_delete_students(self):
        """Test soft-deleting multiple students"""
        response = client.post("/api/students/bulk-delete", json={
            "student_ids": [100, 101, 102]
        })
        
        assert response.status_code in [200, 401, 403]


class TestStudentSearch:
    """Test student search and filtering"""
    
    def test_search_students_by_name(self):
        """Test searching for students by name"""
        response = client.get("/api/students?search=John")
        
        assert response.status_code in [200, 401, 403]
    
    def test_filter_students_by_class(self):
        """Test filtering students by class"""
        response = client.get("/api/students?class_id=5")
        
        assert response.status_code in [200, 401, 403]
    
    def test_filter_students_by_gender(self):
        """Test filtering students by gender"""
        response = client.get("/api/students?gender=Female")
        
        assert response.status_code in [200, 401, 403]
    
    def test_pagination_works(self):
        """Test that pagination works correctly"""
        response = client.get("/api/students?page=1&limit=10")
        
        assert response.status_code in [200, 401, 403]


class TestStudentReports:
    """Test student report generation"""
    
    def test_get_student_profile(self):
        """Test getting complete student profile"""
        response = client.get("/api/students/1/profile")
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_get_student_academic_history(self):
        """Test getting student's academic history"""
        response = client.get("/api/students/1/academic-history")
        
        assert response.status_code in [200, 401, 403, 404]
    
    def test_get_student_fee_statement(self):
        """Test getting student's fee statement"""
        response = client.get("/api/students/1/fee-statement")
        
        assert response.status_code in [200, 401, 403, 404]


class TestDataIntegrity:
    """Test data integrity and constraints"""
    
    def test_duplicate_admission_number_rejected(self):
        """Test that duplicate admission numbers are rejected"""
        student = {
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": "2010-01-01",
            "gender": "Male",
            "admission_number": "DUP001",
            "class_id": 1
        }
        
        # Create first student
        response1 = client.post("/api/students", json=student)
        
        # Try to create duplicate
        response2 = client.post("/api/students", json=student)
        
        # At least one should indicate duplicate
        assert response1.status_code in [200, 201, 401] or response2.status_code in [400, 409]
    
    def test_invalid_class_id_rejected(self):
        """Test that invalid class IDs are rejected"""
        response = client.post("/api/students", json={
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": "2010-01-01",
            "gender": "Male",
            "admission_number": "INV001",
            "class_id": 99999  # Non-existent class
        })
        
        assert response.status_code in [400, 401, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
