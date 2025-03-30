"""
Configuration Module

This module handles loading configuration from environment variables and config files
based on the current environment (development/production).
"""
import os
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# Default environment is development
DEFAULT_ENV = "development"

# Get current environment from environment variable
ENVIRONMENT = os.getenv("APP_ENV", DEFAULT_ENV)

# Configuration directory
CONFIG_DIR = os.getenv("CONFIG_DIR", str(Path(__file__).parent / "config"))


class Settings(BaseModel):
    """Settings model for application configuration."""
    # App settings
    app_name: str = "Weather Data API"
    debug: bool = True
    log_level: str = "INFO"
    
    # API settings
    weather_api_key: str = ""
    weather_api_url: str = "https://api.example.com/weather"
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:8501",  # Default Streamlit port
        "http://localhost:3000",  # Alternative development server
        "https://weather-app.example.com"  # Production domain
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]


def load_config_from_file(env: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file based on environment.
    
    Args:
        env: Environment name (development, production, etc.)
        
    Returns:
        Dict containing configuration values
    """
    config_path = Path(CONFIG_DIR) / f"config_{env}.json"
    
    # If config file exists, load it
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    
    # Otherwise return empty dict
    return {}


def load_environment_variables() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dict containing configuration values from environment variables
    """
    config = {}
    
    # API keys
    if weather_api_key := os.getenv("WEATHER_API_KEY"):
        config["weather_api_key"] = weather_api_key
    
    if weather_api_url := os.getenv("WEATHER_API_URL"):
        config["weather_api_url"] = weather_api_url
    
    # Debug mode
    if debug := os.getenv("DEBUG"):
        config["debug"] = debug.lower() in ("true", "1", "yes")
    
    # Log level
    if log_level := os.getenv("LOG_LEVEL"):
        config["log_level"] = log_level
    
    # CORS origins (comma-separated list)
    if cors_origins := os.getenv("CORS_ORIGINS"):
        config["cors_origins"] = [origin.strip() for origin in cors_origins.split(",")]
    
    return config


# Create base settings
settings = Settings()

# Load config from file based on environment
file_config = load_config_from_file(ENVIRONMENT)
if file_config:
    settings = Settings(**file_config)

# Override with environment variables (highest priority)
env_config = load_environment_variables()
if env_config:
    # Update settings with environment variables
    for key, value in env_config.items():
        setattr(settings, key, value)