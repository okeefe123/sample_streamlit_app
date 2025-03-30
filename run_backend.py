#!/usr/bin/env python3
"""
Script to run the backend FastAPI application
"""
from src.weather_app.backend.main import run_app

if __name__ == "__main__":
    print("Starting backend server...")
    run_app()