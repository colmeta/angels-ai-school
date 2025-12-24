"""
Google Calendar Sync Service
Handles synchronization between internal school events and external Google Calendars.
Supports "Auto-Blocking" for staff and parents.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from api.core.config import get_settings
from api.services.database import get_db_manager

logger = logging.getLogger("angels.calendar")

class CalendarSyncService:
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.settings = get_settings()
        self.db = get_db_manager()
        self.service = self._get_calendar_service()

    def _get_calendar_service(self):
        """Initialize Google Calendar API client using service account"""
        try:
            # In production, this would be a real service account JSON file
            # For this audit/implementation, we assume the environment has the credentials
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not creds_path or not os.path.exists(creds_path):
                logger.warning("Google Calendar credentials not found. Operating in MOCK mode.")
                return None
            
            creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=['https://www.googleapis.com/auth/calendar']
            )
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            return None

    def sync_event_to_stakeholders(self, event_id: str) -> Dict[str, Any]:
        """
        Main entry point to sync an event to all relevant stakeholders.
        Finds teachers and parents, then injects the event into their calendars.
        """
        # 1. Fetch event details
        event_query = "SELECT * FROM school_events WHERE id = %s AND school_id = %s"
        event = self.db.execute_query(event_query, (event_id, self.school_id), fetch=True)
        if not event:
            return {"success": False, "error": "Event not found"}
        
        event = event[0]
        
        # 2. Identify stakeholders based on target_audience
        stakeholders = self._get_stakeholders(event['target_audience'])
        
        # 3. Formulate Google Calendar Event object
        g_event = {
            'summary': f"[{event['event_type'].upper()}] {event['title']}",
            'location': event['location'],
            'description': event['description'],
            'start': {
                'dateTime': f"{event['event_date']}T{event['start_time']}:00",
                'timeZone': 'Africa/Kampala',
            },
            'end': {
                'dateTime': f"{event['event_date']}T{event['end_time']}:00",
                'timeZone': 'Africa/Kampala',
            },
            'attendees': [{'email': s['email']} for s in stakeholders if s.get('email')],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
            'transparency': 'opaque', # This blocks the calendar
        }

        if not self.service:
            logger.info(f"MOCK SYNC: Event '{event['event_name']}' would be synced to {len(stakeholders)} stakeholders.")
            return {"success": True, "mock": True, "stakeholder_count": len(stakeholders)}

        try:
            # Sync to the School's Master Calendar (or specific user calendars if delegated)
            created_event = self.service.events().insert(calendarId='primary', body=g_event, sendUpdates='all').execute()
            
            # Save the external ID for future updates
            self.db.execute_query(
                "UPDATE school_events SET external_id = %s WHERE id = %s",
                (created_event['id'], event_id), fetch=False
            )
            
            return {"success": True, "external_id": created_event['id']}
        except HttpError as error:
            logger.error(f"Google Calendar API Error: {error}")
            return {"success": False, "error": str(error)}

    def _get_stakeholders(self, target_audience: str) -> List[Dict[str, Any]]:
        """Fetch emails of parents and teachers based on audience"""
        emails = []
        
        # Teachers are usually always included for school-wide events
        if target_audience in ['all', 'parents', 'students']:
            teacher_query = "SELECT email FROM teachers WHERE school_id = %s"
            teachers = self.db.execute_query(teacher_query, (self.school_id,), fetch=True)
            emails.extend(teachers)
            
        if target_audience in ['all', 'parents']:
            parent_query = "SELECT email FROM parents WHERE school_id = %s"
            parents = self.db.execute_query(parent_query, (self.school_id,), fetch=True)
            emails.extend(parents)
            
        return emails

def get_calendar_sync_service(school_id: str) -> CalendarSyncService:
    return CalendarSyncService(school_id)
