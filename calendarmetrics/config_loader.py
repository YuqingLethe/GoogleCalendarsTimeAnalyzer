import yaml
from typing import Dict, List, Optional
from datetime import datetime, date
from pathlib import Path

class ConfigLoader:
    """Configuration loader for CalendarMetrics."""
    
    def __init__(self, config_dir: str):
        """Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._load_configs()
        self._validate_dates()
    
    def __repr__(self) -> str:
        return f'ConfigLoader({self.config_dir})'
    
    def _load_configs(self) -> None:
        """Load all configuration files."""
        config_files = {
            'replacements': 'text_replacements.yaml',
            'holidays': 'holidays.yaml',
            'time_periods': 'time_periods.yaml',
            'calendars': 'calendars.yaml'
        }
        
        for attr, filename in config_files.items():
            filepath = self.config_dir / filename
            try:
                with open(filepath) as f:
                    setattr(self, attr, yaml.safe_load(f))
            except FileNotFoundError:
                print(f"Warning: {filename} not found in {self.config_dir}")
                setattr(self, attr, {})
    
    def _validate_dates(self) -> None:
        """Validate date formats in holidays and vacations."""
        if not self.holidays:
            return
            
        # Validate holidays
        for year, dates in self.holidays.get('holidays', {}).items():
            for date_str in dates:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Invalid date format in holidays: {date_str}")
        
        # Validate vacations
        for year, periods in self.holidays.get('vacations', {}).items():
            for period in periods:
                try:
                    datetime.strptime(period['start'], '%Y-%m-%d')
                    datetime.strptime(period['end'], '%Y-%m-%d')
                except (ValueError, KeyError) as e:
                    raise ValueError(f"Invalid vacation period: {period}")
                
                # Validate start date is before end date
                start = datetime.strptime(period['start'], '%Y-%m-%d').date()
                end = datetime.strptime(period['end'], '%Y-%m-%d').date()
                if start > end:
                    raise ValueError(
                        f"Vacation period start date {start} is after end date {end}"
                    )
    
    def get_text_replacements(self) -> Dict[str, str]:
        """Get text replacement mappings."""
        return self.replacements.get('replacements', {})
    
    def is_holiday_or_vacation(self, date_to_check: date) -> bool:
        """Check if date is a holiday or vacation day.
        
        Args:
            date_to_check: Date to check
            
        Returns:
            bool: True if date is a holiday or vacation day
        """
        if not self.holidays:
            return False
            
        year = str(date_to_check.year)
        date_str = date_to_check.strftime('%Y-%m-%d')
        
        # Check holidays
        holidays = self.holidays.get('holidays', {}).get(int(year), [])
        if date_str in holidays:
            return True
        
        # Check vacations
        vacations = self.holidays.get('vacations', {}).get(int(year), [])
        for vacation in vacations:
            start = datetime.strptime(vacation['start'], '%Y-%m-%d').date()
            end = datetime.strptime(vacation['end'], '%Y-%m-%d').date()
            if start <= date_to_check <= end:
                return True
        
        return False
    
    def get_active_range(self) -> Dict[str, str]:
        """Get the active time range for analysis.
        
        Returns:
            Dictionary containing start_date and end_date if configured
        """
        return self.time_periods.get('active_range', {})
    
    def get_all_holidays(self, year: Optional[int] = None) -> List[date]:
        """Get all holiday dates for a specific year or all years.
        
        Args:
            year: Optional year to filter holidays
            
        Returns:
            List of holiday dates
        """
        all_holidays = []
        years = [str(year)] if year else self.holidays.get('holidays', {}).keys()
        
        for yr in years:
            holidays = self.holidays.get('holidays', {}).get(yr, [])
            all_holidays.extend([
                datetime.strptime(date_str, '%Y-%m-%d').date()
                for date_str in holidays
            ])
        
        return sorted(all_holidays)
    
    def get_all_vacations(self, year: Optional[int] = None) -> List[Dict[str, date]]:
        """Get all vacation periods for a specific year or all years.
        
        Args:
            year: Optional year to filter vacations
            
        Returns:
            List of dictionaries containing vacation start and end dates
        """
        all_vacations = []
        years = [str(year)] if year else self.holidays.get('vacations', {}).keys()
        
        for yr in years:
            vacations = self.holidays.get('vacations', {}).get(yr, [])
            for vacation in vacations:
                all_vacations.append({
                    'start': datetime.strptime(vacation['start'], '%Y-%m-%d').date(),
                    'end': datetime.strptime(vacation['end'], '%Y-%m-%d').date(),
                    'description': vacation.get('description', '')
                })
        
        return sorted(all_vacations, key=lambda x: x['start'])