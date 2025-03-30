"""
Location Form Component

This module provides a form component for entering location information.
"""
import streamlit as st
from typing import Optional, Tuple, Callable

class LocationForm:
    """
    A form component for entering and validating location information.
    """
    
    def __init__(self):
        """Initialize the location form component."""
        self._location = ""
    
    def render(self) -> Optional[str]:
        """
        Render the location input form and handle submission.
        
        Returns:
            str: The submitted location if the form was submitted and valid, None otherwise.
        """
        st.subheader("Enter Location")
        
        with st.form(key="location_form"):
            location = st.text_input(
                "City Name",
                placeholder="Enter a city name (e.g., New York, London)",
                help="Enter the name of the city you want to get weather information for."
            )
            
            submit_button = st.form_submit_button(label="Get Weather")
            
            if submit_button:
                if self.validate_location(location):
                    self._location = location
                    return location
        
        return None
    
    def validate_location(self, location: str) -> bool:
        """
        Validate the location input.
        
        Args:
            location: The location string to validate
            
        Returns:
            bool: True if the location is valid, False otherwise
        """
        if not location or location.strip() == "":
            st.error("Please enter a valid location.")
            return False
        
        return True
    
    def submit_location(self, location: str) -> Optional[str]:
        """
        Submit a location for processing.
        
        Args:
            location: The location to submit
            
        Returns:
            str: The validated location if valid, None otherwise
        """
        if self.validate_location(location):
            self._location = location
            return location
        
        return None
    
    @property
    def location(self) -> str:
        """Get the current location value."""
        return self._location