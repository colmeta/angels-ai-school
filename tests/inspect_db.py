import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

def inspect_schema():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    print(f"Connecting to DB...")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    for table in ['parents', 'teachers']:
        print(f"Inspecting columns for '{table}'...")
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
        rows = cur.fetchall()
        for row in rows:
            print(f"- {table}.{row['column_name']} ({row['data_type']})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_schema()
