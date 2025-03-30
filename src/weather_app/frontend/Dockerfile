FROM python:3.9-slim

# Set working directory for the app
WORKDIR /app

# Set environment variable for port
ENV PORT=8501

# Install uv
RUN pip install --no-cache-dir uv

# Create proper package structure
RUN mkdir -p /app/weather_app/frontend

# Copy the application code to the correct package location
COPY . /app/weather_app/frontend/

# Create a virtual environment
RUN uv venv

# Install dependencies directly without editable mode
WORKDIR /app
RUN cd /app/weather_app/frontend && uv pip install --no-cache-dir streamlit==1.24.0 requests==2.28.2 python-dotenv==1.0.0 pytest==7.3.1 httpx==0.24.0 numpy==1.24.3 matplotlib==3.7.1 pandas==2.0.1 plotly==5.14.1

# Set PYTHONPATH environment variable to include the app directory
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD uv run streamlit run weather_app/frontend/app.py --server.port=$PORT --server.address=0.0.0.0