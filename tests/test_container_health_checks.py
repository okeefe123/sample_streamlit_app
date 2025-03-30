import os
import pytest
import subprocess
import time
import json


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


def test_backend_health_check(docker_compose_services):
    """Test that the backend health check is working."""
    # Get the health status of the backend container
    result = subprocess.run(
        ["docker", "inspect", "--format='{{json .State.Health}}'", "weather-app-backend"],
        capture_output=True,
        text=True
    )
    
    # Parse the JSON output
    health_status = json.loads(result.stdout.strip().strip("'"))
    
    # Check that the health status is healthy
    assert health_status["Status"] == "healthy", f"Backend health status is not healthy: {health_status}"
    
    # Check that there are health check logs
    assert len(health_status["Log"]) > 0, "No health check logs found for backend"
    
    # Check that the most recent health check was successful
    assert health_status["Log"][-1]["ExitCode"] == 0, "Most recent backend health check failed"


def test_frontend_health_check(docker_compose_services):
    """Test that the frontend health check is working."""
    # Get the health status of the frontend container
    result = subprocess.run(
        ["docker", "inspect", "--format='{{json .State.Health}}'", "weather-app-frontend"],
        capture_output=True,
        text=True
    )
    
    # Parse the JSON output
    health_status = json.loads(result.stdout.strip().strip("'"))
    
    # Check that the health status is healthy
    assert health_status["Status"] == "healthy", f"Frontend health status is not healthy: {health_status}"
    
    # Check that there are health check logs
    assert len(health_status["Log"]) > 0, "No health check logs found for frontend"
    
    # Check that the most recent health check was successful
    assert health_status["Log"][-1]["ExitCode"] == 0, "Most recent frontend health check failed"


def test_health_check_failure_handling():
    """Test that the health check correctly identifies unhealthy services."""
    try:
        # Start the services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        
        # Wait for services to start
        time.sleep(10)
        
        # Stop the backend service but keep the container running
        subprocess.run(
            ["docker-compose", "exec", "backend", "pkill", "uvicorn"],
            capture_output=True,
            text=True
        )
        
        # Wait for health checks to run
        time.sleep(30)
        
        # Get the health status of the backend container
        result = subprocess.run(
            ["docker", "inspect", "--format='{{json .State.Health}}'", "weather-app-backend"],
            capture_output=True,
            text=True
        )
        
        # Parse the JSON output
        health_status = json.loads(result.stdout.strip().strip("'"))
        
        # Check that the health status is unhealthy
        assert health_status["Status"] == "unhealthy", "Backend health status should be unhealthy after stopping the service"
        
    finally:
        # Stop the services
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )