import pytest
import os
from unittest.mock import patch
import tempfile
import json

def test_api_key_from_environment_variable():
    """Test that API keys are loaded from environment variables."""
    # Import here to avoid circular imports
    from weather_app.backend.config import settings
    
    # Set environment variables for testing
    with patch.dict(os.environ, {"WEATHER_API_KEY": "test_api_key"}):
        # Reload settings to pick up the environment variables
        from importlib import reload
        from weather_app.backend import config
        reload(config)
        from weather_app.backend.config import settings
        
        # Check that the API key is loaded from the environment variable
        assert settings.weather_api_key == "test_api_key"
        
def test_environment_based_configuration():
    """Test that different configurations are loaded based on environment."""
    # Create temporary config files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create development config
        dev_config = {
            "app_name": "Weather API Dev",
            "debug": True,
            "log_level": "DEBUG"
        }
        dev_config_path = os.path.join(temp_dir, "config_development.json")
        with open(dev_config_path, "w") as f:
            json.dump(dev_config, f)
        
        # Create production config
        prod_config = {
            "app_name": "Weather API Prod",
            "debug": False,
            "log_level": "INFO"
        }
        prod_config_path = os.path.join(temp_dir, "config_production.json")
        with open(prod_config_path, "w") as f:
            json.dump(prod_config, f)
        
        # Test development environment
        with patch.dict(os.environ, {
            "APP_ENV": "development",
            "CONFIG_DIR": temp_dir
        }):
            # Import and reload config to pick up environment changes
            from importlib import reload
            from weather_app.backend import config
            reload(config)
            from weather_app.backend.config import settings
            
            # Check development settings
            assert settings.app_name == "Weather API Dev"
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
        
        # Test production environment
        with patch.dict(os.environ, {
            "APP_ENV": "production",
            "CONFIG_DIR": temp_dir
        }):
            # Import and reload config to pick up environment changes
            from importlib import reload
            from weather_app.backend import config
            reload(config)
            from weather_app.backend.config import settings
            
            # Check production settings
            assert settings.app_name == "Weather API Prod"
            assert settings.debug is False
            assert settings.log_level == "INFO"