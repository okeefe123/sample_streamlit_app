"""
Test Wind Display Component

This module tests the wind data display component.
"""
import pytest
from unittest.mock import patch, MagicMock
from weather_app.frontend.components.wind_display import WindDisplay

@pytest.fixture
def wind_display():
    """Fixture to create a WindDisplay instance for testing."""
    return WindDisplay()

@pytest.fixture
def sample_forecast_data():
    """Fixture to provide sample forecast data for testing."""
    return {
        'location': 'Test City',
        'forecast': [
            {
                'date': '2025-03-30',
                'wind_speed': 15,
                'wind_direction': 'NE',
                'wind_gust': 25
            },
            {
                'date': '2025-03-31',
                'wind_speed': 10,
                'wind_direction': 'SW',
                'wind_gust': 18
            },
            {
                'date': '2025-04-01',
                'wind_speed': 8,
                'wind_direction': 'N',
                'wind_gust': 12
            }
        ]
    }

def test_wind_display_initialization():
    """Test that the WindDisplay component initializes correctly."""
    wind_display = WindDisplay()
    assert isinstance(wind_display, WindDisplay)

@patch('streamlit.subheader')
def test_render_with_no_data(mock_subheader, wind_display):
    """Test rendering when no data is provided."""
    with patch('streamlit.info') as mock_info:
        wind_display.render(None)
        mock_info.assert_called_once()
        mock_subheader.assert_not_called()

@patch('streamlit.subheader')
@patch('streamlit.plotly_chart')
def test_render_with_data(mock_plotly_chart, mock_subheader, wind_display, sample_forecast_data):
    """Test rendering with valid forecast data."""
    # Mock the necessary methods to avoid pandas operations
    with patch.object(wind_display, '_display_wind_direction_indicators') as mock_direction:
        with patch.object(wind_display, '_display_wind_speed_chart') as mock_speed:
            # Call the render method
            wind_display.render(sample_forecast_data)
            
            # Verify the subheader was called
            mock_subheader.assert_called_once_with("Wind Data")
            
            # Verify the display methods were called with the forecast data
            mock_direction.assert_called_once_with(sample_forecast_data['forecast'])
            mock_speed.assert_called_once_with(sample_forecast_data['forecast'])

@patch('streamlit.markdown')
def test_display_wind_direction_indicators(mock_markdown, wind_display, sample_forecast_data):
    """Test that wind direction indicators are displayed correctly."""
    # Mock the columns function to return a context manager
    mock_col = MagicMock()
    mock_cols = [mock_col, mock_col, mock_col]  # Same mock for all columns for simplicity
    
    with patch('streamlit.columns', return_value=mock_cols):
        # Call the method
        wind_display._display_wind_direction_indicators(sample_forecast_data['forecast'])
        
        # Since we're using the same mock for all columns, the call count should be
        # multiplied by the number of forecast days
        assert mock_markdown.call_count > 0