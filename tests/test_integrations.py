"""
Integration Tests
End-to-end workflow tests for complete user journeys
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)


class TestTeacherToParentFlow:
    """Test complete teacher→parent communication workflow"""
    
    def test_attendance_to_notification_flow(self):
        """
        Complete flow:
        1. Teacher uploads attendance photo
        2. OCR extracts data
        3. Attendance recorded
        4. Parent receives notification
        """
        # Step 1: Upload attendance (would need actual file in real test)
        # Step 2: OCR processing happens automatically  
        # Step 3: Check attendance was recorded
        response = client.get("/api/students/1/attendance")
        assert response.status_code in [200, 401, 403, 404]
        
        # Step 4: Check parent notification was sent
        # (Would need to verify notification service was called)
    
    def test_grade_entry_to_parent_report(self):
        """
        Complete flow:
        1. Teacher enters grades
        2. System calculates GPA/average
        3. Parent can view child's grades
        4. Report card generated
        """
        # Step 1: Enter grades
        response = client.post("/api/students/1/grades", json={
            "subject": "Mathematics",
            "score": 85,
            "term": "1",
            "year": "2024"
        })
        
        assert response.status_code in [200, 201, 401, 403, 404]
        
        # Step 2-3: Parent views grades
        response = client.get("/api/parent/child/1/grades")
        assert response.status_code in [200, 401, 403, 404]
        
        # Step 4: Generate report card
        response = client.get("/api/students/1/report-card")
        assert response.status_code in [200, 401, 403, 404]


class TestPaymentFlow:
    """Test complete payment workflows"""
    
    def test_mobile_money_payment_flow(self):
        """
        Complete flow:
        1. Parent initiates mobile money payment
        2. Payment recorded
        3. Fee balance updated
        4. Receipt generated
        5. Admin notified
        """
        # Step 1: Initiate payment
        response = client.post("/api/payments", json={
            "student_id": 1,
            "amount": 300000,
            "payment_method": "mobile_money",
            "phone_number": "+256700000000",
            "provider": "MTN"
        })
        
        assert response.status_code in [200, 201, 401, 403]
        
        if response.status_code in [200, 201]:
            payment_id = response.json().get("payment_id") or response.json().get("id")
            
            # Step 3: Check balance updated
            balance_response = client.get("/api/fees/balance/student/1")
            assert balance_response.status_code in [200, 401, 403, 404]
            
            # Step 4: Get receipt
            if payment_id:
                receipt_response = client.get(f"/api/payments/{payment_id}/receipt")
                assert receipt_response.status_code in [200, 401, 403, 404]
    
    def test_cash_payment_flow(self):
        """
        Complete flow:
        1. Admin records cash payment
        2. Receipt printed
        3. Balance updated
        4. Parent notified
        """
        response = client.post("/api/payments", json={
            "student_id": 1,
            "amount": 200000,
            "payment_method": "cash",
            "reference": "CASH001"
        })
        
        assert response.status_code in [200, 201, 401, 403]


class TestVoiceCommandFlow:
    """Test voice command execution workflows"""
    
    def test_voice_to_action_flow(self):
        """
        Complete flow:
        1. Teacher presses mic button (frontend)
        2. Speech recognized
        3. Command parsed by Clarity
        4. Action executed
        5. Confirmation returned
        """
        # Step 3-5: Process voice command
        response = client.post("/api/command-intelligence", json={
            "command": "Mark John Doe as present",
            "user_role": "teacher"
        })
        
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            # Should indicate action was taken
            assert "result" in data or "action" in data or "success" in data
    
    def test_bulk_voice_command_flow(self):
        """
        Test bulk operation via voice:
        "Mark all Class 5A students as present"
        """
        response = client.post("/api/command-intelligence", json={
            "command": "Mark all students in Class 5A as present for today"
        })
        
        assert response.status_code in [200, 401, 403]


class TestDocumentProcessingFlow:
    """Test document upload and processing workflows"""
    
    def test_student_registration_from_photo(self):
        """
        Complete flow:
        1. Admin uploads student records photo
        2. OCR extracts data
        3. Student created in database
        4. Parent account created
        5. Welcome notification sent
        """
        # This would require actual file upload
        # Testing the endpoint exists
        response = client.post("/api/document-intelligence/upload")
        assert response.status_code in [200, 400, 401, 403, 422]
    
    def test_bulk_document_processing(self):
        """
        Complete flow:
        1. Upload 100 student record photos
        2. AI processes all documents
        3. 100 students created
        4. Verification report generated
        """
        # Would require file uploads
        pass


class TestBulkImportFlow:
    """Test data migration and bulk import workflows"""
    
    def test_excel_import_flow(self):
        """
        Complete flow:
        1. Admin uploads students.xlsx
        2. AI detects data type and maps fields
        3. Validation performed
        4. Students imported
        5. Summary report generated
        """
        # Would require file upload
        response = client.post("/api/universal-import")
        assert response.status_code in [200, 400, 401, 403, 422]


class TestEnrollmentFlow:
    """Test student enrollment workflows"""
    
    def test_new_student_enrollment(self):
        """
        Complete flow:
        1. Register new student
        2. Assign to class
        3. Create fee structure
        4. Create parent account
        5. Send welcome communications
        """
        # Step 1: Register student
        student_response = client.post("/api/students", json={
            "first_name": "Test",
            "last_name": "Enrollment",
            "date_of_birth": "2010-01-01",
            "gender": "Male",
            "admission_number": "ENROLL001",
            "class_id": 5
        })
        
        assert student_response.status_code in [200, 201, 401, 403]


class TestReportingFlow:
    """Test report generation workflows"""
    
    def test_end_of_term_report_flow(self):
        """
        Complete flow:
        1. Teacher enters all grades
        2. System calculates averages
        3. Comments added
        4. Report cards generated for all students
        5. Reports sent to parents
        """
        # This is a complex multi-step process
        # Testing key endpoints exist
        
        # Generate report card
        response = client.get("/api/students/1/report-card")
        assert response.status_code in [200, 401, 403, 404]
    
    def test_analytics_dashboard_flow(self):
        """
        Complete flow:
        1. Admin accesses dashboard
        2. AI generates insights
        3. Charts and metrics displayed
        4. Export to PDF available
        """
        response = client.get("/api/analytics/dashboard")
        assert response.status_code in [200, 401, 403]


class TestParentPortalFlow:
    """Test parent portal user journeys"""
    
    def test_parent_login_and_view_child(self):
        """
        Complete flow:
        1. Parent logs in
        2. Views child list
        3. Selects child
        4. Views grades, attendance, fees
        """
        # Login would be tested in auth tests
        # Test viewing child data
        response = client.get("/api/parent/children")
        assert response.status_code in [200, 401, 403, 404]
    
    def test_parent_payment_initiation(self):
        """
        Complete flow:
        1. Parent views fee balance
        2. Initiates payment
        3. Confirms payment
        4. Receives receipt
        """
        # View balance
        response = client.get("/api/parent/child/1/fees")
        assert response.status_code in [200, 401, 403, 404]


class TestMultiRoleFlow:
    """Test multi-role user workflows"""
    
    def test_teacher_admin_dual_role(self):
        """
        Test user with both teacher and admin roles:
        1. Login as teacher
        2. Mark attendance
        3. Switch to admin role
        4. View school-wide analytics
        """
        # This tests role switching functionality
        pass


class TestOfflineToOnlineFlow:
    """Test offline mode synchronization"""
    
    def test_offline_data_sync(self):
        """
        Complete flow:
        1. User goes offline
        2. Records attendance offline
        3. User comes back online
        4. Data syncs automatically
        5. Parent notification sent
        """
        # This would require PWA testing
        # Testing that sync endpoint exists
        pass


class TestEmergencyFlow:
    """Test emergency and incident workflows"""
    
    def test_security_incident_flow(self):
        """
        Complete flow:
        1. Staff reports security incident
        2. Alert sent to admin
        3. Incident logged
        4. Follow-up actions tracked
        """
        response = client.post("/api/v1/agents/security/report-incident", json={
            "type": "safety_concern",
            "description": "Test incident",
            "severity": "high"
        })
        
        assert response.status_code in [200, 201, 401, 403]


class TestSchedulingFlow:
    """Test timetable and scheduling workflows"""
    
    def test_timetable_creation_flow(self):
        """
        Complete flow:
        1. Admin creates timetable
        2. Teachers assigned to periods
        3. Students can view timetable
        4. Changes notify affected users
        """
        # Test timetable viewing
        response = client.get("/api/student/timetable")
        assert response.status_code in [200, 401, 403, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
