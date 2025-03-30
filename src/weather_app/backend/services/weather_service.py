"""
Weather Service Module

This module handles interactions with external weather API services
and provides functions to retrieve weather data.
"""
import os
import json
import time
import logging
from datetime import datetime, timedelta
import httpx
from typing import Dict, Any, Optional, List, Tuple

from weather_app.backend.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache for weather data
_weather_cache = {}
# Cache timeout in seconds (5 minutes)
CACHE_TIMEOUT = 300

# NWS API base URL
NWS_API_BASE_URL = "https://api.weather.gov"

# Simple mapping of common city names to their coordinates (lat, lon)
# In a production app, this would be replaced with a proper geocoding service
CITY_COORDINATES = {
    "new york": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "houston": (29.7604, -95.3698),
    "phoenix": (33.4484, -112.0740),
    "philadelphia": (39.9526, -75.1652),
    "san antonio": (29.4241, -98.4936),
    "san diego": (32.7157, -117.1611),
    "dallas": (32.7767, -96.7970),
    "san jose": (37.3382, -121.8863),
    "austin": (30.2672, -97.7431),
    "jacksonville": (30.3322, -81.6557),
    "san francisco": (37.7749, -122.4194),
    "columbus": (39.9612, -82.9988),
    "indianapolis": (39.7684, -86.1581),
    "seattle": (47.6062, -122.3321),
    "denver": (39.7392, -104.9903),
    "washington": (38.9072, -77.0369),
    "boston": (42.3601, -71.0589),
    "nashville": (36.1627, -86.7816),
    "portland": (45.5051, -122.6750),
    "las vegas": (36.1699, -115.1398),
    "detroit": (42.3314, -83.0458),
    "miami": (25.7617, -80.1918),
    "atlanta": (33.7490, -84.3880),
}

