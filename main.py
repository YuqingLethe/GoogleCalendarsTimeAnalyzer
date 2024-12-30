from calendarmetrics import CalendarParser, ConfigLoader, DataProcessor, Visualizer
from datetime import datetime, timedelta
import os

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Initialize components
    config = ConfigLoader('config')
    parser = CalendarParser(config)
    
    # Parse calendar file
    print("Parsing calendar data...")
    events = parser.parse_ics(os.path.join('input', 'calendar.ics'))
    
    # Process data
    print("Processing events...") 
    processor = DataProcessor(events, config)
    processor.df.to_excel(os.path.join('output', 'processed_events.xlsx'), index=False)
    # Get weekly hours
    weekly_hours = processor.get_weekly_hours()
    
    # Get all available periods
    periods = processor.get_unique_periods()
    
    # Create visualizations
    print("Creating visualizations...")
    viz = Visualizer(config)
    
    # Weekly hours plot
    fig_weekly = viz.plot_weekly_hours(weekly_hours)
    fig_weekly.write_html(os.path.join('output', 'weekly_hours.html'))
    
    # Calendar quarter percentages
    for quarter in periods['calendar_quarters']:
        quarter_data = processor.get_calendar_quarter_percentages(quarter)
        fig_quarter = viz.plot_activities_percentages(quarter_data, f"Activities Distribution - {quarter}")
        fig_quarter.write_html(os.path.join('output', f'percentages_{quarter.replace(" ", "_")}.html'))
    
    # Fiscal year percentages
    for year in periods['fiscal_years']:
        year_data = processor.get_fiscal_year_percentages(year)
        fig_year = viz.plot_activities_percentages(year_data, f"Activities Distribution - FY{year-1}-{year}")
        fig_year.write_html(os.path.join('output', f'percentages_FY_{year-1}_{year}.html'))
    
    print("Analysis complete! Results saved in the 'output' directory.")

if __name__ == '__main__':
    main()