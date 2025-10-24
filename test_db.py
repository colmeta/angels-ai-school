from src.angels_ai___complete_educational_revolution_platform.database import get_db, get_student_ops
import os
from dotenv import load_dotenv

load_dotenv()

# Test connection
db = get_db()
print("✅ Database connected!")

# Test creating a school (you'll need this for everything else)
with db.get_cursor() as cur:
    cur.execute("""
        INSERT INTO schools (name, code, country, city, currency)
        VALUES ('Test School Nairobi', 'TST001', 'Kenya', 'Nairobi', 'KES')
        RETURNING id, name;
    """)
    school = cur.fetchone()
    print(f"✅ Test school created: {school['name']} (ID: {school['id']})")
    print(f"💾 Save this school_id: {school['id']}")