async def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather data for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing weather data
    """
    # Check if we have cached data for this location
    cache_key = f"current_{location.lower()}"
    cached_data = _get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    # If no cached data, fetch from API
    weather_data = await _fetch_current_weather_from_api(location)
    
    # Cache the result
    _add_to_cache(cache_key, weather_data)
    
    return weather_data

async def get_forecast(location: str) -> Dict[str, Any]:
    """
    Get weather forecast data for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing forecast data
    """
    # Check if we have cached data for this location
    cache_key = f"forecast_{location.lower()}"
    cached_data = _get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    # If no cached data, fetch from API
    forecast_data = await _fetch_forecast_from_api(location)
    
    # Cache the result
    _add_to_cache(cache_key, forecast_data)
    
    return forecast_data

async def get_hourly_forecast(location: str) -> Dict[str, Any]:
    """
    Get hourly weather forecast data for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing hourly forecast data
    """
    # Check if we have cached data for this location
    cache_key = f"hourly_{location.lower()}"
    cached_data = _get_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    # If no cached data, fetch from API
    hourly_data = await _fetch_hourly_forecast_from_api(location)
    
    # Cache the result
    _add_to_cache(cache_key, hourly_data)
    
    return hourly_data

async def _fetch_current_weather_from_api(location: str) -> Dict[str, Any]:
    """
    Fetch current weather data from the NWS API.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing weather data
    """
    try:
        # Get coordinates for the location
        coordinates = _get_coordinates_for_location(location)
        if not coordinates:
            logger.warning(f"Could not find coordinates for location: {location}")
            return _generate_mock_current_weather(location)
        
        lat, lon = coordinates
        
        # Get point metadata from NWS API
        async with httpx.AsyncClient() as client:
            # Set user agent header as required by NWS API
            headers = {
                "User-Agent": f"WeatherApp/{settings.app_name} (contact@example.com)",
                "Accept": "application/geo+json"
            }
            
            # Get point metadata
            point_url = f"{NWS_API_BASE_URL}/points/{lat},{lon}"
            point_response = await client.get(point_url, headers=headers)
            
            if point_response.status_code != 200:
                logger.error(f"Error getting point data: {point_response.text}")
                return _generate_mock_current_weather(location)
            
            point_data = point_response.json()
            
            # Get the nearest observation station
            stations_url = point_data["properties"]["observationStations"]
            stations_response = await client.get(stations_url, headers=headers)
            
            if stations_response.status_code != 200:
                logger.error(f"Error getting stations: {stations_response.text}")
                return _generate_mock_current_weather(location)
            
            stations_data = stations_response.json()
            
            if not stations_data["features"]:
                logger.warning(f"No observation stations found for location: {location}")
                return _generate_mock_current_weather(location)
            
            # Get the first (nearest) station
            station_url = stations_data["features"][0]["id"]
            
            # Get the latest observation from this station
            observation_url = f"{station_url}/observations/latest"
            observation_response = await client.get(observation_url, headers=headers)
            
            if observation_response.status_code != 200:
                logger.error(f"Error getting observation: {observation_response.text}")
                return _generate_mock_current_weather(location)
            
            observation_data = observation_response.json()
            
            # Extract and format the weather data
            properties = observation_data["properties"]
            
            # Map wind direction value to cardinal direction
            wind_direction_value = properties.get("windDirection", {}).get("value")
            wind_direction = _convert_degrees_to_cardinal(wind_direction_value) if wind_direction_value else "N/A"
            
            # Determine weather condition
            weather_condition = "Clear"
            if properties.get("textDescription"):
                weather_condition = properties["textDescription"]
            
            # Format the data according to our model
            weather_data = {
                "location": location,
                "temperature": properties.get("temperature", {}).get("value", 0),
                "humidity": int(properties.get("relativeHumidity", {}).get("value", 0)),
                "wind_speed": properties.get("windSpeed", {}).get("value", 0),
                "wind_direction": wind_direction,
                "condition": weather_condition,
                "timestamp": properties.get("timestamp", datetime.now().isoformat())
            }
            
            # Convert temperature from C to F if needed
            if properties.get("temperature", {}).get("unitCode") == "wmoUnit:degC":
                weather_data["temperature"] = _celsius_to_fahrenheit(weather_data["temperature"])
            
            # Convert wind speed from km/h to mph if needed
            if properties.get("windSpeed", {}).get("unitCode") in ["wmoUnit:km_h-1", "wmoUnit:km h-1"]:
                weather_data["wind_speed"] = _kmh_to_mph(weather_data["wind_speed"])
            
            # Ensure humidity is within 0-100 range
            weather_data["humidity"] = max(0, min(100, weather_data["humidity"]))
            
            return weather_data
            
    except Exception as e:
        logger.exception(f"Error fetching current weather data: {str(e)}")
    
    # Fall back to mock data if anything fails
    return _generate_mock_current_weather(location)

async def _fetch_forecast_from_api(location: str) -> Dict[str, Any]:
    """
    Fetch weather forecast data from the NWS API.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing forecast data
    """
    try:
        # Get coordinates for the location
        coordinates = _get_coordinates_for_location(location)
        if not coordinates:
            logger.warning(f"Could not find coordinates for location: {location}")
            return _generate_mock_forecast(location)
        
        lat, lon = coordinates
        
        # Get point metadata from NWS API
        async with httpx.AsyncClient() as client:
            # Set user agent header as required by NWS API
            headers = {
                "User-Agent": f"WeatherApp/{settings.app_name} (contact@example.com)",
                "Accept": "application/geo+json"
            }
            
            # Get point metadata
            point_url = f"{NWS_API_BASE_URL}/points/{lat},{lon}"
            point_response = await client.get(point_url, headers=headers)
            
            if point_response.status_code != 200:
                logger.error(f"Error getting point data: {point_response.text}")
                return _generate_mock_forecast(location)
            
            point_data = point_response.json()
            
            # Get the forecast URL from the point data
            forecast_url = point_data["properties"]["forecast"]
            forecast_response = await client.get(forecast_url, headers=headers)
            
            if forecast_response.status_code != 200:
                logger.error(f"Error getting forecast: {forecast_response.text}")
                return _generate_mock_forecast(location)
            
            forecast_data = forecast_response.json()
            
            # Extract and format the forecast data
            periods = forecast_data["properties"]["periods"]
            
            # Group periods by day (NWS provides day/night periods)
            days = {}
            for period in periods:
                # Extract date from the start time
                start_time = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
                date_str = start_time.strftime("%Y-%m-%d")
                
                if date_str not in days:
                    days[date_str] = {"day": None, "night": None}
                
                # Determine if this is a day or night period
                if period["isDaytime"]:
                    days[date_str]["day"] = period
                else:
                    days[date_str]["night"] = period
            
            # Format the forecast data according to our model
            forecast_days = []
            for date_str, periods in days.items():
                day_period = periods["day"]
                night_period = periods["night"]
                
                if not day_period:
                    continue  # Skip days without day data
                
                # Calculate high and low temperatures
                temp_high = day_period["temperature"]
                temp_low = night_period["temperature"] if night_period else temp_high - 10  # Estimate if no night data
                
                # Extract wind data from day period
                wind_speed_str = day_period["windSpeed"]
                wind_speed = _parse_wind_speed(wind_speed_str)
                wind_direction = day_period["windDirection"]
                
                # Determine precipitation chance
                precip_chance = 0
                if "probabilityOfPrecipitation" in day_period and day_period["probabilityOfPrecipitation"].get("value") is not None:
                    precip_chance = day_period["probabilityOfPrecipitation"]["value"]
                elif night_period and "probabilityOfPrecipitation" in night_period and night_period["probabilityOfPrecipitation"].get("value") is not None:
                    precip_chance = night_period["probabilityOfPrecipitation"]["value"]
                
                # Determine humidity
                humidity = 50  # Default value
                if "relativeHumidity" in day_period and day_period["relativeHumidity"].get("value") is not None:
                    humidity = day_period["relativeHumidity"]["value"]
                
                # Format the day's forecast
                forecast_day = {
                    "date": date_str,
                    "temperature_high": temp_high,
                    "temperature_low": temp_low,
                    "humidity": int(humidity),
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction,
                    "condition": day_period["shortForecast"],
                    "precipitation_chance": int(precip_chance)
                }
                
                forecast_days.append(forecast_day)
            
            # Limit to 3 days to match the expected format
            forecast_days = forecast_days[:3]
            
            return {
                "location": location,
                "forecast": forecast_days
            }
            
    except Exception as e:
        logger.exception(f"Error fetching forecast data: {str(e)}")
    
    # Fall back to mock data if anything fails
    return _generate_mock_forecast(location)

async def _fetch_hourly_forecast_from_api(location: str) -> Dict[str, Any]:
    """
    Fetch hourly weather forecast data from the NWS API.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Dict containing hourly forecast data
    """
    try:
        # Get coordinates for the location
        coordinates = _get_coordinates_for_location(location)
        if not coordinates:
            logger.warning(f"Could not find coordinates for location: {location}")
            return _generate_mock_hourly_forecast(location)
        
        lat, lon = coordinates
        
        # Get point metadata from NWS API
        async with httpx.AsyncClient() as client:
            # Set user agent header as required by NWS API
            headers = {
                "User-Agent": f"WeatherApp/{settings.app_name} (contact@example.com)",
                "Accept": "application/geo+json"
            }
            
            # Get point metadata
            point_url = f"{NWS_API_BASE_URL}/points/{lat},{lon}"
            point_response = await client.get(point_url, headers=headers)
            
            if point_response.status_code != 200:
                logger.error(f"Error getting point data: {point_response.text}")
                return _generate_mock_hourly_forecast(location)
            
            point_data = point_response.json()
            
            # Get the hourly forecast URL from the point data
            hourly_forecast_url = point_data["properties"]["forecastHourly"]
            hourly_forecast_response = await client.get(hourly_forecast_url, headers=headers)
            
            if hourly_forecast_response.status_code != 200:
                logger.error(f"Error getting hourly forecast: {hourly_forecast_response.text}")
                return _generate_mock_hourly_forecast(location)
            
            hourly_forecast_data = hourly_forecast_response.json()
            
            # Extract and format the hourly forecast data
            periods = hourly_forecast_data["properties"]["periods"]
            
            # Format the hourly forecast data according to our model
            hourly_periods = []
            for period in periods[:24]:  # Limit to 24 hours
                # Extract time from the start time
                start_time = datetime.fromisoformat(period["startTime"].replace("Z", "+00:00"))
                
                # Extract wind data
                wind_speed_str = period["windSpeed"]
                wind_speed = _parse_wind_speed(wind_speed_str)
                wind_direction = period["windDirection"]
                
                # Determine precipitation chance
                precip_chance = 0
                if "probabilityOfPrecipitation" in period and period["probabilityOfPrecipitation"].get("value") is not None:
                    precip_chance = period["probabilityOfPrecipitation"]["value"]
                
                # Determine humidity
                humidity = 50  # Default value
                if "relativeHumidity" in period and period["relativeHumidity"].get("value") is not None:
                    humidity = period["relativeHumidity"]["value"]
                
                # Format the hour's forecast
                hourly_period = {
                    "time": period["startTime"],
                    "temperature": period["temperature"],
                    "humidity": int(humidity),
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction,
                    "condition": period["shortForecast"],
                    "precipitation_chance": int(precip_chance)
                }
                
                hourly_periods.append(hourly_period)
            
            return {
                "location": location,
                "forecast": hourly_periods
            }
            
    except Exception as e:
        logger.exception(f"Error fetching hourly forecast data: {str(e)}")
    
    # Fall back to mock data if anything fails
    return _generate_mock_hourly_forecast(location)

def _get_coordinates_for_location(location: str) -> Optional[Tuple[float, float]]:
    """
    Get latitude and longitude coordinates for a location name.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Convert to lowercase for case-insensitive matching
    location_lower = location.lower()
    
    # Check if we have coordinates for this location
    if location_lower in CITY_COORDINATES:
        return CITY_COORDINATES[location_lower]
    
    # In a real implementation, we would use a geocoding service here
    # For now, return None if the location is not in our dictionary
    return None

