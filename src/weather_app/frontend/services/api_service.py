"""
API Service

This module handles communication with the backend API.
"""
import httpx
from typing import Dict, Any, Optional
import streamlit as st
import json
import time

# Default API base URL (assuming backend is running on localhost:8001)
DEFAULT_API_BASE_URL = "http://localhost:8001"

# Cache timeout in seconds (5 minutes)
CACHE_TIMEOUT = 300

class ApiService:
    """
    Service for making API calls to the backend.
    """
    
    def __init__(self, base_url: str = DEFAULT_API_BASE_URL):
        """
        Initialize the API service.
        
        Args:
            base_url: The base URL for the API
        """
        self.base_url = base_url
        # Initialize cache if not already present
        if "api_cache" not in st.session_state:
            st.session_state.api_cache = {}
    
    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather data for a location.
        
        Args:
            location: The location to get weather for
            
        Returns:
            Dict containing weather data or None if an error occurred
        """
        # Check cache first
        cache_key = f"current_{location.lower()}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Make API call
        endpoint = f"{self.base_url}/api/weather/current"
        params = {"location": location}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Cache the result
                self._add_to_cache(cache_key, data)
                
                return data
        except Exception as e:
            st.error(f"Error fetching current weather: {str(e)}")
            return None
    
    async def get_forecast(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a location.
        
        Args:
            location: The location to get forecast for
            
        Returns:
            Dict containing forecast data or None if an error occurred
        """
        # Check cache first
        cache_key = f"forecast_{location.lower()}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Make API call
        endpoint = f"{self.base_url}/api/weather/forecast"
        params = {"location": location}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Cache the result
                self._add_to_cache(cache_key, data)
                
                return data
        except Exception as e:
            st.error(f"Error fetching weather forecast: {str(e)}")
            return None
    
    async def get_hourly_forecast(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get hourly weather forecast for a location.
        
        Args:
            location: The location to get hourly forecast for
            
        Returns:
            Dict containing hourly forecast data or None if an error occurred
        """
        # Check cache first
        cache_key = f"hourly_{location.lower()}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Make API call
        endpoint = f"{self.base_url}/api/weather/hourly"
        params = {"location": location}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Cache the result
                self._add_to_cache(cache_key, data)
                
                return data
        except Exception as e:
            st.error(f"Error fetching hourly forecast: {str(e)}")
            # For now, generate mock data for demonstration purposes
            # This would be removed once the backend endpoint is implemented
            return self._generate_mock_hourly_data(location)
    
    def _generate_mock_hourly_data(self, location: str) -> Dict[str, Any]:
        """
        Generate mock hourly forecast data for demonstration purposes.
        
        Args:
            location: The location to generate data for
            
        Returns:
            Dict containing mock hourly forecast data
        """
        import random
        from datetime import datetime, timedelta
        
        # Base temperature and conditions
        base_temp = random.randint(15, 25)
        conditions = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Sunny"]
        
        # Generate hourly data for 24 hours
        hourly_data = []
        now = datetime.now()
        
        for i in range(24):
            hour_time = now + timedelta(hours=i)
            time_str = hour_time.strftime("%H:%M")
            
            # Temperature varies throughout the day
            hour_factor = i % 24
            if 6 <= hour_factor < 12:  # Morning - rising
                temp_adjustment = (hour_factor - 6) * 1.5
            elif 12 <= hour_factor < 18:  # Afternoon - high
                temp_adjustment = 9 - (hour_factor - 12) * 0.5
            else:  # Evening/night - low
                temp_adjustment = -3
            
            temperature = round(base_temp + temp_adjustment)
            
            # Other weather parameters
            condition = random.choice(conditions)
            precip_chance = random.randint(0, 100) if "Rain" in condition else random.randint(0, 30)
            humidity = random.randint(40, 90)
            wind_speed = random.randint(5, 20)
            wind_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            wind_direction = random.choice(wind_directions)
            
            hourly_data.append({
                "time": time_str,
                "temperature": temperature,
                "condition": condition,
                "precipitation_chance": precip_chance,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "wind_direction": wind_direction
            })
        
        return {
            "location": location,
            "hourly_forecast": hourly_data
        }
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from the cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found or expired
        """
        if key in st.session_state.api_cache:
            cached_item = st.session_state.api_cache[key]
            if time.time() - cached_item["timestamp"] < CACHE_TIMEOUT:
                return cached_item["data"]
        return None
    
    def _add_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """
        Add data to the cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        st.session_state.api_cache[key] = {
            "timestamp": time.time(),
            "data": data
        }