"""
Comprehensive API Testing Script
Tests all critical endpoints with mock data
"""
import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def test_endpoint(self, method: str, endpoint: str, data=None, description=""):
        """Test a single API endpoint"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            
            status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "description": description,
                "status": status
            }
            
            if status == "✅ PASS":
                self.passed += 1
            else:
                self.failed += 1
                result["error"] = response.text
                
            self.results.append(result)
            print(f"{status} {method} {endpoint} - {description}")
            return response
            
        except Exception as e:
            self.failed += 1
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "❌ FAIL",
                "error": str(e)
            }
            self.results.append(result)
            print(f"❌ FAIL {method} {endpoint} - {description} - Error: {str(e)}")
            return None
            
    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("\n" + "="*60)
        print("🧪 STARTING COMPREHENSIVE API TESTING")
        print("="*60 + "\n")
        
        # 1. Health Check & System
        print("\n📋 Testing Health & System Endpoints...")
        self.test_endpoint("GET", "/api/health", description="Health check")
        self.test_endpoint("GET", "/api/version", description="API version")
        
        # 2. Authentication
        print("\n🔐 Testing Authentication Endpoints...")
        login_data ={"email": "admin@stangels.ac.ug", "password": "test123"}
        self.test_endpoint("POST", "/api/auth/login", data=login_data, description="Login")
        
        # 3. School Management
        print("\n🏫 Testing School Management...")
        school_data = {
            "name": "St. Angels Academy",
            "email": "info@stangels.ac.ug",
}
        self.test_endpoint("GET", "/api/schools", description="Get schools")
        self.test_endpoint("POST", "/api/schools", data=school_data, description="Create school")
        
        # 4. Student Management
        print("\n👨‍🎓 Testing Student Management...")
        student_data = {
            "name": "John Mukasa",
            "grade": "P.7",
            "age": 13,
            "gender": "M"
        }
        self.test_endpoint("GET", "/api/students", description="Get students")
        self.test_endpoint("POST", "/api/students", data=student_data, description="Create student")
        
        # 5. Teacher/Staff Management
        print("\n👨‍🏫 Testing Teacher Management...")
        teacher_data = {
            "name": "Mr. James Omondi",
            "subject": "Mathematics",
            "email": "j.omondi@stangels.ac.ug"
        }
        self.test_endpoint("GET", "/api/teachers", description="Get teachers")
        self.test_endpoint("POST", "/api/teachers", data=teacher_data, description="Create teacher")
        
        # 6. Attendance
        print("\n✓ Testing Attendance System...")
        attendance_data = {
            "student_ids": ["STU001", "STU002"],
            "date": "2024-12-25",
            "status": "present"
        }
        self.test_endpoint("GET", "/api/attendance", description="Get attendance")
        self.test_endpoint("POST", "/api/attendance/mark", data=attendance_data, description="Mark attendance")
        
        # 7. Grades & Exams
        print("\n📊 Testing Grades & Exams...")
        grade_data = {
            "student_id": "STU001",
            "subject": "Mathematics",
            "score": 85
        }
        self.test_endpoint("GET", "/api/grades", description="Get grades")
        self.test_endpoint("POST", "/api/grades", data=grade_data, description="Submit grade")
        
        # 8. Fee Management
        print("\n💰 Testing Fee Management...")
        self.test_endpoint("GET", "/api/fees", description="Get fee structure")
        self.test_endpoint("GET", "/api/fees/payments", description="Get payments")
        
        # 9. Documents
        print("\n📄 Testing Document Generation...")
        self.test_endpoint("GET", "/api/documents/id-cards", description="Generate ID cards")
        self.test_endpoint("GET", "/api/documents/report-cards", description="Generate report cards")
        
        # 10. AI Agents
        print("\n🤖 Testing AI Agents...")
        self.test_endpoint("GET", "/api/v1/agents/test-school-001/health", description="Agent health")
        
        # 11. Analytics
        print("\n📈 Testing Analytics...")
        self.test_endpoint("GET", "/api/analytics/dashboard", description="Dashboard analytics")
        
        # Print Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📋 Total: {self.passed + self.failed}")
        print(f"Success Rate: {(self.passed/(self.passed + self.failed)*100):.1f}%")
        
        # Save results
        with open("api_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: api_test_results.json")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