def _convert_degrees_to_cardinal(degrees: float) -> str:
    """
    Convert wind direction in degrees to cardinal direction.
    
    Args:
        degrees: Wind direction in degrees
        
    Returns:
        Cardinal direction (N, NE, E, etc.)
    """
    if degrees is None:
        return "N/A"
    
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    
    index = round(degrees / 22.5) % 16
    return directions[index]

def _celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert temperature from Celsius to Fahrenheit.
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    if celsius is None:
        return 0
    return (celsius * 9/5) + 32

def _kmh_to_mph(kmh: float) -> float:
    """
    Convert wind speed from km/h to mph.
    
    Args:
        kmh: Wind speed in kilometers per hour
        
    Returns:
        Wind speed in miles per hour
    """
    if kmh is None:
        return 0
    return kmh * 0.621371

def _parse_wind_speed(wind_speed_str: str) -> float:
    """
    Parse wind speed from a string like "10 mph" or "15 to 20 mph".
    
    Args:
        wind_speed_str: Wind speed as a string
        
    Returns:
        Wind speed as a float in mph
    """
    try:
        # Handle ranges like "15 to 20 mph"
        if " to " in wind_speed_str:
            parts = wind_speed_str.split(" to ")
            high_speed = parts[1].split(" ")[0]
            return float(high_speed)
        
        # Handle simple values like "10 mph"
        return float(wind_speed_str.split(" ")[0])
    except (ValueError, IndexError):
        return 0.0

