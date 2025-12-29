from api.services.database import get_db_manager
import json

db = get_db_manager()
try:
    columns = db.execute_query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'", fetch=True)
    print(json.dumps(columns, indent=2))
except Exception as e:
    print(f"Error: {e}")
