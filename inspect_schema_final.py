from api.services.database import get_db_manager
import os
from dotenv import load_dotenv

load_dotenv()

db = get_db_manager()

def check_table(table_name):
    print(f"\n--- Schema for {table_name} ---")
    try:
        schema = db.execute_query(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """, fetch=True)
        
        if not schema:
            print(f"Table {table_name} not found or no columns.")
            return

        for col in schema:
            print(f"Col: {col['column_name']}, Type: {col['data_type']}, Nullable: {col['is_nullable']}, Default: {col['column_default']}")
            
    except Exception as e:
        print(f"Error checking {table_name}: {e}")

check_table('users')
check_table('user_sessions')
