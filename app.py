#!/usr/bin/env python3
"""
Weather Data Analysis Application
Main entry point for running either the backend or frontend
"""
import argparse
import sys
import os
import subprocess

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Weather Data Analysis Application")
    parser.add_argument(
        "--component", 
        choices=["backend", "frontend", "all"], 
        default="all",
        help="Component to run (backend, frontend, or all)"
    )
    
    args = parser.parse_args()
    
    if args.component in ["backend", "all"]:
        # Import and run backend
        print("Starting backend server...")
        from src.weather_app.backend.main import run_app as run_backend
        if args.component == "backend":
            run_backend()
            return
        else:
            # Start backend in a separate process if running both
            import multiprocessing
            backend_process = multiprocessing.Process(target=run_backend)
            backend_process.start()
    
    if args.component in ["frontend", "all"]:
        # Run the frontend using streamlit CLI
        print("Starting frontend application...")
        frontend_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "src", "weather_app", "frontend", "app.py"
        )
        
        # Use subprocess to run streamlit
        streamlit_cmd = ["streamlit", "run", frontend_path]
        subprocess.run(streamlit_cmd)

if __name__ == "__main__":
    main()