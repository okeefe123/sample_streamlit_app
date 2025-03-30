import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_forecast_endpoint_returns_forecast_data():
    """Test that the forecast endpoint returns formatted forecast data."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Mock the weather service to return test data
    mock_forecast_data = {
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
            },
            {
                "date": "2025-03-31",
                "temperature_high": 23.0,
                "temperature_low": 14.0,
                "humidity": 65,
                "wind_speed": 10.0,
                "wind_direction": "N",
                "condition": "Partly Cloudy",
                "precipitation_chance": 30
            },
            {
                "date": "2025-04-01",
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
    
    # Use patch to mock the get_forecast function
    with patch("weather_app.backend.services.weather_service.get_forecast", return_value=mock_forecast_data):
        # Test the endpoint with a location parameter
        response = client.get("/api/weather/forecast?location=New%20York")
        
        # Assert response status code is 200 OK
        assert response.status_code == 200
        
        # Assert the response contains the expected data
        data = response.json()
        assert data["location"] == "New York"
        assert "forecast" in data
        assert len(data["forecast"]) == 3
        
        # Check the first forecast day
        first_day = data["forecast"][0]
        assert "date" in first_day
        assert "temperature_high" in first_day
        assert "temperature_low" in first_day
        assert "humidity" in first_day
        assert "wind_speed" in first_day
        assert "wind_direction" in first_day
        assert "condition" in first_day
        assert "precipitation_chance" in first_day

def test_forecast_endpoint_requires_location():
    """Test that the forecast endpoint requires a location parameter."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Test the endpoint without a location parameter
    response = client.get("/api/weather/forecast")
    
    # Assert response status code is 422 Unprocessable Entity (validation error)
    assert response.status_code == 422
    
    # Assert the response contains an error message about the missing parameter
    data = response.json()
    assert "detail" in data
    
    # Check that the error is about the missing location parameter
    error_details = str(data).lower()
    assert "location" in error_details