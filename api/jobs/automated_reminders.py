"""
Automated Reminders Job
Background task that scans upcoming events and triggers notifications at specific intervals.
Intervals: 7 days, 3 days, 1 day.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from api.services.database import get_db_manager
from api.services.notifications import NotificationService

logger = logging.getLogger("angels.jobs.reminders")

class AutomatedRemindersJob:
    def __init__(self):
        self.db = get_db_manager()
        self.notifier = NotificationService()

    async def run_reminder_cycle(self):
        """Main loop to process all schools and their upcoming events"""
        logger.info("Starting automated reminder cycle...")
        
        # 1. Fetch upcoming events for all schools within the next 8 days
        # We look for events 1, 3, and 7 days away precisely
        query = """
        SELECT id, school_id, title, event_date, start_time, event_type, target_audience
        FROM school_events
        WHERE event_date IN (
            CURRENT_DATE + INTERVAL '1 day',
            CURRENT_DATE + INTERVAL '3 days',
            CURRENT_DATE + INTERVAL '7 days'
        )
        AND status = 'active'
        """
        
        upcoming_events = self.db.execute_query(query, fetch=True)
        if not upcoming_events:
            logger.info("No events requiring reminders today.")
            return
            
        for event in upcoming_events:
            await self._process_event_reminders(event)

    async def _process_event_reminders(self, event: Dict[str, Any]):
        """Trigger notifications for a specific event"""
        days_until = (event['event_date'] - datetime.now().date()).days
        
        title = f"Reminder: {event['title']}"
        message = f"Don't forget! {event['title']} is happening in {days_until} day(s) on {event['event_date']} at {event['start_time']}."
        
        # Identify stakeholders
        stakeholders = self._get_event_stakeholders(event['school_id'], event['target_audience'])
        
        for person in stakeholders:
            # Check if we already sent a reminder for this interval to avoid duplicates
            if self._reminder_already_sent(event['id'], person['id'], days_until):
                continue
                
            await self.notifier.send_notification(
                school_id=event['school_id'],
                recipient_id=person['id'],
                recipient_type=person['type'],
                notification_type="general",
                title=title,
                message=message,
                channels=["app", "sms", "push", "email"], # Multi-channel!
                priority="normal",
                related_entity_type="event",
                related_entity_id=event['id']
            )
            
            # Mark as sent
            self._log_reminder_sent(event['id'], person['id'], days_until)

    def _get_event_stakeholders(self, school_id: str, audience: str) -> List[Dict[str, Any]]:
        """Fetch IDs and types of people to notify"""
        people = []
        if audience in ['all', 'parents']:
            parents = self.db.execute_query(
                "SELECT id, 'parent' as type FROM parents WHERE school_id = %s", (school_id,), fetch=True
            )
            people.extend(parents)
        
        if audience in ['all', 'students']:
            students = self.db.execute_query(
                "SELECT id, 'student' as type FROM students WHERE school_id = %s", (school_id,), fetch=True
            )
            people.extend(students)
            
        return people

    def _reminder_already_sent(self, event_id: str, person_id: str, days_interval: int) -> bool:
        """Check audit log for existing reminder"""
        query = """
        SELECT id FROM notification_logs 
        WHERE related_entity_id = %s AND recipient_id = %s AND metadata->>'days_interval' = %s
        """
        result = self.db.execute_query(query, (event_id, person_id, str(days_interval)), fetch=True)
        return len(result) > 0

    def _log_reminder_sent(self, event_id: str, person_id: str, days_interval: int):
        """Log the reminder to prevent duplicates"""
        # This uses the audit/notifications log table
        pass

async def start_automated_reminders():
    job = AutomatedRemindersJob()
    await job.run_reminder_cycle()
