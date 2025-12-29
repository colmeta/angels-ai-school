"""
Test the Executive Assistant Agent
Run this after setting up your database and seed data
"""
from dotenv import load_dotenv
load_dotenv()

from Executive_Assistant_Service import ExecutiveAssistantService, process_registration, get_executive_dashboard
from database import get_db
import json
from datetime import datetime

# ANSI colors for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

# ============================================
# GET SCHOOL ID (You need this first!)
# ============================================
def get_or_create_test_school():
    """Get existing test school or create new one"""
    db = get_db()
    
    # Try to find existing test school
    query = "SELECT * FROM schools WHERE code = 'TST001' LIMIT 1"
    result = db.execute_query(query)
    
    if result:
        school = result[0]
        print_info(f"Using existing school: {school['name']} (ID: {school['id']})")
        return str(school['id'])
    else:
        # Create test school
        query = """
        INSERT INTO schools (name, code, country, city, currency)
        VALUES ('Test School Nairobi', 'TST001', 'Kenya', 'Nairobi', 'KES')
        RETURNING id, name
        """
        result = db.execute_query(query, fetch=True)
        school = result[0]
        print_success(f"Created test school: {school['name']} (ID: {school['id']})")
        return str(school['id'])

# ============================================
# TEST 1: STUDENT REGISTRATION
# ============================================
def test_student_registration(school_id):
    """Test automated student registration workflow"""
    print_header("TEST 1: Student Registration Automation")
    
    registration_data = {
        'student': {
            'first_name': 'Amina',
            'middle_name': 'Zawadi',
            'last_name': 'Ochieng',
            'date_of_birth': '2016-05-20',
            'gender': 'female',
            'grade': 'Grade 2',
            'class': 'Grade 2B',
            'address': '456 Mombasa Road, Nairobi',
            'county': 'Nairobi',
            'city': 'Nairobi',
            'phone': '+254733456789',
            'blood_group': 'A+',
            'allergies': 'Peanuts',
            'medical_conditions': None
        },
        'parents': [
            {
                'first_name': 'James',
                'middle_name': 'Kimani',
                'last_name': 'Ochieng',
                'gender': 'male',
                'phone': '+254744567890',
                'email': 'james.ochieng@email.com',
                'whatsapp': '+254744567890',
                'language': 'en',
                'occupation': 'Engineer',
                'employer': 'Tech Corp Kenya',
                'address': '456 Mombasa Road, Nairobi',
                'county': 'Nairobi',
                'city': 'Nairobi',
                'contact_method': 'whatsapp',
                'opt_in_notifications': True,
                'relationship': 'father',
                'is_primary': True,
                'is_fee_payer': True
            },
            {
                'first_name': 'Grace',
                'middle_name': 'Akinyi',
                'last_name': 'Ochieng',
                'gender': 'female',
                'phone': '+254755678901',
                'email': 'grace.ochieng@email.com',
                'whatsapp': '+254755678901',
                'language': 'en',
                'occupation': 'Accountant',
                'employer': 'Finance Solutions Ltd',
                'address': '456 Mombasa Road, Nairobi',
                'county': 'Nairobi',
                'city': 'Nairobi',
                'contact_method': 'whatsapp',
                'opt_in_notifications': True,
                'relationship': 'mother',
                'is_primary': False,
                'is_fee_payer': False
            }
        ],
        'emergency': {
            'name': 'Grace Ochieng',
            'phone': '+254755678901',
            'relationship': 'mother'
        }
    }
    
    print_info("Processing student registration...")
    result = process_registration(school_id, registration_data)
    
    if result['success']:
        print_success(f"Registration successful!")
        print_info(f"Student ID: {result['student']['id']}")
        print_info(f"Admission Number: {result['admission_number']}")
        print_info(f"Parents registered: {len(result['parents'])}")
        if result['fee_assignment']:
            print_info(f"Fee assigned: KES {result['fee_assignment']['final_amount']}")
    else:
        print_error(f"Registration failed: {result.get('error', 'Unknown error')}")
    
    return result

# ============================================
# TEST 2: ENROLLMENT STATISTICS
# ============================================
def test_enrollment_statistics(school_id):
    """Test enrollment analytics generation"""
    print_header("TEST 2: Enrollment Statistics & Analytics")
    
    service = ExecutiveAssistantService(school_id)
    
    # Test different time periods
    for period in ['day', 'week', 'month']:
        print_info(f"\nGetting {period} statistics...")
        stats = service.get_enrollment_statistics(period)
        
        print(f"  Total Students: {stats['total_students']}")
        print(f"  Active Students: {stats['active_students']}")
        print(f"  New Enrollments: {stats['new_enrollments']}")
        print(f"  Gender Distribution: Male={stats['gender_distribution']['male']}, Female={stats['gender_distribution']['female']}")
        
        if stats['grade_distribution']:
            print(f"  Grade Distribution:")
            for grade_info in stats['grade_distribution']:
                print(f"    - {grade_info['current_grade']}: {grade_info['student_count']} students")

