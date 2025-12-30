import os
import sys

# Add the current directory to sys.path to ensure we can import 'api'
sys.path.append(os.getcwd())

from api.services.database import get_db_manager

def fix_schema():
    print("Starting schema fix for authentication...")
    try:
        db = get_db_manager()
        
        # 1. Make password_hash nullable
        print("Alterting users table to make password_hash nullable...")
        db.execute_query(
            "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"
        )
        print("✅ usage: password_hash is now nullable.")

        print("Schema fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")

if __name__ == "__main__":
    fix_schema()
