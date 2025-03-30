#!/usr/bin/env python3
"""
Script to run the frontend Streamlit application
"""
import os
import subprocess

if __name__ == "__main__":
    frontend_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "src", "weather_app", "frontend", "app.py"
    )
    
    print(f"Starting Streamlit frontend from: {frontend_path}")
    subprocess.run(["streamlit", "run", frontend_path])