import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_hourly_forecast_endpoint_returns_forecast_data():
    """Test that the hourly forecast endpoint returns formatted forecast data."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Mock the weather service to return test data
    mock_hourly_data = {
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
            },
            {
                "time": "2025-03-29T13:00:00Z",
                "temperature": 23.0,
                "humidity": 63,
                "wind_speed": 10.5,
                "wind_direction": "NE",
                "condition": "Partly Cloudy",
                "precipitation_chance": 15
            },
            {
                "time": "2025-03-29T14:00:00Z",
                "temperature": 23.5,
                "humidity": 60,
                "wind_speed": 11.0,
                "wind_direction": "E",
                "condition": "Sunny",
                "precipitation_chance": 10
            }
        ]
    }
    
    # Use patch to mock the get_hourly_forecast function
    with patch("weather_app.backend.services.weather_service.get_hourly_forecast", return_value=mock_hourly_data):
        # Test the endpoint with a location parameter
        response = client.get("/api/weather/hourly?location=New%20York")
        
        # Assert response status code is 200 OK
        assert response.status_code == 200
        
        # Assert the response contains the expected data
        data = response.json()
        assert data["location"] == "New York"
        assert "forecast" in data
        assert len(data["forecast"]) == 3
        
        # Check the first forecast hour
        first_hour = data["forecast"][0]
        assert "time" in first_hour
        assert "temperature" in first_hour
        assert "humidity" in first_hour
        assert "wind_speed" in first_hour
        assert "wind_direction" in first_hour
        assert "condition" in first_hour
        assert "precipitation_chance" in first_hour

def test_hourly_forecast_endpoint_requires_location():
    """Test that the hourly forecast endpoint requires a location parameter."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Test the endpoint without a location parameter
    response = client.get("/api/weather/hourly")
    
    # Assert response status code is 422 Unprocessable Entity (validation error)
    assert response.status_code == 422
    
    # Assert the response contains an error message about the missing parameter
    data = response.json()
    assert "detail" in data
    
    # Check that the error is about the missing location parameter
    error_details = str(data).lower()
    assert "location" in error_details