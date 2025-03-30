"""
Wind Display Component

This module provides a component for displaying wind data visualization.
"""
import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px

class WindDisplay:
    """
    A component for displaying wind data visualization.
    """
    
    def __init__(self):
        """Initialize the wind display component."""
        pass
    
    def render(self, forecast_data: Optional[Dict[str, Any]]) -> None:
        """
        Render the wind data visualization.
        
        Args:
            forecast_data: The forecast data containing wind information
        """
        if not forecast_data:
            st.info("No forecast data to display. Please enter a location.")
            return
        
        st.subheader("Wind Data")
        
        # Display wind direction indicators
        self._display_wind_direction_indicators(forecast_data['forecast'])
        
        # Display wind speed and gust chart
        self._display_wind_speed_chart(forecast_data['forecast'])
    
    def _display_wind_direction_indicators(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display wind direction indicators for each forecast day.
        
        Args:
            forecast_days: List of forecast days with wind direction data
        """
        # Create columns for each forecast day
        cols = st.columns(len(forecast_days))
        
        for i, day in enumerate(forecast_days):
            with cols[i]:
                st.markdown(f"**{day['date']}**")
                
                # Display wind direction arrow based on direction
                direction = day['wind_direction']
                arrow = self._get_direction_arrow(direction)
                
                st.markdown(f"<h1 style='text-align: center;'>{arrow}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{direction}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{day['wind_speed']} km/h</p>", unsafe_allow_html=True)
    
    def _display_wind_speed_chart(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display a chart showing wind speed and gust data.
        
        Args:
            forecast_days: List of forecast days with wind speed and gust data
        """
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Date': [day['date'] for day in forecast_days],
            'Wind Speed (km/h)': [day['wind_speed'] for day in forecast_days],
            'Wind Gust (km/h)': [day.get('wind_gust', day['wind_speed'] * 1.5) for day in forecast_days]
        })
        
        # Create a melted dataframe for the chart
        df_melted = pd.melt(df, id_vars=['Date'], 
                           value_vars=['Wind Speed (km/h)', 'Wind Gust (km/h)'], 
                           var_name='Measurement', value_name='Speed (km/h)')
        
        # Create the chart
        fig = px.bar(df_melted, x='Date', y='Speed (km/h)', color='Measurement',
                    barmode='group', title='Wind Speed and Gusts')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_direction_arrow(self, direction: str) -> str:
        """
        Get an arrow character representing wind direction.
        
        Args:
            direction: Wind direction as a string (e.g., 'N', 'NE', 'E', etc.)
            
        Returns:
            Arrow character representing the direction
        """
        direction = direction.upper()
        
        direction_arrows = {
            'N': '↓',
            'NNE': '↓↘',
            'NE': '↙',
            'ENE': '↙←',
            'E': '←',
            'ESE': '←↖',
            'SE': '↖',
            'SSE': '↑↖',
            'S': '↑',
            'SSW': '↑↗',
            'SW': '↗',
            'WSW': '→↗',
            'W': '→',
            'WNW': '→↘',
            'NW': '↘',
            'NNW': '↓↘'
        }
        
        # Return the arrow for the direction, or a default if not found
        return direction_arrows.get(direction, '•')