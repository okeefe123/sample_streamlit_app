import streamlit as st
import asyncio
from weather_app.frontend.components.location_form import LocationForm
from weather_app.frontend.components.current_weather_display import CurrentWeatherDisplay
from weather_app.frontend.components.forecast_display import ForecastDisplay
from weather_app.frontend.components.wind_display import WindDisplay
from weather_app.frontend.components.humidity_display import HumidityDisplay
from weather_app.frontend.components.hourly_forecast import HourlyForecast
from weather_app.frontend.services.api_service import ApiService

def main():
    """Main function for the Streamlit application."""
    # Set up page configuration
    st.set_page_config(
        page_title="Weather Data App",
        page_icon="🌤️",
        layout="wide"
    )
    
    # Set up page title and description
    st.title("Weather Data Analysis Application")
    st.markdown("""
    This application provides weather data and forecasts for locations around the world.
    Enter a location below to get started.
    """)
    
    # Initialize components
    location_form = LocationForm()
    current_weather_display = CurrentWeatherDisplay()
    forecast_display = ForecastDisplay()
    wind_display = WindDisplay()
    humidity_display = HumidityDisplay()
    hourly_forecast = HourlyForecast()
    api_service = ApiService()
    
    # Initialize session state for storing weather data
    if "current_weather" not in st.session_state:
        st.session_state.current_weather = None
    if "forecast" not in st.session_state:
        st.session_state.forecast = None
    if "hourly_forecast" not in st.session_state:
        st.session_state.hourly_forecast = None
    
    # Render the location form
    location = location_form.render()
    
    # If a location was submitted, fetch weather data
    if location:
        with st.spinner(f"Fetching weather data for {location}..."):
            # Use asyncio to run async API calls
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Fetch current weather and forecast concurrently
            current_weather_task = loop.create_task(api_service.get_current_weather(location))
            forecast_task = loop.create_task(api_service.get_forecast(location))
            hourly_task = loop.create_task(api_service.get_hourly_forecast(location))
            
            # Wait for all tasks to complete
            loop.run_until_complete(asyncio.gather(current_weather_task, forecast_task, hourly_task))
            
            # Get results
            st.session_state.current_weather = current_weather_task.result()
            st.session_state.forecast = forecast_task.result()
            st.session_state.hourly_forecast = hourly_task.result()
            
            # Close the event loop
            loop.close()
    
    # Display a separator
    st.markdown("---")
    
    # Create tabs for different views
    current_tab, forecast_tab, hourly_tab, wind_tab, humidity_tab = st.tabs([
        "Current Weather", 
        "Daily Forecast", 
        "Hourly Forecast",
        "Wind Analysis",
        "Humidity Analysis"
    ])
    
    # Display current weather in the first tab
    with current_tab:
        current_weather_display.render(st.session_state.current_weather)
    
    # Display forecast in the second tab
    with forecast_tab:
        forecast_display.render(st.session_state.forecast)
    
    # Display hourly forecast in the third tab
    with hourly_tab:
        hourly_forecast.render(st.session_state.hourly_forecast)
    
    # Display wind data in the fourth tab
    with wind_tab:
        wind_display.render(st.session_state.forecast)
    
    # Display humidity data in the fifth tab
    with humidity_tab:
        humidity_display.render(st.session_state.forecast)
    
    # Add footer
    st.markdown("---")
    st.markdown("Weather Data Analysis Application | Created with Streamlit and FastAPI")

if __name__ == "__main__":
    main()