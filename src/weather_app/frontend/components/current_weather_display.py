"""
Current Weather Display Component

This module provides a component for displaying current weather information.
"""
import streamlit as st
from typing import Dict, Any, Optional

class CurrentWeatherDisplay:
    """
    A component for displaying current weather information.
    """
    
    def __init__(self):
        """Initialize the current weather display component."""
        pass
    
    def render(self, weather_data: Optional[Dict[str, Any]]) -> None:
        """
        Render the current weather display.
        
        Args:
            weather_data: The weather data to display
        """
        if not weather_data:
            st.info("No weather data to display. Please enter a location.")
            return
        
        st.subheader(f"Current Weather in {weather_data['location']}")
        
        # Create columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Display main weather information
            st.metric("Temperature", f"{weather_data['temperature']}°C")
            st.metric("Humidity", f"{weather_data['humidity']}%")
            st.metric("Wind", f"{weather_data['wind_speed']} km/h {weather_data['wind_direction']}")
        
        with col2:
            # Display condition and timestamp
            st.markdown(f"**Condition:** {weather_data['condition']}")
            st.markdown(f"**Last Updated:** {weather_data['timestamp']}")
            
            # Display weather icon based on condition
            self._display_weather_icon(weather_data['condition'])
    
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