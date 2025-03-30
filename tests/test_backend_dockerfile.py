import os
import pytest
import subprocess
import time
import requests


@pytest.fixture
def backend_dockerfile_path():
    """Return the path to the backend Dockerfile."""
    return os.path.join(os.getcwd(), "backend", "Dockerfile")


def test_backend_dockerfile_exists(backend_dockerfile_path):
    """Test that the backend Dockerfile exists."""
    assert os.path.exists(backend_dockerfile_path), "Backend Dockerfile does not exist"


def test_backend_dockerfile_content(backend_dockerfile_path):
    """Test that the backend Dockerfile contains necessary components."""
    with open(backend_dockerfile_path, "r") as f:
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
def test_backend_image_builds():
    """Test that the backend Docker image builds successfully."""
    backend_dir = os.path.join(os.getcwd(), "backend")
    result = subprocess.run(
        ["docker", "build", "-t", "weather-backend-test", "."],
        cwd=backend_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"


@pytest.mark.integration
def test_backend_container_runs():
    """Test that the backend container runs and the health endpoint is accessible."""
    # Build the image
    backend_dir = os.path.join(os.getcwd(), "backend")
    subprocess.run(
        ["docker", "build", "-t", "weather-backend-test", "."],
        cwd=backend_dir,
        capture_output=True,
        text=True
    )
    
    # Run the container
    container_process = subprocess.Popen(
        [
            "docker", "run", 
            "--rm", "-d", 
            "-p", "8000:8000", 
            "--name", "weather-backend-test-container",
            "weather-backend-test"
        ],
        stdout=subprocess.PIPE,
        text=True
    )
    container_id = container_process.stdout.read().strip()
    
    try:
        # Wait for container to start
        time.sleep(5)
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/health")
        assert response.status_code == 200, "Health endpoint did not return 200 OK"
        assert "status" in response.json(), "Health response should contain status"
        assert response.json()["status"] == "healthy", "Health status should be 'healthy'"
    
    finally:
        # Clean up container
        subprocess.run(
            ["docker", "stop", container_id],
            capture_output=True
        )