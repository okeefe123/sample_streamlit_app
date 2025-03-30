from fastapi import FastAPI, Query, HTTPException, Depends
import datetime
import os
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from weather_app.backend.models.weather import CurrentWeather, WeatherForecast, HourlyForecast
from weather_app.backend.services import weather_service
from weather_app.backend.config import settings

# Create the FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="API for weather data retrieval and analysis",
    debug=settings.debug
)

# Version of the application
VERSION = "0.1.0"

# Configure CORS with more explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Create a custom middleware to ensure CORS headers are properly set
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    
    # Get origin from request headers
    origin = request.headers.get("origin")
    
    # If origin is in allowed origins or "*" is in allowed origins, set the appropriate headers
    if origin:
        # Check if this specific origin is allowed or if all origins are allowed
        if origin in settings.cors_origins or "*" in settings.cors_origins:
            response.headers["access-control-allow-origin"] = origin
            response.headers["access-control-allow-credentials"] = "true"
            response.headers["vary"] = "Origin"
            
            # For preflight requests, add additional headers
            if request.method == "OPTIONS":
                response.headers["access-control-allow-methods"] = ", ".join(settings.cors_allow_methods)
                response.headers["access-control-allow-headers"] = ", ".join(settings.cors_allow_headers)
                response.headers["access-control-max-age"] = "600"
    
    return response

# Add OPTIONS method handler for all routes to support preflight requests
@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {}

@app.get("/")
async def root():
    """Root endpoint that provides a welcome message."""
    return {"message": "Welcome to Weather Data API"}

@app.get("/api/health")
async def health():
    """Health check endpoint that returns service status information."""
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "Weather Data API"
    }

@app.get("/api/weather/current", response_model=CurrentWeather)
async def current_weather(location: str = Query(..., description="The location to get weather for")):
    """
    Get current weather for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        CurrentWeather: The current weather data
    """
    try:
        weather_data = await weather_service.get_current_weather(location)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@app.get("/api/weather/forecast", response_model=WeatherForecast)
async def weather_forecast(location: str = Query(..., description="The location to get forecast for")):
    """
    Get weather forecast for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        WeatherForecast: The weather forecast data
    """
    try:
        forecast_data = await weather_service.get_forecast(location)
        return forecast_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast data: {str(e)}")

@app.get("/api/weather/hourly", response_model=HourlyForecast)
async def hourly_forecast(location: str = Query(..., description="The location to get hourly forecast for")):
    """
    Get hourly weather forecast for a specific location.
    
    Args:
        location: The name of the location (city, etc.)
        
    Returns:
        HourlyForecast: The hourly weather forecast data
    """
    try:
        hourly_data = await weather_service.get_hourly_forecast(location)
        return hourly_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly forecast data: {str(e)}")