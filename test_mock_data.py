"""
Mock Data Generator for Testing Angels AI School Platform
Creates realistic test data for comprehensive platform testing
"""
import json
import random
from datetime import datetime, timedelta

# Mock School Data
MOCK_SCHOOL = {
    "id": "test-school-001",
    "name": "St. Angels Academy",
    "motto": "Excellence Through Knowledge",
    "address": "123 Education Road, Kampala, Uganda",
    "phone": "+256 700 123456",
    "email": "info@stangels.ac.ug",
    "principal": "Dr. Sarah Nakato",
    "established": "2010",
    "student_count": 450,
    "staff_count": 35
}

# Mock Students
MOCK_STUDENTS = [
    {"id": "STU001", "name": "John Mukasa", "grade": "P.7", "age": 13, "gender": "M", "parent_phone": "+256 700 111222"},
    {"id": "STU002", "name": "Mary Nalongo", "grade": "P.7", "age": 13, "gender": "F", "parent_phone": "+256 700 222333"},
    {"id": "STU003", "name": "Peter Okello", "grade": "P.6", "age": 12, "gender": "M", "parent_phone": "+256 700 333444"},
    {"id": "STU004", "name": "Grace Namatovu", "grade": "P.6", "age": 12, "gender": "F", "parent_phone": "+256 700 444555"},
    {"id": "STU005", "name": "David Ssemakula", "grade": "P.5", "age": 11, "gender": "M", "parent_phone": "+256 700 555666"},
    {"id": "STU006", "name": "Sarah Achieng", "grade": "P.5", "age": 11, "gender": "F", "parent_phone": "+256 700 666777"},
    {"id": "STU007", "name": "Samuel Wafula", "grade": "P.4", "age": 10, "gender": "M", "parent_phone": "+256 700 777888"},
    {"id": "STU008", "name": "Rebecca Nambi", "grade": "P.4", "age": 10, "gender": "F", "parent_phone": "+256 700 888999"},
    {"id": "STU009", "name": "Joshua Kiprotich", "grade": "P.3", "age": 9, "gender": "M", "parent_phone": "+256 700 999000"},
    {"id": "STU010", "name": "Faith Akello", "grade": "P.3", "age": 9, "gender": "F", "parent_phone": "+256 700 000111"},
]

# Mock Teachers
MOCK_TEACHERS = [
    {"id": "TCH001", "name": "Mr. James Omondi", "subject": "Mathematics", "email": "j.omondi@stangels.ac.ug"},
    {"id": "TCH002", "name": "Mrs. Alice Namusoke", "subject": "English", "email": "a.namusoke@stangels.ac.ug"},
    {"id": "TCH003", "name": "Mr. Robert Kato", "subject": "Science", "email": "r.kato@stangels.ac.ug"},
    {"id": "TCH004", "name": "Ms. Christine Aber", "subject": "Social Studies", "email": "c.aber@stangels.ac.ug"},
    {"id": "TCH005", "name": "Mr. Patrick Lubega", "subject": "Religious Education", "email": "p.lubega@stangels.ac.ug"},
]

# Mock Grades
MOCK_GRADES = {
    "STU001": {"Math": 85, "English": 78, "Science": 92, "SST": 88, "RE": 75},
    "STU002": {"Math": 92, "English": 88, "Science": 85, "SST": 90, "RE": 82},
    "STU003": {"Math": 75, "English": 82, "Science": 78, "SST": 80, "RE": 77},
    "STU004": {"Math": 88, "English": 90, "Science": 86, "SST": 85, "RE": 88},
    "STU005": {"Math": 70, "English": 75, "Science": 72, "SST": 74, "RE": 70},
}

# Mock Attendance (last 30 days)
def generate_attendance():
    attendance = {}
    today = datetime.now()
    for student in MOCK_STUDENTS:
        student_attendance = []
        for i in range(30):
            date = today - timedelta(days=i)
            # 95% attendance rate
            status = "present" if random.random() < 0.95 else "absent"
            student_attendance.append({
                "date": date.strftime("%Y-%m-%d"),
                "status": status
            })
        attendance[student["id"]] = student_attendance
    return attendance

# Mock Fee Structure
MOCK_FEE_STRUCTURE = {
    "term_fee": 450000,  # UGX
    "exam_fee": 50000,
    "library_fee": 20000,
    "sports_fee": 30000,
    "total": 550000
}

# Mock Fee Payments
MOCK_FEE_PAYMENTS = {
    "STU001": {"paid": 550000, "balance": 0, "status": "full"},
    "STU002": {"paid": 550000, "balance": 0, "status": "full"},
    "STU003": {"paid": 400000, "balance": 150000, "status": "partial"},
    "STU004": {"paid": 550000, "balance": 0, "status": "full"},
    "STU005": {"paid": 300000, "balance": 250000, "status": "partial"},
}

# Mock Timetable
MOCK_TIMETABLE = {
    "Monday": [
        {"time": "8:00-9:00", "subject": "Mathematics", "teacher": "Mr. James Omondi"},
        {"time": "9:00-10:00", "subject": "English", "teacher": "Mrs. Alice Namusoke"},
        {"time": "10:00-10:30", "subject": "Break", "teacher": "-"},
        {"time": "10:30-11:30", "subject": "Science", "teacher": "Mr. Robert Kato"},
        {"time": "11:30-12:30", "subject": "Social Studies", "teacher": "Ms. Christine Aber"},
    ],
    "Tuesday": [
        {"time": "8:00-9:00", "subject": "English", "teacher": "Mrs. Alice Namusoke"},
        {"time": "9:00-10:00", "subject": "Mathematics", "teacher": "Mr. James Omondi"},
        {"time": "10:00-10:30", "subject": "Break", "teacher": "-"},
        {"time": "10:30-11:30", "subject": "Religious Education", "teacher": "Mr. Patrick Lubega"},
        {"time": "11:30-12:30", "subject": "Science", "teacher": "Mr. Robert Kato"},
    ],
}

def save_mock_data():
    """Save all mock data to JSON file"""
    data = {
        "school": MOCK_SCHOOL,
        "students": MOCK_STUDENTS,
        "teachers": MOCK_TEACHERS,
        "grades": MOCK_GRADES,
        "attendance": generate_attendance(),
        "fee_structure": MOCK_FEE_STRUCTURE,
        "fee_payments": MOCK_FEE_PAYMENTS,
        "timetable": MOCK_TIMETABLE
    }
    
    with open("mock_test_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("✅ Mock data generated successfully!")
    print(f"   - School: {MOCK_SCHOOL['name']}")
    print(f"   - Students: {len(MOCK_STUDENTS)}")
    print(f"   - Teachers: {len(MOCK_TEACHERS)}")
    print(f"   - Saved to: mock_test_data.json")

if __name__ == "__main__":
    save_mock_data()
