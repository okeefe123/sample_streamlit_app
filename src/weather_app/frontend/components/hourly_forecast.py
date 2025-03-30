"""
Hourly Forecast Component

This module provides a component for displaying hourly weather forecast in a scrollable view.
"""
import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px

class HourlyForecast:
    """
    A component for displaying hourly weather forecast in a scrollable view.
    """
    
    def __init__(self):
        """Initialize the hourly forecast component."""
        pass
    
    def render(self, hourly_data: Optional[Dict[str, Any]]) -> None:
        """
        Render the hourly forecast scrollable view.
        
        Args:
            hourly_data: The hourly forecast data to display
        """
        if not hourly_data:
            st.info("No hourly forecast data to display. Please enter a location.")
            return
        
        st.subheader("Hourly Forecast")
        
        # Create a scrollable container for the hourly forecast
        with st.container():
            # Display hourly forecast cards
            self._display_hourly_cards(hourly_data['hourly_forecast'])
            
            # Display temperature trend chart
            self._display_temperature_trend(hourly_data['hourly_forecast'])
            
            # Display precipitation chance chart
            self._display_precipitation_chance(hourly_data['hourly_forecast'])
    
    def _display_hourly_cards(self, hourly_forecast: List[Dict[str, Any]]) -> None:
        """
        Display hourly forecast cards in a horizontal scrollable view.
        
        Args:
            hourly_forecast: List of hourly forecast data points
        """
        # Create a horizontal layout with columns
        cols = st.columns(len(hourly_forecast))
        
        for i, hour in enumerate(hourly_forecast):
            with cols[i]:
                # Display time
                st.markdown(f"**{hour['time']}**")
                
                # Display weather icon based on condition
                self._display_weather_icon(hour['condition'])
                
                # Display temperature
                st.markdown(f"<h3 style='text-align: center;'>{hour['temperature']}°C</h3>", unsafe_allow_html=True)
                
                # Display condition
                st.markdown(f"<p style='text-align: center;'>{hour['condition']}</p>", unsafe_allow_html=True)
                
                # Display precipitation chance
                precip_color = self._get_precipitation_color(hour['precipitation_chance'])
                st.markdown(
                    f"<p style='text-align: center; color: {precip_color};'>💧 {hour['precipitation_chance']}%</p>",
                    unsafe_allow_html=True
                )
                
                # Display wind
                st.markdown(
                    f"<p style='text-align: center;'>🌬️ {hour['wind_speed']} km/h {hour['wind_direction']}</p>",
                    unsafe_allow_html=True
                )
                
                # Display humidity
                st.markdown(
                    f"<p style='text-align: center;'>💦 {hour['humidity']}%</p>",
                    unsafe_allow_html=True
                )
    
    def _display_temperature_trend(self, hourly_forecast: List[Dict[str, Any]]) -> None:
        """
        Display a temperature trend chart for the hourly forecast.
        
        Args:
            hourly_forecast: List of hourly forecast data points
        """
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Time': [hour['time'] for hour in hourly_forecast],
            'Temperature (°C)': [hour['temperature'] for hour in hourly_forecast]
        })
        
        # Create the chart
        fig = px.line(df, x='Time', y='Temperature (°C)', 
                     markers=True, title='Hourly Temperature Trend')
        
        # Update layout to show grid lines and improve readability
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Temperature (°C)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_precipitation_chance(self, hourly_forecast: List[Dict[str, Any]]) -> None:
        """
        Display a precipitation chance chart for the hourly forecast.
        
        Args:
            hourly_forecast: List of hourly forecast data points
        """
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Time': [hour['time'] for hour in hourly_forecast],
            'Precipitation Chance (%)': [hour['precipitation_chance'] for hour in hourly_forecast],
            'Humidity (%)': [hour['humidity'] for hour in hourly_forecast]
        })
        
        # Create the chart
        fig = px.bar(df, x='Time', y=['Precipitation Chance (%)', 'Humidity (%)'],
                    barmode='group', title='Hourly Precipitation and Humidity')
        
        # Update layout to show grid lines and improve readability
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Percentage (%)',
            legend_title='Measurement',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_weather_icon(self, condition: str) -> None:
        """
        Display a weather icon based on the condition.
        
        Args:
            condition: The weather condition
        """
        condition = condition.lower()
        
        if "sunny" in condition or "clear" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>☀️</div>", unsafe_allow_html=True)
        elif "partly cloudy" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>⛅</div>", unsafe_allow_html=True)
        elif "cloudy" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>☁️</div>", unsafe_allow_html=True)
        elif "rain" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>🌧️</div>", unsafe_allow_html=True)
        elif "storm" in condition or "thunder" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>⛈️</div>", unsafe_allow_html=True)
        elif "snow" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>❄️</div>", unsafe_allow_html=True)
        elif "fog" in condition or "mist" in condition:
            st.markdown("<div style='text-align: center; font-size: 28px;'>🌫️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; font-size: 28px;'>🌡️</div>", unsafe_allow_html=True)
    
    def _get_precipitation_color(self, precipitation_chance: int) -> str:
        """
        Get a color representing the precipitation chance.
        
        Args:
            precipitation_chance: Precipitation chance percentage
            
        Returns:
            Hex color code representing the precipitation chance
        """
        if precipitation_chance < 20:
            return "#90EE90"  # Light green (low chance)
        elif precipitation_chance < 50:
            return "#FFD700"  # Gold (moderate chance)
        elif precipitation_chance < 80:
            return "#FFA500"  # Orange (high chance)
        else:
            return "#FF4500"  # OrangeRed (very high chance)