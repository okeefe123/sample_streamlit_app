import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from weather_app.frontend.components.location_form import LocationForm

def test_location_form_initialization():
    """Test that the location form initializes correctly."""
    # Create a location form instance
    form = LocationForm()
    
    # Check that the form has the expected attributes
    assert hasattr(form, 'submit_location')
    assert callable(form.submit_location)

def test_location_form_validation():
    """Test that the location form validates input correctly."""
    # Create a location form instance
    form = LocationForm()
    
    # Test with empty location
    with patch('streamlit.error') as mock_error:
        result = form.validate_location("")
        assert result is False
        mock_error.assert_called_once()
    
    # Test with valid location
    with patch('streamlit.error') as mock_error:
        result = form.validate_location("New York")
        assert result is True
        mock_error.assert_not_called()