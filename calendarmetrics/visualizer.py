import plotly.graph_objects as go
import plotly.express as px
from typing import Dict
import pandas as pd


class Visualizer:
    def __init__(self, config_loader):
        self.config = config_loader
        # Get colors from calendars configuration
        self.colors = {
            calendar['category']: calendar['color']
            for calendar in self.config.calendars.get('calendars', {}).values()
        }
        
        self.layout_settings = dict(
            font=dict(family="Montserrat, sans-serif", color='white'),
            paper_bgcolor='rgb(17, 17, 17)',
            plot_bgcolor='rgb(17, 17, 17)',
            title_font=dict(family="Montserrat, sans-serif", size=24, color='white'),
            showlegend=True,
            legend=dict(
                font=dict(family="Montserrat, sans-serif", color='white'),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(255,255,255,0.1)'
            )
        )

    def plot_weekly_hours(self, df: pd.DataFrame) -> go.Figure:
        pivot = df.pivot(index=['year', 'week'], columns='macro_activities', values='duration').round(1)
        week_labels = [f"{year} W{week}" for year, week in pivot.index]
        
        fig = go.Figure()
        
        for column in pivot.columns:
            color = self.colors.get(column, '#808080')  # Default gray if no color defined
            fig.add_trace(go.Bar(
                name=column,
                x=week_labels,
                y=pivot[column],
                marker_color=color
            ))
        
        fig.update_layout(
            **self.layout_settings,
            title='Hours per Macro-activities per Week',
            xaxis=dict(
                title='Week',
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(family="Montserrat, sans-serif", color='white')
            ),
            yaxis=dict(
                title='Hours',
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(family="Montserrat, sans-serif", color='white')
            ),
            barmode='stack',
            legend_title=dict(
                text='Macro-activities',
                font=dict(family="Montserrat, sans-serif", color='white')
            ),
            height=600,
            width=1200
        )
        
        return fig
        
    def plot_activities_percentages(self, df: pd.DataFrame, title: str = "Hours per Macro-activities") -> go.Figure:
        df['percentage'] = df['percentage'].round(1)
        
        colors = [self.colors.get(activities, '#808080') for activities in df['macro_activities']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df['macro_activities'],
            values=df['percentage'],
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='auto',
            textfont=dict(family="Montserrat, sans-serif", color='white'),
            hovertemplate="<b>%{label}</b><br>Hours: %{value:.1f}<br>Percentage: %{percent}<extra></extra>"
        )])
        
        fig.update_layout(
            **self.layout_settings,
            title=title,
            height=800,
            width=800
        )
        
        return fig