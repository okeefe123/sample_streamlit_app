import os
import pytest
import subprocess
import time
import requests


def test_docker_compose_file_exists():
    """Test that the docker-compose.yml file exists."""
    assert os.path.exists("docker-compose.yml"), "docker-compose.yml file does not exist"


def test_docker_compose_validate():
    """Test that the docker-compose.yml file is valid."""
    result = subprocess.run(
        ["docker-compose", "config"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"


@pytest.mark.integration
def test_docker_compose_up():
    """Test that the services can be started using docker-compose."""
    try:
        # Start the services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        
        # Wait for services to start
        time.sleep(10)
        
        # Check that the backend is running
        backend_response = requests.get("http://localhost:8000/api/health")
        assert backend_response.status_code == 200, "Backend health check failed"
        assert backend_response.json()["status"] == "healthy", "Backend health status is not 'healthy'"
        
        # Check that the frontend is running
        frontend_response = requests.get("http://localhost:8501")
        assert frontend_response.status_code == 200, "Frontend is not accessible"
        
    finally:
        # Stop the services
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )


@pytest.mark.integration
def test_environment_variables():
    """Test that environment variables are correctly passed to containers."""
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
        
        # Check that the environment variable is set in the backend container
        result = subprocess.run(
            [
                "docker-compose", "exec", "backend",
                "python", "-c", 
                "import os; print(os.environ.get('WEATHER_API_KEY'))"
            ],
            capture_output=True,
            text=True
        )
        assert "test-api-key" in result.stdout, "Environment variable not correctly passed to backend container"
        
    finally:
        # Stop the services
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )
        
        # Unset the test environment variable
        del os.environ["WEATHER_API_KEY"]


@pytest.mark.integration
def test_volume_mounts():
    """Test that volume mounts work correctly for code reloading."""
    try:
        # Start the services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        
        # Wait for services to start
        time.sleep(10)
        
        # Create a temporary file in the backend directory
        with open("backend/test_file.txt", "w") as f:
            f.write("test content")
        
        # Check that the file is accessible in the container
        result = subprocess.run(
            [
                "docker-compose", "exec", "backend",
                "cat", "test_file.txt"
            ],
            capture_output=True,
            text=True
        )
        assert "test content" in result.stdout, "Volume mount not working correctly for backend"
        
        # Create a temporary file in the frontend directory
        with open("src/weather_app/frontend/test_file.txt", "w") as f:
            f.write("test content")
        
        # Check that the file is accessible in the container
        result = subprocess.run(
            [
                "docker-compose", "exec", "frontend",
                "cat", "test_file.txt"
            ],
            capture_output=True,
            text=True
        )
        assert "test content" in result.stdout, "Volume mount not working correctly for frontend"
        
    finally:
        # Stop the services
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )
        
        # Remove the temporary files
        if os.path.exists("backend/test_file.txt"):
            os.remove("backend/test_file.txt")
        if os.path.exists("src/weather_app/frontend/test_file.txt"):
            os.remove("src/weather_app/frontend/test_file.txt")