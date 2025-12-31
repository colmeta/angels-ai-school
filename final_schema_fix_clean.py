from api.services.database import get_db_manager
import os
from dotenv import load_dotenv

load_dotenv()

db = get_db_manager()

queries = [
    "ALTER TABLE user_sessions ALTER COLUMN school_id DROP NOT NULL;",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_url TEXT;",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS metadata JSONB;",
    "ALTER TABLE users ALTER COLUMN password_hash TYPE TEXT;",
    "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"
]

print("Starting final schema correction (clean)...")

try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for q in queries:
            print(f"Executing: {q}")
            cursor.execute(q)
        cursor.close()
    print("SUCCESS: Final schema correction complete!")
except Exception as e:
    print(f"ERROR: Error during correction: {str(e)}")
