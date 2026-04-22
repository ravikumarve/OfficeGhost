"""
AI Office Pilot - Calendar Integration
Local .ics file parsing and meeting management
"""

import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

from core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Calendar event data"""
    uid: str
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    organizer: Optional[str] = None
    attendees: list[str] = None
    rrule: Optional[str] = None

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class ICSParseError(Exception):
    """ICS parsing errors"""
    pass


class CalendarManager:
    """Manage calendar events from .ics files"""

    VCALENDAR_START = "BEGIN:VCALENDAR"
    VCALENDAR_END = "END:VCALENDAR"
    VEVENT_START = "BEGIN:VEVENT"
    VEVENT_END = "END:VEVENT"

    def __init__(self) -> None:
        self.events: list[CalendarEvent] = []
        self._load_events()

    def _get_calendar_dir(self) -> Path:
        """Get calendar directory"""
        calendar_dir = Config.CALENDAR_DIR
        calendar_dir.mkdir(parents=True, exist_ok=True)
        return calendar_dir

    def _load_events(self) -> None:
        """Load events from .ics files"""
        calendar_dir = self._get_calendar_dir()

        for ics_file in calendar_dir.glob("*.ics"):
            try:
                self._parse_ics_file(ics_file)
            except Exception as e:
                logger.warning(f"Failed to parse {ics_file}: {e}")

        logger.info(f"Loaded {len(self.events)} calendar events")

    def _parse_ics_file(self, file_path: Path) -> None:
        """Parse a single .ics file"""
        content = file_path.read_text()
        self._parse_ics_content(content)

    def _parse_ics_content(self, content: str) -> None:
        """Parse ICS content string"""
        lines = self._fold_lines(content)
        in_event = False
        current_event: dict = {}

        for line in lines:
            if line.startswith(self.VEVENT_START):
                in_event = True
                current_event = {}
            elif line.startswith(self.VEVENT_END) and in_event:
                in_event = False
                event = self._create_event(current_event)
                if event:
                    self.events.append(event)
            elif in_event:
                self._parse_event_line(line, current_event)

    def _fold_lines(self, content: str) -> list[str]:
        """Handle ICS line folding"""
        lines = []
        for line in content.split("\n"):
            if line.startswith(" ") or line.startswith("\t"):
                if lines:
                    lines[-1] += line[1:]
                else:
                    lines.append(line)
            else:
                lines.append(line)
        return [l.strip() for l in lines if l.strip()]

    def _parse_event_line(self, line: str, event: dict) -> None:
        """Parse a single event property line"""
        if ":" not in line:
            return

        key, _, value = line.partition(":")

        # Handle parameters
        if ";" in key:
            key = key.split(";")[0]

        key = key.upper()

        if key == "SUMMARY":
            event["summary"] = value
        elif key == "DESCRIPTION":
            event["description"] = value.replace("\\n", "\n")
        elif key == "LOCATION":
            event["location"] = value
        elif key == "DTSTART":
            event["start"] = self._parse_datetime(value)
        elif key == "DTEND":
            event["end"] = self._parse_datetime(value)
        elif key == "ORGANIZER":
            event["organizer"] = self._parse_organizer(value)
        elif key == "ATTENDEE":
            if "attendees" not in event:
                event["attendees"] = []
            event["attendees"].append(self._parse_attendee(value))
        elif key == "RRULE":
            event["rrule"] = value
        elif key == "UID":
            event["uid"] = value

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        """Parse ICS datetime string"""
        try:
            if "T" in value:
                if value.endswith("Z"):
                    return datetime.strptime(value, "%Y%m%dT%H%M%SZ")
                return datetime.strptime(value, "%Y%m%dT%H%M%S")
            return datetime.strptime(value, "%Y%m%d")
        except Exception:
            return None

    def _parse_organizer(self, value: str) -> str:
        """Parse organizer email"""
        if "mailto:" in value:
            return value.replace("mailto:", "")
        return value

    def _parse_attendee(self, value: str) -> str:
        """Parse attendee email"""
            if "mailto:" in value:
                return value.replace("mailto:", "")
            return value

    def _create_event(self, data: dict) -> Optional[CalendarEvent]:
        """Create CalendarEvent from parsed data"""
        if "summary" not in data:
            return None

        return CalendarEvent(
            uid=data.get("uid", ""),
            summary=data["summary"],
            description=data.get("description"),
            location=data.get("location"),
            start=data.get("start"),
            end=data.get("end"),
            organizer=data.get("organizer"),
            attendees=data.get("attendees", []),
            rrule=data.get("rrule")
        )

    def process_meeting_request(
        self,
        email_body: str,
        sender_email: str,
        sender_name: str
    ) -> Optional[dict]:
        """
        Process meeting request from email and generate response options
        
        Args:
            email_body: Email body content
            sender_email: Sender's email address
            sender_name: Sender's name
            
        Returns:
            Dict with meeting details and response options
        """
        meeting = self.parse_email_meeting(email_body)
        
        if not meeting:
            return None
        
        # Check for conflicts
        has_conflict = False
        if meeting.start and meeting.end:
            has_conflict = self.is_meeting_conflict(meeting.start, meeting.end)
        
        # Find available time slots if there's a conflict
        free_slots = []
        if has_conflict and meeting.start:
            free_slots = self.find_free_slots(
                duration_minutes=int(
                    (meeting.end - meeting.start).total_seconds() / 60
                ) if meeting.end and meeting.start else 30,
                start_date=meeting.start,
                days=3
            )[:3]
        
        return {
            "meeting": {
                "summary": meeting.summary,
                "start": meeting.start.isoformat() if meeting.start else None,
                "end": meeting.end.isoformat() if meeting.end else None,
                "location": meeting.location,
                "organizer": meeting.organizer,
                "attendees": meeting.attendees
            },
            "has_conflict": has_conflict,
            "suggested_times": [
                {"start": s[0].isoformat(), "end": s[1].isoformat()}
                for s in free_slots
            ],
            "response_options": self._generate_response_options(has_conflict)
        }

    def _generate_response_options(self, has_conflict: bool) -> list[dict]:
        """Generate meeting response options"""
        options = [
            {"action": "accept", "label": "Accept", "template": "Accept"},
            {"action": "tentative", "label": "Tentative", "template": "Tentative"},
            {"action": "decline", "label": "Decline", "template": "Decline"},
        ]
        
        if has_conflict:
            options.append({
                "action": "propose_new_time",
                "label": "Propose New Time",
                "template": "Counter Proposal"
            })
        
        return options

    def respond_to_meeting(
        self,
        meeting: CalendarEvent,
        response: str,
        custom_message: Optional[str] = None
    ) -> str:
        """
        Generate meeting response email
        
        Args:
            meeting: The meeting event
            response: Response type (accept, tentative, decline, propose_new_time)
            custom_message: Optional custom message
            
        Returns:
            Response email content
        """
        response_templates = {
            "accept": "Thank you for the invitation. I am pleased to confirm my attendance.",
            "tentative": "Thank you for the invitation. I may be able to attend, but need to confirm.",
            "decline": "Thank you for the invitation. Unfortunately, I am unable to attend.",
            "propose_new_time": "Thank you for the invitation. I have a conflict at that time. Would the following times work for you?"
        }
        
        base_response = response_templates.get(response, response_templates["tentative"])
        
        if custom_message:
            response_text = f"{base_response}\n\n{custom_message}"
        else:
            response_text = base_response
        
        return response_text

    def get_upcoming(self, hours: int = 24) -> list[CalendarEvent]:
        """Get upcoming events"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)

        upcoming = [
            e for e in self.events
            if e.start and now <= e.start <= cutoff
        ]

        return sorted(upcoming, key=lambda e: e.start)

    def get_today(self) -> list[CalendarEvent]:
        """Get today's events"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        return [
            e for e in self.events
            if e.start and today_start <= e.start < today_end
        ]

    def is_meeting_conflict(self, start: datetime, end: datetime) -> bool:
        """Check if time slot conflicts with existing events"""
        for event in self.events:
            if not event.start or not event.end:
                continue
            if event.start < end and event.end > start:
                return True
        return False

    def find_free_slots(
        self,
        duration_minutes: int,
        start_date: Optional[datetime] = None,
        days: int = 7
    ) -> list[tuple[datetime, datetime]]:
        """Find free time slots"""
        if start_date is None:
            start_date = datetime.now()

        free_slots = []
        current = start_date.replace(hour=9, minute=0)

        for _ in range(days * 24):
            end = current + timedelta(minutes=duration_minutes)

            if end.hour <= 17 and not self.is_meeting_conflict(current, end):
                free_slots.append((current, end))

            current = current + timedelta(minutes=30)

        return free_slots

    def add_event(self, event: CalendarEvent) -> None:
        """Add event to calendar"""
        self.events.append(event)
        self._save_event(event)

    def _save_event(self, event: CalendarEvent) -> None:
        """Save event to .ics file"""
        calendar_dir = self._get_calendar_dir()
        ics_file = calendar_dir / f"{event.uid}.ics"

        content = self._generate_ics(event)
        ics_file.write_text(content)

    def _generate_ics(self, event: CalendarEvent) -> str:
        """Generate ICS content for an event"""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//AI Office Pilot//Calendar//EN",
            "BEGIN:VEVENT",
            f"UID:{event.uid}",
            f"SUMMARY:{event.summary}",
        ]

        if event.start:
            lines.append(f"DTSTART:{event.start.strftime('%Y%m%dT%H%M%S')}")
        if event.end:
            lines.append(f"DTEND:{event.end.strftime('%Y%m%dT%H%M%S')}")
        if event.location:
            lines.append(f"LOCATION:{event.location}")
        if event.description:
            lines.append(f"DESCRIPTION:{event.description}")
        if event.organizer:
            lines.append(f"ORGANIZER:mailto:{event.organizer}")
        for attendee in event.attendees:
            lines.append(f"ATTENDEE:mailto:{attendee}")

        lines.extend([
            "END:VEVENT",
            "END:VCALENDAR"
        ])

        return "\r\n".join(lines)

    def parse_email_meeting(self, email_body: str) -> Optional[CalendarEvent]:
        """Parse meeting request from email body"""
        ics_pattern = r"BEGIN:VCALENDAR.*?END:VCALENDAR"
        match = re.search(ics_pattern, email_body, re.DOTALL)

        if match:
            try:
                self._parse_ics_content(match.group())
                return self.events[-1] if self.events else None
            except Exception as e:
                logger.warning(f"Failed to parse meeting from email: {e}")

        return None