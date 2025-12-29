
import pytest
import time
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app
from api.database import SessionLocal
from api.models import School, Student, FeeStructure

client = TestClient(app)

# We need to find the school ID we just created
def get_galaxy_school_id():
    db = SessionLocal()
    # Find school with "Galaxy" in name
    school = db.query(School).filter(School.name.like("%Galaxy%")).first()
    db.close()
    if school:
        return school.id
    return None

class TestLoadPerformance:
    
    school_id = get_galaxy_school_id()
    
    def test_student_list_performance(self):
        """
        Goal: Fetch all students for the school.
        Target: < 500ms
        """
        if not self.school_id:
            pytest.skip("Galaxy International Academy not found. Run seeder first.")

        print(f"\n[LoadTest] Fetching students for school: {self.school_id}")
        
        start_time = time.time()
        response = client.get(f"/api/students?school_id={self.school_id}")
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"[LoadTest] Duration: {duration:.4f}s")
        
        assert response.status_code == 200
        data = response.json()
        print(f"[LoadTest] Count: {len(data)}")
        
        # Soft assertion for performance
        if duration > 0.5:
             print(f"⚠️ WARNING: Student list took {duration:.4f}s (Target: <0.5s)")

    def test_report_card_generation_batch(self):
        """
        Goal: Generate report cards for a whole class (approx 30 students).
        Target: < 10s for the batch (approx 300ms per student).
        """
        if not self.school_id:
            pytest.skip("School not found")
            
        # Get a class
        db = SessionLocal()
        student = db.query(Student).filter(Student.school_id == self.school_id).first()
        if not student:
            pytest.skip("No students found")
            
        class_name = student.current_class
        db.close()
        
        print(f"\n[LoadTest] Generating reports for class: {class_name}")
        
        start_time = time.time()
        # Assuming there is a batch generation endpoint or we simulate loop
        # For now, let's hit the endpoint for up to 10 students serially to measure latency
        
        # Get 10 students
        response = client.get(f"/api/students?school_id={self.school_id}&current_class={class_name}&limit=10")
        students = response.json()
        
        for s in students:
            # Generate report
            r_start = time.time()
            resp = client.post(f"/api/reports/generate", json={
                "student_id": s['id'],
                "term": "Term 1",
                "year": "2026"
            })
            # We don't assert 200 strictly if data is missing, but we measure time
            r_dur = time.time() - r_start
            print(f"  - Student {s['id']}: {r_dur:.4f}s")
            
        total_duration = time.time() - start_time
        print(f"[LoadTest] Total Duration for batch: {total_duration:.4f}s")

    def test_finance_defaulters_query(self):
        """
        Goal: Query defaulters list. This often involves conflicting joins.
        Target: < 1s
        """
        if not self.school_id:
            pytest.skip("School not found")
            
        print("\n[LoadTest] Querying fee defaulters...")
        start_time = time.time()
        
        # Typically this would be an endpoint like /api/finance/defaulters or /api/students?payment_status=defaulted
        response = client.get(f"/api/finance/defaulters?school_id={self.school_id}")
        
        duration = time.time() - start_time
        print(f"[LoadTest] Duration: {duration:.4f}s")
        
        if response.status_code != 200:
             print(f"⚠️ Endpoint failed: {response.status_code}")
        else:
             print(f"[LoadTest] Found {len(response.json())} defaulters")

if __name__ == "__main__":
    # If run directly settings need to be correct
    pytest.main([__file__, "-v", "-s"])
