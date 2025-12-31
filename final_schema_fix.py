from api.services.database import get_db_manager
import os
from dotenv import load_dotenv

load_dotenv()

db = get_db_manager()

queries = [
    # 1. Make school_id nullable in user_sessions
    "ALTER TABLE user_sessions ALTER COLUMN school_id DROP NOT NULL;",
    
    # 2. Add photo_url to users if it doesn't exist
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_url TEXT;",
    
    # 3. Add metadata to users if it doesn't exist (helpful for Google profile data)
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS metadata JSONB;",
    
    # 4. Ensure password_hash is TEXT and nullable (redundant but safe)
    "ALTER TABLE users ALTER COLUMN password_hash TYPE TEXT;",
    "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"
]

print("Starting final schema correction...")

try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for q in queries:
            print(f"Executing: {q}")
            cursor.execute(q)
        cursor.close()
    print("✅ Final schema correction complete!")
except Exception as e:
    print(f"❌ Error during correction: {e}")
