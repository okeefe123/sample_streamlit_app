import os
import pytest
import subprocess
import time
import requests


@pytest.fixture(scope="module")
def docker_compose_services():
    """Start the services using docker-compose."""
    # Start the services
    subprocess.run(
        ["docker-compose", "up", "-d"],
        capture_output=True,
        text=True
    )
    
    # Wait for services to start
    time.sleep(10)
    
    yield
    
    # Stop the services
    subprocess.run(
        ["docker-compose", "down"],
        capture_output=True,
        text=True
    )


def test_frontend_can_call_backend_health_endpoint(docker_compose_services):
    """Test that the frontend container can call the backend health endpoint."""
    # Execute a command in the frontend container to make a request to the backend
    result = subprocess.run(
        [
            "docker-compose", "exec", "frontend",
            "python", "-c", 
            "import requests; response = requests.get('http://backend:8000/api/health'); print(response.status_code); print(response.text)"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the command was successful
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check that the response status code is 200
    assert "200" in result.stdout, f"Expected status code 200, got: {result.stdout}"
    
    # Check that the response contains the expected data
    assert "status" in result.stdout, f"Expected 'status' in response, got: {result.stdout}"


def test_frontend_can_call_backend_current_weather_endpoint(docker_compose_services):
    """Test that the frontend container can call the backend current weather endpoint."""
    # Execute a command in the frontend container to make a request to the backend
    result = subprocess.run(
        [
            "docker-compose", "exec", "frontend",
            "python", "-c", 
            "import requests; response = requests.get('http://backend:8000/api/weather/current?location=London'); print(response.status_code); print(response.text)"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the command was successful
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check that the response status code is 200 or 400 (if API key is not set)
    assert any(code in result.stdout for code in ["200", "400"]), f"Expected status code 200 or 400, got: {result.stdout}"


def test_frontend_can_call_backend_forecast_endpoint(docker_compose_services):
    """Test that the frontend container can call the backend forecast endpoint."""
    # Execute a command in the frontend container to make a request to the backend
    result = subprocess.run(
        [
            "docker-compose", "exec", "frontend",
            "python", "-c", 
            "import requests; response = requests.get('http://backend:8000/api/weather/forecast?location=London'); print(response.status_code); print(response.text)"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the command was successful
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check that the response status code is 200 or 400 (if API key is not set)
    assert any(code in result.stdout for code in ["200", "400"]), f"Expected status code 200 or 400, got: {result.stdout}"


def test_frontend_service_can_reach_backend_service():
    """Test that the frontend service can reach the backend service."""
    try:
        # Set a test environment variable
        os.environ["WEATHER_API_KEY"] = "test-api-key"
        
        # Start the services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        
        # Wait for services to start
        time.sleep(10)
        
        # Create a test script in the frontend container
        test_script = """
import requests
import sys

try:
    # Try to connect to the backend health endpoint
    response = requests.get('http://backend:8000/api/health')
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check if the response is successful
    if response.status_code == 200 and response.json().get('status') == 'healthy':
        print("SUCCESS: Frontend can communicate with backend")
        sys.exit(0)
    else:
        print("FAILURE: Backend returned unexpected response")
        sys.exit(1)
except Exception as e:
    print(f"FAILURE: Error connecting to backend: {e}")
    sys.exit(1)
"""
        
        # Write the test script to a file in the frontend container
        subprocess.run(
            [
                "docker-compose", "exec", "-T", "frontend",
                "bash", "-c", f"cat > /app/test_communication.py << 'EOL'\n{test_script}\nEOL"
            ],
            capture_output=True,
            text=True
        )
        
        # Run the test script in the frontend container
        result = subprocess.run(
            [
                "docker-compose", "exec", "frontend",
                "python", "/app/test_communication.py"
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the script was successful
        assert result.returncode == 0, f"Test script failed: {result.stderr}\nOutput: {result.stdout}"
        
        # Check that the success message is in the output
        assert "SUCCESS: Frontend can communicate with backend" in result.stdout, f"Expected success message, got: {result.stdout}"
        
    finally:
        # Stop the services
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )
        
        # Unset the test environment variable
        if "WEATHER_API_KEY" in os.environ:
            del os.environ["WEATHER_API_KEY"]