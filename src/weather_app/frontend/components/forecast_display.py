"""
Forecast Display Component

This module provides a component for displaying weather forecast information.
"""
import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px

class ForecastDisplay:
    """
    A component for displaying weather forecast information.
    """
    
    def __init__(self):
        """Initialize the forecast display component."""
        pass
    
    def render(self, forecast_data: Optional[Dict[str, Any]]) -> None:
        """
        Render the forecast display.
        
        Args:
            forecast_data: The forecast data to display
        """
        if not forecast_data:
            st.info("No forecast data to display. Please enter a location.")
            return
        
        st.subheader(f"Weather Forecast for {forecast_data['location']}")
        
        # Display forecast cards
        self._display_forecast_cards(forecast_data['forecast'])
        
        # Display temperature trend chart
        self._display_temperature_chart(forecast_data['forecast'])
        
        # Display precipitation chart
        self._display_precipitation_chart(forecast_data['forecast'])
    
    def _display_forecast_cards(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display forecast cards for each day.
        
        Args:
            forecast_days: List of forecast days
        """
        # Create columns for each forecast day
        cols = st.columns(len(forecast_days))
        
        for i, day in enumerate(forecast_days):
            with cols[i]:
                st.markdown(f"**{day['date']}**")
                
                # Display weather icon based on condition
                self._display_weather_icon(day['condition'])
                
                st.markdown(f"**{day['condition']}**")
                st.markdown(f"High: **{day['temperature_high']}°C**")
                st.markdown(f"Low: **{day['temperature_low']}°C**")
                st.markdown(f"Humidity: {day['humidity']}%")
                st.markdown(f"Wind: {day['wind_speed']} km/h {day['wind_direction']}")
                st.markdown(f"Precipitation: {day['precipitation_chance']}%")
    
    def _display_temperature_chart(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display a temperature trend chart.
        
        Args:
            forecast_days: List of forecast days
        """
        st.subheader("Temperature Trend")
        
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Date': [day['date'] for day in forecast_days],
            'High': [day['temperature_high'] for day in forecast_days],
            'Low': [day['temperature_low'] for day in forecast_days]
        })
        
        # Create a melted dataframe for the chart
        df_melted = pd.melt(df, id_vars=['Date'], value_vars=['High', 'Low'], 
                           var_name='Temperature Type', value_name='Temperature (°C)')
        
        # Create the chart
        fig = px.line(df_melted, x='Date', y='Temperature (°C)', color='Temperature Type',
                     markers=True, title='Temperature Forecast')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_precipitation_chart(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display a precipitation chance chart.
        
        Args:
            forecast_days: List of forecast days
        """
        st.subheader("Precipitation Chance")
        
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Date': [day['date'] for day in forecast_days],
            'Precipitation Chance (%)': [day['precipitation_chance'] for day in forecast_days]
        })
        
        # Create the chart
        fig = px.bar(df, x='Date', y='Precipitation Chance (%)', 
                    title='Precipitation Forecast')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_weather_icon(self, condition: str) -> None:
        """
        Display a weather icon based on the condition.
        
        Args:
            condition: The weather condition
        """
        condition = condition.lower()
        
        if "sunny" in condition or "clear" in condition:
            st.markdown("☀️")
        elif "partly cloudy" in condition:
            st.markdown("⛅")
        elif "cloudy" in condition:
            st.markdown("☁️")
        elif "rain" in condition:
            st.markdown("🌧️")
        elif "storm" in condition or "thunder" in condition:
            st.markdown("⛈️")
        elif "snow" in condition:
            st.markdown("❄️")
        elif "fog" in condition or "mist" in condition:
            st.markdown("🌫️")
        else:
            st.markdown("🌡️")