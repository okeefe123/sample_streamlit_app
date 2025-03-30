import pytest
from fastapi.testclient import TestClient

def test_app_initialization():
    """Test that the FastAPI application can be initialized."""
    # Import the app only within the test to avoid circular imports
    from backend.api.app import app
    
    # Check that app is a FastAPI instance
    assert app is not None
    assert app.title == "Weather Data API"
    
    # Initialize test client
    client = TestClient(app)
    
    # Basic verification that the application is working
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Weather Data API" in response.json()["message"]