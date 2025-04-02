from typing import Dict, List, Optional, Tuple
import icalendar
from datetime import datetime, timedelta, date
import pytz

class CalendarParser:
    """Parser for Google Calendar ICS files."""
    
    def __init__(self, config_loader):
        """Initialize parser with configuration.
        
        Args:
            config_loader: ConfigLoader instance with replacements and activities mappings
        """
        self.config = config_loader
        self.time_range = self._get_time_range()
        
    def _get_time_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get configured time range from config."""
        active_range = self.config.get_active_range()
        start_date = None
        end_date = None
        
        if active_range:
            if 'start_date' in active_range:
                start_date = datetime.strptime(active_range['start_date'], '%Y-%m-%d')
                start_date = start_date.replace(hour=0, minute=0, second=0)
                # Convert to UTC then remove timezone info
                start_date = pytz.UTC.localize(start_date).replace(tzinfo=None)
                
            if 'end_date' in active_range:
                end_date = datetime.strptime(active_range['end_date'], '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)
                # Convert to UTC then remove timezone info
                end_date = pytz.UTC.localize(end_date).replace(tzinfo=None)
                
        return start_date, end_date
        
    def _convert_to_utc(self, dt: datetime) -> datetime:
        """Convert datetime to UTC and strip timezone information."""
        if dt.tzinfo is None:
            # If naive, assume it's UTC
            return dt
        # Convert to UTC then remove timezone info
        return dt.astimezone(pytz.UTC).replace(tzinfo=None)
        
    def parse_ics(self, ics_path: str, calendar_category: str) -> List[Dict]:
        """Parse ICS file and extract relevant event information.
        
        Args:
            ics_path: Path to the ICS file
            calendar_category: Category of the calendar (e.g., "WORK", "PERSONAL")
            
        Returns:
            List of event dictionaries
        """
        events = []
        start_date, end_date = self.time_range

        with open(ics_path, 'rb') as f:
            cal = icalendar.Calendar.from_ical(f.read())
            
            for event in cal.walk('vevent'):
                event_start = event.get('dtstart').dt
                event_end = event.get('dtend').dt
                
                # Handle all-day events
                if isinstance(event_start, date) and not isinstance(event_start, datetime):
                    event_start = datetime.combine(event_start, datetime.min.time())
                    event_end = datetime.combine(event_end, datetime.max.time())
                
                # Convert to UTC and strip timezone info
                event_start = self._convert_to_utc(event_start)
                event_end = self._convert_to_utc(event_end)
                
                # Apply time range filtering
                if start_date and event_end < start_date:
                    continue
                if end_date and event_start > end_date:
                    continue
                
                summary = str(event.get('summary', ''))
                
                # Skip if event occurs on holiday/vacation
                if self._is_holiday_or_vacation(event_start.date()):
                    continue
                
                # Apply text replacements
                summary = self._apply_replacements(summary)
                
                # Calculate duration in hours
                duration = self._calculate_duration(event_start, event_end)
                
                events.append({
                    'start': event_start,
                    'end': event_end,
                    'macro_activities': calendar_category,
                    'micro_activities': summary,
                    'duration': duration,
                    'calendar': calendar_category
                })
                    
        return events
    
    def _apply_replacements(self, text: str) -> str:
        """Apply configured text replacements."""
        for old, new in self.config.get_text_replacements().items():
            text = text.replace(old, new)
        return text
    
    def _calculate_duration(self, start: datetime, end: datetime) -> float:
        """Calculate event duration in hours."""
        return (end - start).total_seconds() / 3600
    
    def _is_holiday_or_vacation(self, date: datetime.date) -> bool:
        """Check if date is a holiday or vacation day."""
        return self.config.is_holiday_or_vacation(date)