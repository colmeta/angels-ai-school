from api.services.database import get_db_manager
import os
from dotenv import load_dotenv

load_dotenv()

db = get_db_manager()
try:
    schema = db.execute_query(\"\"\"
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users'
    \"\"\", fetch=True)
    
    for col in schema:
        print(f"Column: {col['column_name']}, Type: {col['data_type']}, MaxLen: {col['character_maximum_length']}, Nullable: {col['is_nullable']}")
        
except Exception as e:
    print(f"Error checking schema: {e}")
