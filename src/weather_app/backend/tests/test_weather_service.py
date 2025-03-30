"""
Tests for the weather service module.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from weather_app.backend.services.weather_service import (
    get_current_weather,
    get_forecast,
    _get_coordinates_for_location,
    _convert_degrees_to_cardinal,
    _celsius_to_fahrenheit,
    _kmh_to_mph,
    _parse_wind_speed
)

# Test data for mocking API responses
MOCK_POINT_RESPONSE = {
    "properties": {
        "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast",
        "observationStations": "https://api.weather.gov/gridpoints/TOP/31,80/stations"
    }
}

MOCK_STATIONS_RESPONSE = {
    "features": [
        {
            "id": "https://api.weather.gov/stations/KTOP"
        }
    ]
}

MOCK_OBSERVATION_RESPONSE = {
    "properties": {
        "temperature": {
            "value": 22.2,
            "unitCode": "wmoUnit:degC"
        },
        "relativeHumidity": {
            "value": 65
        },
        "windSpeed": {
            "value": 16.5,
            "unitCode": "wmoUnit:km_h-1"
        },
        "windDirection": {
            "value": 45
        },
        "textDescription": "Partly Cloudy",
        "timestamp": "2025-03-29T12:00:00Z"
    }
}

MOCK_FORECAST_RESPONSE = {
    "properties": {
        "periods": [
            {
                "number": 1,
                "name": "Today",
                "startTime": "2025-03-30T08:00:00-05:00",
                "endTime": "2025-03-30T18:00:00-05:00",
                "isDaytime": True,
                "temperature": 25,
                "windSpeed": "10 mph",
                "windDirection": "NW",
                "shortForecast": "Sunny",
                "probabilityOfPrecipitation": {"value": 10},
                "relativeHumidity": {"value": 60}
            },
            {
                "number": 2,
                "name": "Tonight",
                "startTime": "2025-03-30T18:00:00-05:00",
                "endTime": "2025-03-31T06:00:00-05:00",
                "isDaytime": False,
                "temperature": 15,
                "windSpeed": "5 mph",
                "windDirection": "N",
                "shortForecast": "Clear",
                "probabilityOfPrecipitation": {"value": 5},
                "relativeHumidity": {"value": 70}
            },
            {
                "number": 3,
                "name": "Monday",
                "startTime": "2025-03-31T06:00:00-05:00",
                "endTime": "2025-03-31T18:00:00-05:00",
                "isDaytime": True,
                "temperature": 23,
                "windSpeed": "10 mph",
                "windDirection": "N",
                "shortForecast": "Partly Cloudy",
                "probabilityOfPrecipitation": {"value": 30},
                "relativeHumidity": {"value": 65}
            },
            {
                "number": 4,
                "name": "Monday Night",
                "startTime": "2025-03-31T18:00:00-05:00",
                "endTime": "2025-04-01T06:00:00-05:00",
                "isDaytime": False,
                "temperature": 14,
                "windSpeed": "5 mph",
                "windDirection": "NE",
                "shortForecast": "Partly Cloudy",
                "probabilityOfPrecipitation": {"value": 20},
                "relativeHumidity": {"value": 75}
            },
            {
                "number": 5,
                "name": "Tuesday",
                "startTime": "2025-04-01T06:00:00-05:00",
                "endTime": "2025-04-01T18:00:00-05:00",
                "isDaytime": True,
                "temperature": 20,
                "windSpeed": "15 mph",
                "windDirection": "NE",
                "shortForecast": "Rainy",
                "probabilityOfPrecipitation": {"value": 80},
                "relativeHumidity": {"value": 70}
            }
        ]
    }
}

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
        self.text = json.dumps(json_data)
    
    def json(self):
        return self._json_data

class MockAsyncClient:
    async def get(self, url, headers=None):
        if "points" in url:
            return MockResponse(200, MOCK_POINT_RESPONSE)
        elif "stations" in url:
            return MockResponse(200, MOCK_STATIONS_RESPONSE)
        elif "observations" in url:
            return MockResponse(200, MOCK_OBSERVATION_RESPONSE)
        elif "forecast" in url:
            return MockResponse(200, MOCK_FORECAST_RESPONSE)
        return MockResponse(404, {"error": "Not found"})
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_get_current_weather():
    """Test getting current weather data."""
    with patch("httpx.AsyncClient", return_value=MockAsyncClient()):
        # Test with a known city
        weather_data = await get_current_weather("New York")
        
        assert weather_data["location"] == "New York"
        assert isinstance(weather_data["temperature"], float)
        assert isinstance(weather_data["humidity"], int)
        assert isinstance(weather_data["wind_speed"], float)
        assert isinstance(weather_data["wind_direction"], str)
        assert isinstance(weather_data["condition"], str)
        assert isinstance(weather_data["timestamp"], str)

@pytest.mark.asyncio
async def test_get_forecast():
    """Test getting forecast data."""
    with patch("httpx.AsyncClient", return_value=MockAsyncClient()):
        # Test with a known city
        forecast_data = await get_forecast("New York")
        
        assert forecast_data["location"] == "New York"
        assert "forecast" in forecast_data
        assert len(forecast_data["forecast"]) > 0
        
        # Check the first forecast day
        first_day = forecast_data["forecast"][0]
        assert "date" in first_day
        assert "temperature_high" in first_day
        assert "temperature_low" in first_day
        assert "humidity" in first_day
        assert "wind_speed" in first_day
        assert "wind_direction" in first_day
        assert "condition" in first_day
        assert "precipitation_chance" in first_day

def test_get_coordinates_for_location():
    """Test getting coordinates for a location."""
    # Test with a known city
    coordinates = _get_coordinates_for_location("New York")
    assert coordinates is not None
    assert len(coordinates) == 2
    assert isinstance(coordinates[0], float)  # latitude
    assert isinstance(coordinates[1], float)  # longitude
    
    # Test with an unknown city
    coordinates = _get_coordinates_for_location("Unknown City")
    assert coordinates is None

def test_convert_degrees_to_cardinal():
    """Test converting degrees to cardinal direction."""
    assert _convert_degrees_to_cardinal(0) == "N"
    assert _convert_degrees_to_cardinal(45) == "NE"
    assert _convert_degrees_to_cardinal(90) == "E"
    assert _convert_degrees_to_cardinal(135) == "SE"
    assert _convert_degrees_to_cardinal(180) == "S"
    assert _convert_degrees_to_cardinal(225) == "SW"
    assert _convert_degrees_to_cardinal(270) == "W"
    assert _convert_degrees_to_cardinal(315) == "NW"
    assert _convert_degrees_to_cardinal(360) == "N"
    assert _convert_degrees_to_cardinal(None) == "N/A"

def test_celsius_to_fahrenheit():
    """Test converting Celsius to Fahrenheit."""
    assert _celsius_to_fahrenheit(0) == 32.0
    assert _celsius_to_fahrenheit(100) == 212.0
    assert _celsius_to_fahrenheit(-40) == -40.0
    assert _celsius_to_fahrenheit(None) == 0

def test_kmh_to_mph():
    """Test converting km/h to mph."""
    assert _kmh_to_mph(0) == 0.0
    assert round(_kmh_to_mph(100), 2) == 62.14
    assert _kmh_to_mph(None) == 0

def test_parse_wind_speed():
    """Test parsing wind speed from string."""
    assert _parse_wind_speed("10 mph") == 10.0
    assert _parse_wind_speed("15 to 20 mph") == 20.0
    assert _parse_wind_speed("Variable 5 to 10 kt") == 10.0
    assert _parse_wind_speed("Invalid") == 0.0