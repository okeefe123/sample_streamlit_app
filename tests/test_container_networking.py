import os
import pytest
import subprocess
import time
import requests


@pytest.fixture(scope="module")
def docker_network():
    """Create a Docker network for testing."""
    # Create a Docker network
    network_name = "weather-app-test-network"
    subprocess.run(
        ["docker", "network", "create", network_name],
        capture_output=True,
        text=True
    )
    
    yield network_name
    
    # Clean up the network
    subprocess.run(
        ["docker", "network", "rm", network_name],
        capture_output=True,
        text=True
    )


@pytest.fixture(scope="module")
def backend_container(docker_network):
    """Start a backend container for testing."""
    # Build the backend image
    backend_dir = os.path.join(os.getcwd(), "backend")
    subprocess.run(
        ["docker", "build", "-t", "weather-backend-test", "."],
        cwd=backend_dir,
        capture_output=True,
        text=True
    )
    
    # Run the backend container
    container_process = subprocess.Popen(
        [
            "docker", "run", 
            "--rm", "-d", 
            "--network", docker_network,
            "--name", "weather-backend-test-container",
            "-e", "ENVIRONMENT=development",
            "weather-backend-test"
        ],
        stdout=subprocess.PIPE,
        text=True
    )
    container_id = container_process.stdout.read().strip()
    
    # Wait for container to start
    time.sleep(5)
    
    yield container_id
    
    # Clean up container
    subprocess.run(
        ["docker", "stop", container_id],
        capture_output=True
    )


@pytest.fixture(scope="module")
def frontend_container(docker_network, backend_container):
    """Start a frontend container for testing."""
    # Build the frontend image
    frontend_dir = os.path.join(os.getcwd(), "src", "weather_app", "frontend")
    subprocess.run(
        ["docker", "build", "-t", "weather-frontend-test", "."],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    
    # Run the frontend container
    container_process = subprocess.Popen(
        [
            "docker", "run", 
            "--rm", "-d", 
            "--network", docker_network,
            "-p", "8501:8501",
            "--name", "weather-frontend-test-container",
            "-e", "BACKEND_URL=http://weather-backend-test-container:8000",
            "weather-frontend-test"
        ],
        stdout=subprocess.PIPE,
        text=True
    )
    container_id = container_process.stdout.read().strip()
    
    # Wait for container to start
    time.sleep(5)
    
    yield container_id
    
    # Clean up container
    subprocess.run(
        ["docker", "stop", container_id],
        capture_output=True
    )


@pytest.mark.integration
def test_frontend_can_access_backend(frontend_container):
    """Test that the frontend container can access the backend container."""
    # Execute a command in the frontend container to make a request to the backend
    result = subprocess.run(
        [
            "docker", "exec", 
            "weather-frontend-test-container",
            "python", "-c", 
            "import requests; response = requests.get('http://weather-backend-test-container:8000/api/health'); print(response.status_code); print(response.text)"
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


@pytest.mark.integration
def test_frontend_accessible_from_host(frontend_container):
    """Test that the frontend is accessible from the host."""
    # Make a request to the frontend from the host
    response = requests.get("http://localhost:8501")
    
    # Check that the response status code is 200
    assert response.status_code == 200, f"Expected status code 200, got: {response.status_code}"