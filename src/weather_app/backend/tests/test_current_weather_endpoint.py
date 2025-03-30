import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_current_weather_endpoint_returns_weather_data():
    """Test that the current weather endpoint returns formatted weather data."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Mock the weather service to return test data
    mock_weather_data = {
        "location": "New York",
        "temperature": 22.5,
        "humidity": 65,
        "wind_speed": 10.2,
        "wind_direction": "NE",
        "condition": "Partly Cloudy",
        "timestamp": "2025-03-29T12:00:00Z"
    }
    
    # Use patch to mock the get_current_weather function
    with patch("weather_app.backend.services.weather_service.get_current_weather", return_value=mock_weather_data):
        # Test the endpoint with a location parameter
        response = client.get("/api/weather/current?location=New%20York")
        
        # Assert response status code is 200 OK
        assert response.status_code == 200
        
        # Assert the response contains the expected data
        data = response.json()
        assert data["location"] == "New York"
        assert "temperature" in data
        assert "humidity" in data
        assert "wind_speed" in data
        assert "wind_direction" in data
        assert "condition" in data
        assert "timestamp" in data

def test_current_weather_endpoint_requires_location():
    """Test that the current weather endpoint requires a location parameter."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Test the endpoint without a location parameter
    response = client.get("/api/weather/current")
    
    # Assert response status code is 422 Unprocessable Entity (validation error)
    assert response.status_code == 422
    
    # Assert the response contains an error message about the missing parameter
    data = response.json()
    assert "detail" in data
    
    # Check that the error is about the missing location parameter
    # The exact format may vary, but it should mention 'location' somewhere in the error details
    error_details = str(data).lower()
    assert "location" in error_details