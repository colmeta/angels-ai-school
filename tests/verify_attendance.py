
import requests
import json
import uuid

# Configuration
API_URL = "http://localhost:8000/api/attendance/batch"
# Mock token - in a real test we would login first, but assuming we mock the dependency or disable auth for local test
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer mocked_token" 
}

# Mock Data
school_id = str(uuid.uuid4())
student_id = str(uuid.uuid4())

# 1. Subject Attendance Payload
subject_payload = {
    "type": "subject",
    "records": [
        {
            "student_id": student_id,
            "subject": "Mathematics",
            "class_name": "P.1",
            "status": "present",
            "mode": "voice",
            "notes": "Arrived early"
        }
    ]
}

# 2. Exam Attendance Payload
exam_payload = {
    "type": "exam",
    "records": [
        {
            "student_id": student_id,
            "exam_name": "Mid-Term 2024",
            "subject": "Mathematics",
            "class_name": "P.1",
            "status": "sat_exam",
            "mode": "photo",
            "booklet_number": "BK-001"
        }
    ]
}

print("Note: This script requires a running local server and valid auth token to fully succeed.")
print("It serves as a payload verification for now.")

print("\n--- Subject Payload ---")
print(json.dumps(subject_payload, indent=2))

print("\n--- Exam Payload ---")
print(json.dumps(exam_payload, indent=2))
