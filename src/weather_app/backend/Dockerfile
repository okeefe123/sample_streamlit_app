FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variable for port
ENV PORT=8001

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml
COPY pyproject.toml .

# Create a virtual environment
RUN uv venv

# Install dependencies using uv
RUN uv pip install --no-cache-dir -e .

# Copy the application code
COPY . .

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE ${PORT}

# Command to run the application
CMD ["uvicorn", "weather_app.backend.api.app:app", "--host", "0.0.0.0", "--port", "${PORT}"] 