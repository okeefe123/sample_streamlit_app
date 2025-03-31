FROM python:3.9-slim

# Set working directory for the app
WORKDIR /app

# Set environment variable for port
ENV PORT=8000

# Install uv
RUN pip install --no-cache-dir uv

# Create proper package structure
RUN mkdir -p /app/weather_app/backend

# Copy the application code to the correct package location
COPY . /app/weather_app/backend/

# Create a virtual environment
RUN uv venv

# Install dependencies from pyproject.toml
WORKDIR /app
RUN cd /app/weather_app/backend && uv pip install --no-cache-dir -e .

# Set PYTHONPATH environment variable to include the app directory
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application using uvicorn through uv
CMD uv run uvicorn weather_app.backend.api.app:app --host 0.0.0.0 --port $PORT 