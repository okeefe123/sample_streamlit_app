import pytest
from fastapi.testclient import TestClient

def test_health_endpoint():
    """Test that the health endpoint returns the correct response."""
    # Import the app only within the test to avoid circular imports
    from weather_app.backend.api.app import app
    
    # Initialize test client
    client = TestClient(app)
    
    # Test the health endpoint
    response = client.get("/api/health")
    
    # Assert response status code is 200 OK
    assert response.status_code == 200
    
    # Assert the response contains the expected fields
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "service" in data
    assert data["service"] == "Weather Data API"