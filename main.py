from calendarmetrics import CalendarParser, ConfigLoader, DataProcessor, Visualizer
from datetime import datetime, timedelta
import os

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Initialize components
    config = ConfigLoader('config')
    parser = CalendarParser(config)
    
    # Parse all calendar files
    print("Parsing calendar data...")
    all_events = []
    calendars_dir = os.path.join('input', 'calendars')
    
    for calendar_name, calendar_config in config.calendars.get('calendars', {}).items():
        ics_path = os.path.join(calendars_dir, calendar_config['file'])
        print(f"\nProcessing {calendar_name} calendar from {ics_path}...")
        try:
            events = parser.parse_ics(ics_path, calendar_config['category'])
            print(f"Found {len(events)} events in {calendar_name} calendar")
            all_events.extend(events)
        except Exception as e:
            print(f"Error processing {calendar_name} calendar: {str(e)}")
    
    print(f"\nTotal events found across all calendars: {len(all_events)}")
    
    # Process data
    print("\nProcessing events...") 
    processor = DataProcessor(all_events, config)
    
    # Save raw data
    output_excel = os.path.join('output', 'processed_events.xlsx')
    processor.df.to_excel(output_excel, index=False)
    print(f"Saved raw data to {output_excel}")
    print(f"Data shape: {processor.df.shape}")
    print("\nUnique macro activities found:", processor.df['macro_activities'].unique())
    
    # Get weekly hours
    weekly_hours = processor.get_weekly_hours()
    
    # Get all available periods
    periods = processor.get_unique_periods()
    
    # Create visualizations
    print("\nCreating visualizations...")
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
    
    print("\nAnalysis complete! Results saved in the 'output' directory.")

if __name__ == "__main__":
    main()