"""
Weather Data Models

This module defines the data models for weather information.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CurrentWeather(BaseModel):
    """Model for current weather data."""
    location: str
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0)
    wind_direction: str
    condition: str
    timestamp: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": "New York",
                "temperature": 22.5,
                "humidity": 65,
                "wind_speed": 10.2,
                "wind_direction": "NE",
                "condition": "Partly Cloudy",
                "timestamp": "2025-03-29T12:00:00Z"
            }
        }
    )

class ForecastDay(BaseModel):
    """Model for a single day's forecast."""
    date: str
    temperature_high: float
    temperature_low: float
    humidity: int = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0)
    wind_direction: str
    condition: str
    precipitation_chance: int = Field(..., ge=0, le=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-03-30",
                "temperature_high": 25.0,
                "temperature_low": 15.0,
                "humidity": 60,
                "wind_speed": 12.5,
                "wind_direction": "NW",
                "condition": "Sunny",
                "precipitation_chance": 10
            }
        }
    )

class WeatherForecast(BaseModel):
    """Model for weather forecast data."""
    location: str
    forecast: List[ForecastDay]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": "New York",
                "forecast": [
                    {
                        "date": "2025-03-30",
                        "temperature_high": 25.0,
                        "temperature_low": 15.0,
                        "humidity": 60,
                        "wind_speed": 12.5,
                        "wind_direction": "NW",
                        "condition": "Sunny",
                        "precipitation_chance": 10
                    }
                ]
            }
        }
    )

class HourlyForecastPeriod(BaseModel):
    """Model for a single hour's forecast."""
    time: str
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0)
    wind_direction: str
    condition: str
    precipitation_chance: int = Field(..., ge=0, le=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "time": "2025-03-29T12:00:00Z",
                "temperature": 22.5,
                "humidity": 65,
                "wind_speed": 10.2,
                "wind_direction": "NE",
                "condition": "Partly Cloudy",
                "precipitation_chance": 20
            }
        }
    )

class HourlyForecast(BaseModel):
    """Model for hourly weather forecast data."""
    location: str
    forecast: List[HourlyForecastPeriod]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": "New York",
                "forecast": [
                    {
                        "time": "2025-03-29T12:00:00Z",
                        "temperature": 22.5,
                        "humidity": 65,
                        "wind_speed": 10.2,
                        "wind_direction": "NE",
                        "condition": "Partly Cloudy",
                        "precipitation_chance": 20
                    }
                ]
            }
        }
    )