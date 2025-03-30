from fastapi import FastAPI
import datetime
import os

# Create the FastAPI application
app = FastAPI(title="Weather Data API", description="API for weather data retrieval and analysis")

# Version of the application
VERSION = "0.1.0"

@app.get("/")
async def root():
    """Root endpoint that provides a welcome message."""
    return {"message": "Welcome to Weather Data API"}

@app.get("/api/health")
async def health():
    """Health check endpoint that returns service status information."""
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "Weather Data API"
    }