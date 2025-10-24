from src.angels_ai___complete_educational_revolution_platform.database import *
from datetime import datetime, timedelta
import uuid

# Your school ID from test_db.py
SCHOOL_ID = "paste-your-school-id-here"

# Create sample student
student_ops = get_student_ops()
student = student_ops.create_student({
    'school_id': SCHOOL_ID,
    'admission_number': 'ADM001',
    'first_name': 'John',
    'middle_name': 'Kamau',
    'last_name': 'Mwangi',
    'date_of_birth': '2015-03-15',
    'gender': 'male',
    'current_grade': 'Grade 3',
    'current_class': 'Grade 3A',
    'admission_date': '2022-01-10',
    'enrollment_status': 'active',
    'home_address': '123 Ngong Road, Nairobi',
    'county_state': 'Nairobi',
    'city': 'Nairobi',
    'primary_phone': '+254712345678',
    'email': None,
    'blood_group': 'O+',
    'allergies': None,
    'medical_conditions': None,
    'emergency_contact_name': 'Mary Mwangi',
    'emergency_contact_phone': '+254722345678',
    'emergency_contact_relationship': 'mother'
})

print(f"✅ Student created: {student['id']}")

# Create parent
parent_ops = get_parent_ops()
parent = parent_ops.create_parent({
    'school_id': SCHOOL_ID,
    'first_name': 'Mary',
    'middle_name': 'Wanjiru',
    'last_name': 'Mwangi',
    'gender': 'female',
    'primary_phone': '+254722345678',
    'secondary_phone': None,
    'email': 'mary.mwangi@email.com',
    'whatsapp_number': '+254722345678',
    'preferred_language': 'en',
    'occupation': 'Teacher',
    'employer': 'Public School Nairobi',
    'work_phone': None,
    'home_address': '123 Ngong Road, Nairobi',
    'county_state': 'Nairobi',
    'city': 'Nairobi',
    'preferred_contact_method': 'whatsapp',
    'opt_in_notifications': True
})

print(f"✅ Parent created: {parent['id']}")

# Link parent to student
relationship = parent_ops.link_parent_to_student(
    student_id=student['id'],
    parent_id=parent['id'],
    relationship_type='mother',
    is_primary=True,
    is_fee_payer=True
)

print(f"✅ Parent-Student relationship created")

# Create fee structure
fee_ops = get_fee_ops()
fee_structure = fee_ops.create_fee_structure({
    'school_id': SCHOOL_ID,
    'name': 'Grade 3 - Term 1 2025',
    'grade_level': 'Grade 3',
    'academic_term': 'Term 1',
    'academic_year': '2025',
    'tuition_amount': 25000,
    'additional_fees': {'transport': 5000, 'meals': 8000},
    'total_amount': 38000,
    'due_date': (datetime.now() + timedelta(days=30)).date(),
    'late_fee_amount': 500,
    'late_fee_starts_after_days': 7,
    'is_active': True
})

print(f"✅ Fee structure created: {fee_structure['id']}")

# Assign fee to student
student_fee = fee_ops.assign_fee_to_student(
    student_id=student['id'],
    fee_structure_id=fee_structure['id'],
    discount_percentage=0,
    discount_reason=None
)

print(f"✅ Fee assigned to student: KES {student_fee['final_amount']}")

print("\n" + "="*50)
print("🎉 Sample data created successfully!")
print("="*50)
print(f"School ID: {SCHOOL_ID}")
print(f"Student: {student['first_name']} {student['last_name']} ({student['admission_number']})")
print(f"Parent: {parent['first_name']} {parent['last_name']} ({parent['primary_phone']})")
print(f"Fee: KES {student_fee['final_amount']} (Balance: KES {student_fee['balance']})")
print("="*50)
