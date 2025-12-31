from api.services.database import get_db_manager
import os
from dotenv import load_dotenv

load_dotenv()

db = get_db_manager()

queries = [
    "ALTER TABLE users ALTER COLUMN password_hash TYPE TEXT;",
    "ALTER TABLE users ALTER COLUMN role DROP NOT NULL;",
    "ALTER TABLE users ALTER COLUMN school_id DROP NOT NULL;",
    "UPDATE users SET role = 'director' WHERE role IS NULL;"
]

print("Starting emergency schema upgrade...")

try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for q in queries:
            print(f"Executing: {q}")
            cursor.execute(q)
        cursor.close()
    print("✅ Emergency schema upgrade complete!")
except Exception as e:
    print(f"❌ Error during upgrade: {e}")
