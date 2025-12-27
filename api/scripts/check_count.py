import os
import sys
# Add parent directory to path to allow importing from api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from api.services.database import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

def check_count():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return
    
    db = DatabaseManager(database_url=db_url)
    try:
        results = db.execute_query("SELECT COUNT(*) as count FROM students")
        print(f"Current Student Count: {results[0]['count']}")
    except Exception as e:
        print(f"Error checking count: {e}")
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    check_count()