def _generate_mock_current_weather(location: str) -> Dict[str, Any]:
    """
    Generate mock current weather data for a location.
    
    Args:
        location: The name of the location
        
    Returns:
        Dict containing mock weather data
    """
    return {
        "location": location,
        "temperature": 22.5,
        "humidity": 65,
        "wind_speed": 10.2,
        "wind_direction": "NE",
        "condition": "Partly Cloudy",
        "timestamp": datetime.now().isoformat()
    }

def _generate_mock_forecast(location: str) -> Dict[str, Any]:
    """
    Generate mock forecast data for a location.
    
    Args:
        location: The name of the location
        
    Returns:
        Dict containing mock forecast data
    """
    # Generate dates for the next 3 days
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]
    
    return {
        "location": location,
        "forecast": [
            {
                "date": dates[0],
                "temperature_high": 25.0,
                "temperature_low": 15.0,
                "humidity": 60,
                "wind_speed": 12.5,
                "wind_direction": "NW",
                "condition": "Sunny",
                "precipitation_chance": 10
            },
            {
                "date": dates[1],
                "temperature_high": 23.0,
                "temperature_low": 14.0,
                "humidity": 65,
                "wind_speed": 10.0,
                "wind_direction": "N",
                "condition": "Partly Cloudy",
                "precipitation_chance": 30
            },
            {
                "date": dates[2],
                "temperature_high": 20.0,
                "temperature_low": 12.0,
                "humidity": 70,
                "wind_speed": 15.0,
                "wind_direction": "NE",
                "condition": "Rainy",
                "precipitation_chance": 80
            }
        ]
    }

