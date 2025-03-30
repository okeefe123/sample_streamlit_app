import os
import pytest
import subprocess
import time
import requests


@pytest.fixture
def frontend_dockerfile_path():
    """Return the path to the frontend Dockerfile."""
    return os.path.join(os.getcwd(), "src", "weather_app", "frontend", "Dockerfile")


def test_frontend_dockerfile_exists(frontend_dockerfile_path):
    """Test that the frontend Dockerfile exists."""
    assert os.path.exists(frontend_dockerfile_path), "Frontend Dockerfile does not exist"


def test_frontend_dockerfile_content(frontend_dockerfile_path):
    """Test that the frontend Dockerfile contains necessary components."""
    with open(frontend_dockerfile_path, "r") as f:
        content = f.read()
    
    # Check for Python base image
    assert "FROM python" in content, "Dockerfile should use Python base image"
    
    # Check for working directory
    assert "WORKDIR" in content, "Dockerfile should set a working directory"
    
    # Check for copying requirements or installing dependencies
    assert any(cmd in content for cmd in ["COPY requirements", "pip install"]), \
        "Dockerfile should install dependencies"
    
    # Check for exposing a port
    assert "EXPOSE" in content, "Dockerfile should expose a port"
    
    # Check for CMD or ENTRYPOINT to run the application
    assert any(cmd in content for cmd in ["CMD", "ENTRYPOINT"]), \
        "Dockerfile should have a command to run the application"


@pytest.mark.integration
def test_frontend_image_builds():
    """Test that the frontend Docker image builds successfully."""
    frontend_dir = os.path.join(os.getcwd(), "src", "weather_app", "frontend")
    result = subprocess.run(
        ["docker", "build", "-t", "weather-frontend-test", "."],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"


@pytest.mark.integration
def test_frontend_container_runs():
    """Test that the frontend container runs and is accessible."""
    # Build the image
    frontend_dir = os.path.join(os.getcwd(), "src", "weather_app", "frontend")
    subprocess.run(
        ["docker", "build", "-t", "weather-frontend-test", "."],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    
    # Run the container
    container_process = subprocess.Popen(
        [
            "docker", "run", 
            "--rm", "-d", 
            "-p", "8501:8501", 
            "--name", "weather-frontend-test-container",
            "weather-frontend-test"
        ],
        stdout=subprocess.PIPE,
        text=True
    )
    container_id = container_process.stdout.read().strip()
    
    try:
        # Wait for container to start
        time.sleep(5)
        
        # Test that the frontend is accessible
        response = requests.get("http://localhost:8501")
        assert response.status_code == 200, "Frontend did not return 200 OK"
    
    finally:
        # Clean up container
        subprocess.run(
            ["docker", "stop", container_id],
            capture_output=True
        )