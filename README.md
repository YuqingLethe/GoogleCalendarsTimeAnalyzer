# Time-Tracker-Google-Calendar
Analyze time usage by processing events from various .ics files. It provides insights into activities time percentages and weekly distributions. Configurable files enable mapping, replacements, and customizations to generate metrics over user-defined periods.

## Output Examples

### Activities & Weekly Hours Distribution
![Sample Weekly Hours Distribution](docs/assets/images/sample.png)

## Features

- 📊 Visualize time allocation across different activities
- 📅 Analyze weekly work patterns
- ⚙️ Configurable activities categorization with macro and micro activities
- 🔄 Text replacement for consistency
- 📌 Holiday and vacation handling
- 📈 Custom time period analysis with fiscal year support
- 🎨 Customizable color schemes for visualizations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gabrielesanticchi/Time-Tracker-Google-Calendar.git
cd calendarmetrics
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Export your Google Calendar to ICS format:
   - Go to Google Calendar Settings
   - Navigate to "Import & Export"
   - Click "Export" to download your calendar as ICS

2. Place the ICS file in the `input` directory as `calendar.ics`

3. Configure your settings (see Configuration section)

4. Run the analysis:
```bash
python main.py 
```

## Configuration

CalendarMetrics uses YAML configuration files located in the `config/` directory:

### 1. Calendars (`calendars.yaml`)

This file defines your calendar categories and their properties:

```yaml
calendars:
  work:
    file: "2Work.ics"
    category: "WORK"
    color: "#4287f5"
    description: "Work-related activities"
    
  sleep:
    file: "3Sleep.ics"
    category: "SLEEP"
    color: "#f54242"
    description: "Sleep activities"
    
  errands:
    file: "4Errands.ics"
    category: "ERRANDS"
    color: "#42f554"
    description: "Errand activities"
```

### 2. Text Replacements (`text_replacements.yaml`)

Define common typos or variations to be standardized:

```yaml
replacements:
  "meting": "meeting"
  "developement": "development"
  "synq": "sync"
```

### 3. Holidays and Vacations (`holidays.yaml`)

Specify dates to exclude from analysis by year:

```yaml
holidays:
  2024:
    - "2024-01-01"  # New Year's Day
    - "2024-12-25"  # Christmas

vacations:
  2024:
    - start: "2024-07-15"
      end: "2024-07-30"
      description: "Summer Break"
```

### 4. Time Periods (`time_periods.yaml`)

Define fiscal year settings and analysis date range:

```yaml
default_periods:
  quarter:
    start_month: 9  # September
    duration_months: 3
  year:
    start_month: 9  # September
    end_month: 8    # August next year

active_range:
  start_date: "2024-01-01"
  end_date: "2024-12-31"
```

## Calendar Event Format

With the multi-calendar approach, each calendar file should contain events for a specific category. The event summaries can be in any format since the categorization is now handled by the calendar file itself.

Example event summaries:
- Work calendar: "Team meeting", "Project planning", "Code review"
- Sleep calendar: "Sleep", "Nap", "Rest"
- Errands calendar: "Grocery shopping", "Doctor appointment", "Car maintenance"

## Output

The tool generates several visualizations in the `