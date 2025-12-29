import sys
import os
import random
from datetime import datetime, timedelta
import uuid
from faker import Faker
from dotenv import load_dotenv
import json

# Add parent directory to path to allow importing from api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Fix: Use the classes actually found in api/services/database.py
from api.services.database import (
    DatabaseManager, 
    StudentOperations, 
    ParentOperations, 
    FeeOperations,
    SchoolOperations
)

# Load environment variables
load_dotenv()

fake = Faker()

def seed_galaxy_academy():
    print("Starting Galaxy International Academy Seeding...")
    
    # Initialize Database Manager
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not set in environment")
        return

    db = DatabaseManager(database_url=db_url)
    
    # Initialize Operations
    student_ops = StudentOperations(db)
    parent_ops = ParentOperations(db)
    fee_ops = FeeOperations(db)
    school_ops = SchoolOperations(db) 

    school_id = str(uuid.uuid4())
    
    print(f"Creating School: Galaxy International Academy ({school_id})")
    
    # Raw Insert for School
    # Schema: id, name, address, phone, email, website, logo_url, created_at, updated_at
    school_query = """
    INSERT INTO schools (id, name, address, phone, email, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    ON CONFLICT (id) DO NOTHING
    RETURNING id;
    """
    
    try:
        # We try to create specific school record 
        db.execute_query(school_query, (
            school_id, 
            "Galaxy International Academy", 
            fake.address(), 
            fake.phone_number(), 
            "info@galaxy.edu"
        ))
    except Exception as e:
        print(f"Could not create school record directly (Schema mistmatch?): {e}")
        # Proceeding assuming maybe it worked or we skip and use ID for foreign keys
    
    print("Building Classes List (Logical)...")
    levels = {
        "Nursery": ["Baby", "Middle", "Top"],
        "Primary": [f"P.{i}" for i in range(1, 8)],
        "Secondary": [f"S.{i}" for i in range(1, 7)]
    }
    streams = ["North", "South", "East"]
    
    class_list = []
    for level, grades in levels.items():
        for grade in grades:
            for stream in streams:
                class_list.append({
                    "grade": grade,
                    "name": f"{grade} {stream}"
                })

    # 3. Create Fee Structure
    print("Creating Fee Structure...")
    term_fee = None
    try:
        # Schema: id, school_id, class_name, term, year, fee_items (json), 
        # total_amount, currency, created_at
        
        # We need to construct fee_items
        fee_items = [
            {"name": "Tuition", "amount": 500000},
            {"name": "Transport", "amount": 100000}
        ]
        
        # Since Ops might be expecting different keys due to drift, we use raw SQL or adjust dict keys
        # The schema says fee_items is JSONB. Ops might be wrapping it.
        # Let's inspect fee_ops.create_fee_structure in api/services/database.py again? 
        # Wait, I saw it in Step 82 line 312.
        # It expects: school_id, name, grade_level, academic_term... 
        # BUT Schema has class_name, term, year.
        # The Ops class is OUT OF SYNC with Schema!
        
        # WE MUST USE RAW SQL to be safe, because Ops might fail with column errors as seen before.
        # "column name does not exist" was from Ops execution.
        
        fee_query = """
        INSERT INTO fee_structures (
            school_id, class_name, term, year, 
            fee_items, total_amount, currency, created_at
        ) VALUES (
            %s, %s, %s, %s, 
            %s, %s, %s, NOW()
        ) RETURNING *;
        """
        
        result = db.execute_query(fee_query, (
            school_id,
            "General", # class_name
            "Term 1",  # term
            2026,      # year
            json.dumps(fee_items),
            600000,
            "UGX"
        ))
        
        if result:
            term_fee = result[0]
            print(f"Fee structure created: {term_fee.get('id')}")
            
    except Exception as e:
        print(f"Fee Structure Error: {e}")

    # 4. Enroll Students
    print("Enrolling Students...")
    total_students = 0
    
    for cls in class_list:
        # 20-30 students per class
        for _ in range(random.randint(20, 30)):
            s_gender = random.choice(['male', 'female'])
            s_first = fake.first_name_male() if s_gender == 'male' else fake.first_name_female()
            s_last = fake.last_name()
            
            # Schema: id, school_id, admission_number, first_name, last_name, date_of_birth, 
            # gender, class_name, stream, status
            student_id = str(uuid.uuid4())
            admission_number = f"ADM{random.randint(100000, 999999)}"
            
            student_query = """
            INSERT INTO students (
                id, school_id, admission_number, first_name, last_name, 
                date_of_birth, gender, class_name, stream, status
            ) VALUES (
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, 'active'
            ) RETURNING id;
            """
            
            try:
                db.execute_query(student_query, (
                    student_id,
                    school_id,
                    admission_number,
                    s_first,
                    s_last,
                    fake.date_of_birth(minimum_age=4, maximum_age=18),
                    s_gender,
                    cls['grade'], # Mapping 'grade' to class_name e.g. P.1
                    cls['name'],  # Mapping 'name' to stream e.g. P.1 East (or just East? Schema says stream VARCHAR(50))
                    # Let's assume class_name=P.1, stream=East.
                    # My class_list has grade="P.1", name="P.1 East". 
                    # I'll preserve cls['name'] as valid stream info or redundant.
                ))
                
                # Parent
                parent_id = str(uuid.uuid4())
                p_first = fake.first_name()
                p_last = s_last
                
                # Schema: id, school_id, first_name, last_name, email, phone, occupation
                parent_query = """
                INSERT INTO parents (
                    id, school_id, first_name, last_name, email, phone, occupation
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
                """
                
                db.execute_query(parent_query, (
                    parent_id,
                    school_id,
                    p_first,
                    p_last,
                    fake.email(),
                    fake.phone_number(),
                    fake.job()
                ))
                
                # Link Parent
                # Schema: id, student_id, parent_id, relationship, is_primary
                link_query = """
                INSERT INTO student_parents (
                    student_id, parent_id, relationship, is_primary
                ) VALUES (%s, %s, 'Mother', true);
                """
                db.execute_query(link_query, (student_id, parent_id), fetch=False)
                
                # Assign Fees
                # Schema: id, school_id, student_id, term, year, total_fees, balance, payment_status, due_date
                if term_fee:
                    sf_query = """
                    INSERT INTO student_fees (
                        school_id, student_id, term, year, 
                        total_fees, balance, payment_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'pending');
                    """
                    db.execute_query(sf_query, (
                        school_id,
                        student_id,
                        "Term 1",
                        2026,
                        600000,
                        600000
                    ), fetch=False)

                total_students += 1
                if total_students % 50 == 0:
                    print(f"   ... {total_students} students enrolled")
                    
            except Exception as e:
                 print(f"Error enrolling student: {e}")
                 # break # Uncomment to stop on first error

    print(f"Enrollment Complete: {total_students} students added.")
    print(f"School ID: {school_id}")
    
    # Clean up
    db.close_all_connections()

if __name__ == "__main__":
    seed_galaxy_academy()
