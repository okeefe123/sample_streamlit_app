"""
Test Humidity Display Component

This module tests the humidity visualization component.
"""
import pytest
from unittest.mock import patch, MagicMock
from weather_app.frontend.components.humidity_display import HumidityDisplay

@pytest.fixture
def humidity_display():
    """Fixture to create a HumidityDisplay instance for testing."""
    return HumidityDisplay()

@pytest.fixture
def sample_forecast_data():
    """Fixture to provide sample forecast data for testing."""
    return {
        'location': 'Test City',
        'forecast': [
            {
                'date': '2025-03-30',
                'humidity': 75,
                'temperature_high': 25,
                'temperature_low': 18
            },
            {
                'date': '2025-03-31',
                'humidity': 60,
                'temperature_high': 28,
                'temperature_low': 20
            },
            {
                'date': '2025-04-01',
                'humidity': 85,
                'temperature_high': 22,
                'temperature_low': 15
            }
        ]
    }

def test_humidity_display_initialization():
    """Test that the HumidityDisplay component initializes correctly."""
    humidity_display = HumidityDisplay()
    assert isinstance(humidity_display, HumidityDisplay)

@patch('streamlit.subheader')
def test_render_with_no_data(mock_subheader, humidity_display):
    """Test rendering when no data is provided."""
    with patch('streamlit.info') as mock_info:
        humidity_display.render(None)
        mock_info.assert_called_once()
        mock_subheader.assert_not_called()

@patch('streamlit.subheader')
@patch('streamlit.plotly_chart')
def test_render_with_data(mock_plotly_chart, mock_subheader, humidity_display, sample_forecast_data):
    """Test rendering with valid forecast data."""
    # Mock the necessary methods to avoid pandas operations
    with patch.object(humidity_display, '_display_humidity_indicators') as mock_indicators:
        with patch.object(humidity_display, '_display_humidity_temperature_chart') as mock_chart:
            # Call the render method
            humidity_display.render(sample_forecast_data)
            
            # Verify the subheader was called
            mock_subheader.assert_called_once_with("Humidity Analysis")
            
            # Verify the display methods were called with the forecast data
            mock_indicators.assert_called_once_with(sample_forecast_data['forecast'])
            mock_chart.assert_called_once_with(sample_forecast_data['forecast'])

@patch('streamlit.markdown')
def test_display_humidity_indicators(mock_markdown, humidity_display, sample_forecast_data):
    """Test that humidity indicators are displayed correctly."""
    # Mock the columns function to return a context manager
    mock_col = MagicMock()
    mock_cols = [mock_col, mock_col, mock_col]  # Same mock for all columns for simplicity
    
    with patch('streamlit.columns', return_value=mock_cols):
        # Call the method
        humidity_display._display_humidity_indicators(sample_forecast_data['forecast'])
        
        # Since we're using the same mock for all columns, the call count should be
        # multiplied by the number of forecast days
        assert mock_markdown.call_count > 0