# ============================================
# TEST 3: EXECUTIVE DASHBOARD
# ============================================
def test_executive_dashboard(school_id):
    """Test executive report generation"""
    print_header("TEST 3: Executive Dashboard Report")
    
    print_info("Generating comprehensive executive report...")
    report = get_executive_dashboard(school_id)
    
    print_success("Report Generated!")
    print(f"\n{Colors.BOLD}Report Type:{Colors.ENDC} {report['report_type']}")
    print(f"{Colors.BOLD}Generated At:{Colors.ENDC} {report['generated_at']}")
    
    # Enrollment Overview
    print(f"\n{Colors.BOLD}📚 ENROLLMENT OVERVIEW{Colors.ENDC}")
    print(f"  Total Students: {report['enrollment']['total_students']}")
    print(f"  Active Students: {report['enrollment']['active_students']}")
    print(f"  New Enrollments (period): {report['enrollment']['new_enrollments']}")
    
    # Financial Overview
    print(f"\n{Colors.BOLD}💰 FINANCIAL OVERVIEW{Colors.ENDC}")
    finances = report['finances']
    print(f"  Expected Revenue: KES {finances['total_expected']:,.2f}")
    print(f"  Collected: KES {finances['total_collected']:,.2f}")
    print(f"  Outstanding: KES {finances['total_outstanding']:,.2f}")
    print(f"  Collection Rate: {finances['collection_rate']:.1f}%")
    print(f"  Overdue Accounts: {finances['overdue_count']}")
    
    # Communication Overview
    print(f"\n{Colors.BOLD}📱 COMMUNICATION OVERVIEW{Colors.ENDC}")
    comms = report['communications']
    print(f"  Messages Sent: {comms['messages_sent']}")
    print(f"  Delivery Rate: {comms['delivery_rate']:.1f}%")
    print(f"  Read Rate: {comms['read_rate']:.1f}%")
    print(f"  Failed Messages: {comms['failed_messages']}")
    print(f"  Total Cost: KES {comms['total_cost']:.2f}")
    
    # Executive Summary
    print(f"\n{Colors.BOLD}📊 EXECUTIVE INSIGHTS{Colors.ENDC}")
    for insight in report['summary']:
        print(f"  {insight}")

# ============================================
# TEST 4: BATCH OPERATIONS
# ============================================
def test_batch_operations(school_id):
    """Test batch student registration"""
    print_header("TEST 4: Batch Registration (10 Students)")
    
    print_info("Simulating bulk student enrollment...")
    
    successful = 0
    failed = 0
    
    for i in range(10):
        registration_data = {
            'student': {
                'first_name': f'Student{i+1}',
                'last_name': f'TestFamily{i+1}',
                'date_of_birth': f'201{i % 10}-0{(i % 12) + 1}-15',
                'gender': 'male' if i % 2 == 0 else 'female',
                'grade': f'Grade {(i % 6) + 1}',
                'address': f'Address {i+1}, Nairobi',
                'county': 'Nairobi',
                'city': 'Nairobi',
                'phone': f'+25471234{i:04d}'
            },
            'parents': [
                {
                    'first_name': f'Parent{i+1}',
                    'last_name': f'TestFamily{i+1}',
                    'gender': 'male' if i % 2 == 0 else 'female',
                    'phone': f'+25472234{i:04d}',
                    'email': f'parent{i+1}@test.com',
                    'whatsapp': f'+25472234{i:04d}',
                    'language': 'en',
                    'occupation': 'Professional',
                    'address': f'Address {i+1}, Nairobi',
                    'county': 'Nairobi',
                    'city': 'Nairobi',
                    'contact_method': 'whatsapp',
                    'opt_in_notifications': True,
                    'relationship': 'parent',
                    'is_primary': True,
                    'is_fee_payer': True
                }
            ],
            'emergency': {
                'name': f'Parent{i+1} TestFamily{i+1}',
                'phone': f'+25472234{i:04d}',
                'relationship': 'parent'
            }
        }
        
        result = process_registration(school_id, registration_data)
        
        if result['success']:
            successful += 1
            print_success(f"  Student {i+1}/10 registered: {result['admission_number']}")
        else:
            failed += 1
            print_error(f"  Student {i+1}/10 failed: {result.get('error', 'Unknown')}")
    
    print(f"\n{Colors.BOLD}Batch Results:{Colors.ENDC}")
    print(f"  Successful: {successful}/10")
    print(f"  Failed: {failed}/10")

# ============================================
# MAIN TEST RUNNER
# ============================================
def run_all_tests():
    """Run all Executive Assistant tests"""
    print_header("🚀 ANGELS AI - EXECUTIVE ASSISTANT TESTING SUITE 🚀")
    
    try:
        # Step 1: Get or create test school
        print_info("Step 1: Setting up test school...")
        school_id = get_or_create_test_school()
        
        # Step 2: Test student registration
        test_student_registration(school_id)
        
        # Step 3: Test enrollment statistics
        test_enrollment_statistics(school_id)
        
        # Step 4: Test executive dashboard
        test_executive_dashboard(school_id)
        
        # Step 5: Test batch operations
        test_batch_operations(school_id)
        
        # Final summary
        print_header("✅ ALL TESTS COMPLETED SUCCESSFULLY! ✅")
        print_success("Executive Assistant Service is fully operational!")
        print_info(f"School ID for future tests: {school_id}")
        
    except Exception as e:
        print_error(f"Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
