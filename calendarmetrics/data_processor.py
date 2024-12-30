from typing import List, Dict
import pandas as pd

class DataProcessor:
    """Process calendar events data into analyzable formats."""
    
    def __init__(self, events: List[Dict], config_loader):
        """Initialize processor with events data.
        
        Args:
            events: List of event dictionaries from CalendarParser
            config_loader: ConfigLoader instance with time period configurations
        """
        self.events = events
        self.config = config_loader
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Convert events to pandas DataFrame with calendar and custom quarters."""
        df = pd.DataFrame(self.events)
        
        # Basic time columns
        df['week'] = df['start'].dt.isocalendar().week
        df['year'] = df['start'].dt.year
        df['month'] = df['start'].dt.month
        
        # Calendar quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
        df['calendar_quarter'] = ((df['month'] - 1) // 3 + 1).astype(int)
        df['calendar_quarter_year'] = df.apply(
            lambda x: f"{x['year']} Q{x['calendar_quarter']}", axis=1
        )
        
        # Custom quarter based on fiscal year start
        fiscal_start_month = self.config.time_periods['default_periods']['year']['start_month']
        df['custom_quarter'] = ((df['month'] - fiscal_start_month) % 12 // 3 + 1).astype(int)
        
        # Fiscal year (e.g., if fiscal_start_month is 9, then Sept 2023 -> 2024)
        df['fiscal_year'] = df.apply(
            lambda x: x['year'] + (1 if x['month'] >= fiscal_start_month else 0),
            axis=1
        )
        
        return df
    
    def get_weekly_hours(self) -> pd.DataFrame:
        """Calculate hours per macro activities per week."""
        return (self.df.groupby(['year', 'week', 'macro_activities'])['duration']
                .sum()
                .reset_index())
    
    def get_calendar_quarter_percentages(self, quarter_year: str = None) -> pd.DataFrame:
        """Calculate percentages for calendar quarters.
        
        Args:
            quarter_year: Optional quarter-year string (e.g., "2023 Q3")
            
        Returns:
            DataFrame with activities percentages for the specified quarter or all data
        """
        if quarter_year:
            filtered = self.df[self.df['calendar_quarter_year'] == quarter_year]
        else:
            filtered = self.df
            
        total_hours = filtered['duration'].sum()
        if total_hours == 0:
            return pd.DataFrame(columns=['macro_activities', 'hours', 'percentage'])
            
        return (filtered.groupby('macro_activities')['duration']
                .agg(['sum', lambda x: (x.sum()/total_hours)*100])
                .rename(columns={'sum': 'hours', '<lambda_0>': 'percentage'})
                .reset_index())
    
    def get_fiscal_year_percentages(self, fiscal_year: int = None) -> pd.DataFrame:
        """Calculate percentages for fiscal years.
        
        Args:
            fiscal_year: Optional fiscal year (e.g., 2024 for FY2023-2024)
            
        Returns:
            DataFrame with activities percentages for the specified fiscal year or all data
        """
        if fiscal_year:
            filtered = self.df[self.df['fiscal_year'] == fiscal_year]
        else:
            filtered = self.df
            
        total_hours = filtered['duration'].sum()
        if total_hours == 0:
            return pd.DataFrame(columns=['macro_activities', 'hours', 'percentage'])
            
        return (filtered.groupby('macro_activities')['duration']
                .agg(['sum', lambda x: (x.sum()/total_hours)*100])
                .rename(columns={'sum': 'hours', '<lambda_0>': 'percentage'})
                .reset_index())
    
    def get_unique_periods(self) -> Dict[str, List]:
        """Get lists of unique calendar quarters and fiscal years in the data."""
        return {
            'calendar_quarters': sorted(self.df['calendar_quarter_year'].unique()),
            'fiscal_years': sorted(self.df['fiscal_year'].unique())
        }