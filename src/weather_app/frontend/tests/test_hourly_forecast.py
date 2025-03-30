"""
Test Hourly Forecast Component

This module tests the hourly forecast scrollable view component.
"""
import pytest
from unittest.mock import patch, MagicMock
from weather_app.frontend.components.hourly_forecast import HourlyForecast

@pytest.fixture
def hourly_forecast():
    """Fixture to create a HourlyForecast instance for testing."""
    return HourlyForecast()

@pytest.fixture
def sample_hourly_data():
    """Fixture to provide sample hourly forecast data for testing."""
    return {
        'location': 'Test City',
        'hourly_forecast': [
            {
                'time': '00:00',
                'temperature': 18,
                'condition': 'Clear',
                'precipitation_chance': 5,
                'humidity': 70,
                'wind_speed': 8,
                'wind_direction': 'NE'
            },
            {
                'time': '03:00',
                'temperature': 16,
                'condition': 'Clear',
                'precipitation_chance': 5,
                'humidity': 75,
                'wind_speed': 7,
                'wind_direction': 'NE'
            },
            {
                'time': '06:00',
                'temperature': 15,
                'condition': 'Partly Cloudy',
                'precipitation_chance': 10,
                'humidity': 80,
                'wind_speed': 6,
                'wind_direction': 'E'
            },
            {
                'time': '09:00',
                'temperature': 20,
                'condition': 'Sunny',
                'precipitation_chance': 0,
                'humidity': 65,
                'wind_speed': 8,
                'wind_direction': 'SE'
            },
            {
                'time': '12:00',
                'temperature': 25,
                'condition': 'Sunny',
                'precipitation_chance': 0,
                'humidity': 55,
                'wind_speed': 10,
                'wind_direction': 'S'
            },
            {
                'time': '15:00',
                'temperature': 27,
                'condition': 'Sunny',
                'precipitation_chance': 0,
                'humidity': 50,
                'wind_speed': 12,
                'wind_direction': 'S'
            },
            {
                'time': '18:00',
                'temperature': 24,
                'condition': 'Clear',
                'precipitation_chance': 5,
                'humidity': 60,
                'wind_speed': 10,
                'wind_direction': 'SW'
            },
            {
                'time': '21:00',
                'temperature': 20,
                'condition': 'Clear',
                'precipitation_chance': 5,
                'humidity': 65,
                'wind_speed': 8,
                'wind_direction': 'W'
            }
        ]
    }

def test_hourly_forecast_initialization():
    """Test that the HourlyForecast component initializes correctly."""
    hourly_forecast = HourlyForecast()
    assert isinstance(hourly_forecast, HourlyForecast)

@patch('streamlit.subheader')
def test_render_with_no_data(mock_subheader, hourly_forecast):
    """Test rendering when no data is provided."""
    with patch('streamlit.info') as mock_info:
        hourly_forecast.render(None)
        mock_info.assert_called_once()
        mock_subheader.assert_not_called()

@patch('streamlit.subheader')
@patch('streamlit.container')
def test_render_with_data(mock_container, mock_subheader, hourly_forecast, sample_hourly_data):
    """Test rendering with valid hourly forecast data."""
    # Mock the container context manager
    mock_container_instance = MagicMock()
    mock_container.return_value.__enter__.return_value = mock_container_instance
    
    # Mock the necessary methods to avoid pandas operations
    with patch.object(hourly_forecast, '_display_hourly_cards') as mock_cards:
        with patch.object(hourly_forecast, '_display_temperature_trend') as mock_temp:
            with patch.object(hourly_forecast, '_display_precipitation_chance') as mock_precip:
                # Call the render method
                hourly_forecast.render(sample_hourly_data)
                
                # Verify the subheader was called
                mock_subheader.assert_called_once_with("Hourly Forecast")
                
                # Verify container was created
                mock_container.assert_called_once()
                
                # Verify the display methods were called with the hourly forecast data
                mock_cards.assert_called_once_with(sample_hourly_data['hourly_forecast'])
                mock_temp.assert_called_once_with(sample_hourly_data['hourly_forecast'])
                mock_precip.assert_called_once_with(sample_hourly_data['hourly_forecast'])

@patch('streamlit.markdown')
def test_display_hourly_cards(mock_markdown, hourly_forecast, sample_hourly_data):
    """Test that hourly forecast cards are displayed correctly."""
    # Mock the columns function to return a list of mocks
    mock_col = MagicMock()
    mock_cols = [mock_col] * len(sample_hourly_data['hourly_forecast'])  # Same mock for all columns
    
    with patch('streamlit.columns', return_value=mock_cols):
        # Call the method
        hourly_forecast._display_hourly_cards(sample_hourly_data['hourly_forecast'])
        
        # Verify markdown was called at least once
        assert mock_markdown.call_count > 0