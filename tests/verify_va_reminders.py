import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from api.jobs.automated_reminders import AutomatedRemindersJob
from api.services.database import get_db_manager
from dotenv import load_dotenv

async def verify_reminders():
    load_dotenv()
    print("Starting Automated Reminder Verification...")
    db = get_db_manager()
    
    school_id = "00000000-0000-0000-0000-000000000001"
    
    # 0. Ensure school exists
    print("Ensuring test school exists...")
    db.execute_query("INSERT INTO schools (id, name) VALUES (%s, 'Test School') ON CONFLICT DO NOTHING", (school_id,), fetch=False)
    
    # 1. Clear existing events for testing
    print("Cleaning up test events...")
    db.execute_query("DELETE FROM school_events WHERE title LIKE 'TEST_EVENT%'", fetch=False)
    
    # 2. Setup mock events for 1, 3, and 7 days away
    # Note: INTERVAL usage depends on Postgres version, assuming standard here
    print("Injecting test events for 1, 3, and 7 days intervals...")
    school_id = "00000000-0000-0000-0000-000000000001"
    
    db.execute_query("""
    INSERT INTO school_events (school_id, title, event_type, event_date, start_time, end_time, location, target_audience)
    VALUES 
    (%s, 'TEST_EVENT_1DAY', 'sports', CURRENT_DATE + INTERVAL '1 day', '10:00', '12:00', 'Field', ARRAY['all']),
    (%s, 'TEST_EVENT_3DAYS', 'meeting', CURRENT_DATE + INTERVAL '3 days', '14:00', '15:00', 'Hall', ARRAY['parents']),
    (%s, 'TEST_EVENT_7DAYS', 'concert', CURRENT_DATE + INTERVAL '7 days', '18:00', '20:00', 'Stage', ARRAY['all'])
    """, (school_id, school_id, school_id), fetch=False)

    # 3. Define a fake recipient to avoid database errors in get_stakeholders
    print("Creating mock stakeholders if they don't exist...")
    parent_id = "00000000-0000-0000-0000-000000000002"
    teacher_id = "00000000-0000-0000-0000-000000000003"
    
    db.execute_query("INSERT INTO parents (id, school_id, first_name, last_name, phone, email) VALUES (%s, %s, 'Test', 'Parent', '+256700000000', 'test@example.com') ON CONFLICT DO NOTHING", (parent_id, school_id), fetch=False)
    db.execute_query("INSERT INTO teachers (id, school_id, first_name, last_name, phone, email, employee_number) VALUES (%s, %s, 'Test', 'Teacher', '+256700000001', 'teacher@example.com', 'T-001') ON CONFLICT DO NOTHING", (teacher_id, school_id), fetch=False)

    # 4. Run the Job
    print("Running AutomatedRemindersJob.run_reminder_cycle()...")
    job = AutomatedRemindersJob()
    await job.run_reminder_cycle()
    
    print("Verification Run Complete. Check console logs for dispatch messages.")

if __name__ == "__main__":
    asyncio.run(verify_reminders())