def _generate_mock_hourly_forecast(location: str) -> Dict[str, Any]:
    """
    Generate mock hourly forecast data for a location.
    
    Args:
        location: The name of the location
        
    Returns:
        Dict containing mock hourly forecast data
    """
    # Generate times for the next 24 hours
    now = datetime.now()
    hourly_forecast = []
    
    for i in range(24):
        hour_time = now + timedelta(hours=i)
        
        # Vary temperature throughout the day
        hour = hour_time.hour
        base_temp = 20.0  # Base temperature
        
        # Temperature peaks in the afternoon (around 2-3 PM)
        if 6 <= hour <= 14:
            temp_adjustment = (hour - 6) * 0.8  # Increasing temperature
        else:
            temp_adjustment = max(0, 14 - abs(hour - 14)) * 0.8  # Decreasing temperature
        
        temperature = base_temp + temp_adjustment
        
        # Vary conditions based on time
        if 6 <= hour <= 18:  # Daytime
            condition = "Sunny" if i % 4 != 0 else "Partly Cloudy"
            precip_chance = 10 if i % 4 != 0 else 20
        else:  # Nighttime
            condition = "Clear" if i % 4 != 0 else "Partly Cloudy"
            precip_chance = 5 if i % 4 != 0 else 15
        
        hourly_forecast.append({
            "time": hour_time.isoformat(),
            "temperature": round(temperature, 1),
            "humidity": 60 + (i % 10),
            "wind_speed": 8.0 + (i % 5),
            "wind_direction": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][i % 8],
            "condition": condition,
            "precipitation_chance": precip_chance
        })
    
    return {
        "location": location,
        "forecast": hourly_forecast
    }

def _get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    """
    Get data from the cache if it exists and is not expired.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None if not found or expired
    """
    if key in _weather_cache:
        cached_item = _weather_cache[key]
        if time.time() - cached_item["timestamp"] < CACHE_TIMEOUT:
            return cached_item["data"]
    return None

def _add_to_cache(key: str, data: Dict[str, Any]) -> None:
    """
    Add data to the cache.
    
    Args:
        key: Cache key
        data: Data to cache
    """
    _weather_cache[key] = {
        "timestamp": time.time(),
        "data": data
    }