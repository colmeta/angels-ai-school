import psycopg2
import os

def get_db_url():
    if not os.path.exists('.env'):
        return None
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                return line.split('=', 1)[1].strip()
    return None

db_url = get_db_url()
if not db_url:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

try:
    print(f"[*] Connecting to database...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("[*] Adding google_id column...")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(150) UNIQUE")
    
    print("[*] Adding auth_provider column...")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'email'")
    
    print("[*] Updating password_hash nullability...")
    cur.execute("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL")
    
    conn.commit()
    cur.close()
    conn.close()
    print("[OK] Migration successful!")
except Exception as e:
    print(f"[ERROR] Migration failed: {e}")
