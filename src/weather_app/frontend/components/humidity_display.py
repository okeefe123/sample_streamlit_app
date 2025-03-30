"""
Humidity Display Component

This module provides a component for displaying humidity visualization.
"""
import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px

class HumidityDisplay:
    """
    A component for displaying humidity visualization.
    """
    
    def __init__(self):
        """Initialize the humidity display component."""
        pass
    
    def render(self, forecast_data: Optional[Dict[str, Any]]) -> None:
        """
        Render the humidity visualization.
        
        Args:
            forecast_data: The forecast data containing humidity information
        """
        if not forecast_data:
            st.info("No forecast data to display. Please enter a location.")
            return
        
        st.subheader("Humidity Analysis")
        
        # Display humidity indicators
        self._display_humidity_indicators(forecast_data['forecast'])
        
        # Display humidity vs temperature chart
        self._display_humidity_temperature_chart(forecast_data['forecast'])
    
    def _display_humidity_indicators(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display humidity indicators for each forecast day.
        
        Args:
            forecast_days: List of forecast days with humidity data
        """
        # Create columns for each forecast day
        cols = st.columns(len(forecast_days))
        
        for i, day in enumerate(forecast_days):
            with cols[i]:
                st.markdown(f"**{day['date']}**")
                
                # Display humidity value with a visual indicator
                humidity = day['humidity']
                humidity_level = self._get_humidity_level(humidity)
                humidity_color = self._get_humidity_color(humidity)
                
                # Display humidity with color-coded indicator
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{humidity}%</div>
                        <div style="color: {humidity_color}; font-weight: bold;">{humidity_level}</div>
                        <div style="background: linear-gradient(to right, #f0f8ff, {humidity_color}); 
                              height: 10px; width: {humidity}%; margin: auto;"></div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    def _display_humidity_temperature_chart(self, forecast_days: List[Dict[str, Any]]) -> None:
        """
        Display a chart showing humidity in relation to temperature.
        
        Args:
            forecast_days: List of forecast days with humidity and temperature data
        """
        # Create dataframe for the chart
        df = pd.DataFrame({
            'Date': [day['date'] for day in forecast_days],
            'Humidity (%)': [day['humidity'] for day in forecast_days],
            'High Temperature (°C)': [day['temperature_high'] for day in forecast_days],
            'Low Temperature (°C)': [day['temperature_low'] for day in forecast_days]
        })
        
        # Create the humidity line chart with temperature as secondary y-axis
        fig = px.line(df, x='Date', y=['Humidity (%)', 'High Temperature (°C)', 'Low Temperature (°C)'],
                     markers=True, title='Humidity and Temperature Relationship')
        
        # Update layout to show grid lines and improve readability
        fig.update_layout(
            yaxis_title='Humidity (%)',
            xaxis_title='Date',
            legend_title='Measurement',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation about humidity and comfort
        with st.expander("About Humidity and Comfort"):
            st.markdown("""
            ### Humidity and Comfort Levels
            
            Humidity affects how comfortable the weather feels:
            
            - **Low Humidity (0-30%)**: Dry conditions that can cause dry skin, static electricity, and respiratory issues.
            - **Moderate Humidity (30-60%)**: Generally comfortable conditions.
            - **High Humidity (60-80%)**: Can feel muggy and uncomfortable, especially in warm weather.
            - **Very High Humidity (80-100%)**: Feels oppressive, sweat doesn't evaporate easily, making it feel hotter.
            
            The relationship between humidity and temperature is important for understanding the "feels like" temperature.
            """)
    
    def _get_humidity_level(self, humidity: int) -> str:
        """
        Get a descriptive level for the humidity value.
        
        Args:
            humidity: Humidity percentage
            
        Returns:
            String describing the humidity level
        """
        if humidity < 30:
            return "Dry"
        elif humidity < 60:
            return "Moderate"
        elif humidity < 80:
            return "Humid"
        else:
            return "Very Humid"
    
    def _get_humidity_color(self, humidity: int) -> str:
        """
        Get a color representing the humidity level.
        
        Args:
            humidity: Humidity percentage
            
        Returns:
            Hex color code representing the humidity level
        """
        if humidity < 30:
            return "#FFA07A"  # Light salmon (dry)
        elif humidity < 60:
            return "#90EE90"  # Light green (moderate)
        elif humidity < 80:
            return "#87CEFA"  # Light sky blue (humid)
        else:
            return "#6A5ACD"  # Slate blue (very humid)