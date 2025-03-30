import os
import pytest
import subprocess
import time
import json


@pytest.fixture(scope="module")
def updated_docker_compose():
    """Update the docker-compose.yml file to include the test data volume."""
    # Read the current docker-compose.yml file
    with open("docker-compose.yml", "r") as f:
        docker_compose_content = f.read()
    
    # Check if the test data volume is already defined in volumes section
    if "test_data:" not in docker_compose_content:
        # Add the test data volume to the volumes section
        docker_compose_content = docker_compose_content.replace(
            "volumes:\n  backend_modules:\n  frontend_modules:",
            "volumes:\n  backend_modules:\n  frontend_modules:\n  test_data:"
        )
    
    # Check if the test data volume is already mounted in the backend service
    if "./test_data:/app/test_data" not in docker_compose_content:
        # Add the test data volume to the backend service
        backend_volumes_pattern = "    volumes:\n      - ./backend:/app\n      - backend_modules:/app/node_modules"
        if backend_volumes_pattern in docker_compose_content:
            docker_compose_content = docker_compose_content.replace(
                backend_volumes_pattern,
                backend_volumes_pattern + "\n      - ./test_data:/app/test_data"
            )
    
    # Check if the test data volume is already mounted in the frontend service
    if "./test_data:/app/test_data" not in docker_compose_content:
        # Add the test data volume to the frontend service
        frontend_volumes_pattern = "    volumes:\n      - ./src/weather_app/frontend:/app\n      - frontend_modules:/app/node_modules"
        if frontend_volumes_pattern in docker_compose_content:
            docker_compose_content = docker_compose_content.replace(
                frontend_volumes_pattern,
                frontend_volumes_pattern + "\n      - ./test_data:/app/test_data"
            )
    
    # Write the updated docker-compose.yml file
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    yield
    
    # No cleanup needed as we're keeping the test data volume in the docker-compose.yml file


@pytest.fixture(scope="module")
def docker_compose_services(updated_docker_compose):
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


def test_backend_can_access_test_data(docker_compose_services):
    """Test that the backend container can access the test data."""
    # Execute a command in the backend container to check if the test data is accessible
    result = subprocess.run(
        [
            "docker-compose", "exec", "backend",
            "python", "-c", 
            "import os, json; print(os.path.exists('/app/test_data/weather_samples.json')); "
            "print(json.load(open('/app/test_data/weather_samples.json')).keys() if os.path.exists('/app/test_data/weather_samples.json') else 'File not found')"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the command was successful
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check that the test data file exists
    assert "True" in result.stdout, "Test data file not found in backend container"
    
    # Check that the test data can be loaded
    assert "london" in result.stdout and "new_york" in result.stdout and "tokyo" in result.stdout, \
        f"Test data could not be loaded in backend container: {result.stdout}"


def test_frontend_can_access_test_data(docker_compose_services):
    """Test that the frontend container can access the test data."""
    # Execute a command in the frontend container to check if the test data is accessible
    result = subprocess.run(
        [
            "docker-compose", "exec", "frontend",
            "python", "-c", 
            "import os, json; print(os.path.exists('/app/test_data/weather_samples.json')); "
            "print(json.load(open('/app/test_data/weather_samples.json')).keys() if os.path.exists('/app/test_data/weather_samples.json') else 'File not found')"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the command was successful
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    
    # Check that the test data file exists
    assert "True" in result.stdout, "Test data file not found in frontend container"
    
    # Check that the test data can be loaded
    assert "london" in result.stdout and "new_york" in result.stdout and "tokyo" in result.stdout, \
        f"Test data could not be loaded in frontend container: {result.stdout}"


def test_backend_can_use_test_data_for_mocking(docker_compose_services):
    """Test that the backend can use the test data for mocking external API calls."""
    # Create a test script in the backend container
    test_script = """
import json
import os

# Load the test data
with open('/app/test_data/weather_samples.json', 'r') as f:
    test_data = json.load(f)

# Check if the test data contains the expected cities
cities = list(test_data.keys())
print(f"Cities in test data: {cities}")

# Check if the test data contains current weather data
for city in cities:
    if 'current' in test_data[city]:
        print(f"{city} has current weather data: {test_data[city]['current']['temperature']}°C")
    else:
        print(f"{city} does not have current weather data")

# Check if the test data contains forecast data
for city in cities:
    if 'forecast' in test_data[city]:
        print(f"{city} has forecast data for {len(test_data[city]['forecast'])} days")
    else:
        print(f"{city} does not have forecast data")
"""
    
    # Write the test script to a file in the backend container
    subprocess.run(
        [
            "docker-compose", "exec", "-T", "backend",
            "bash", "-c", f"cat > /app/test_data_script.py << 'EOL'\n{test_script}\nEOL"
        ],
        capture_output=True,
        text=True
    )
    
    # Run the test script in the backend container
    result = subprocess.run(
        [
            "docker-compose", "exec", "backend",
            "python", "/app/test_data_script.py"
        ],
        capture_output=True,
        text=True
    )
    
    # Check that the script was successful
    assert result.returncode == 0, f"Test script failed: {result.stderr}\nOutput: {result.stdout}"
    
    # Check that the script output contains the expected data
    assert "Cities in test data:" in result.stdout, f"Expected cities list, got: {result.stdout}"
    assert "london has current weather data" in result.stdout, f"Expected London current weather data, got: {result.stdout}"
    assert "london has forecast data for 3 days" in result.stdout, f"Expected London forecast data, got: {result.stdout}"