from api.services.database import get_db_manager

db = get_db_manager()

try:
    print("🚀 Starting migration for Google Sign-In fields...")
    
    # 1. Add google_id column
    print("Adding google_id column...")
    db.execute_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(150) UNIQUE")
    
    # 2. Add auth_provider column
    print("Adding auth_provider column...")
    db.execute_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'email'")
    
    # 3. Drop NOT NULL constraint on password_hash
    print("Updating password_hash nullability...")
    db.execute_query("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL")
    
    print("✅ Migration successful!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
