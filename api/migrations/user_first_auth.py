import os
import psycopg2
from api.core.config import get_settings

def run_migration():
    settings = get_settings()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    print(f"🚀 Running migration on database...")
    
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # 1. Update users table
        print("Updating 'users' table...")
        cur.execute("ALTER TABLE users ALTER COLUMN role DROP NOT NULL;")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_url TEXT;")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]';")
        
        # 2. Create user_school_roles table
        print("Creating 'user_school_roles' table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_school_roles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            is_primary BOOLEAN DEFAULT false,
            achievements JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, school_id, role)
        );
        """)
        
        # 3. Add school_code to schools
        print("Adding 'school_code' to 'schools' table...")
        cur.execute("ALTER TABLE schools ADD COLUMN IF NOT EXISTS school_code VARCHAR(10) UNIQUE;")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
