sa# Weather API Implementation Plan

## Executive Summary

This document outlines the implementation plan for integrating a weather API into our Streamlit application. After analyzing the National Weather Service (NWS) API and evaluating alternatives, we propose a dual-implementation approach that leverages the strengths of both the NWS API and a global weather API provider.

## API Analysis

### National Weather Service (NWS) API

**Strengths:**
- Free to use with no API key required
- Comprehensive and authoritative US weather data
- Extensive endpoint options (forecasts, alerts, observations)
- Well-documented
- No commercial usage restrictions

**Limitations:**
- US-only coverage
- Complex workflow requiring coordinate-to-grid conversion
- Known issues documented in the API documentation
- Rate limits not publicly disclosed
- More complex than some commercial alternatives

**Key Endpoints:**
1. `/points/{latitude},{longitude}` - Provides grid endpoints for a location
2. `/gridpoints/{office}/{gridX},{gridY}/forecast` - 7-day forecast (12-hour periods)
3. `/gridpoints/{office}/{gridX},{gridY}/forecast/hourly` - Hourly forecast
4. `/gridpoints/{office}/{gridX},{gridY}` - Raw forecast data
5. `/stations/{stationId}/observations/latest` - Latest observations
6. `/alerts/active?area={state}` - Active weather alerts

**Implementation Flow:**
1. Get user location (latitude/longitude)
2. Call `/points/{latitude},{longitude}` to get grid data
3. Use returned grid data to call forecast, observation and alert endpoints
4. Parse and display results

### Alternative APIs

For global coverage and simplified implementation, consider these alternatives:

1. **OpenWeatherMap**
   - Free tier: 1,000 calls/day
   - Global coverage
   - Simple API structure
   - Requires API key

2. **WeatherAPI.com**
   - Free tier: 1,000,000 calls/month
   - Global coverage
   - Comprehensive data
   - Simple integration

3. **Tomorrow.io**
   - Free tier available
   - Global coverage
   - ML-enhanced forecasts
   - Requires API key

## Recommended Implementation Strategy

### Primary Approach: Hybrid Implementation

We recommend implementing a hybrid approach:

1. **For US locations**: Use the NWS API as the primary data source
   - Benefit from authoritative US government data
   - No rate limit concerns for production
   - No API key management needed

2. **For non-US locations**: Use OpenWeatherMap or WeatherAPI
   - Global coverage
   - Simple API structure
   - Reasonable free tier for development

### Implementation Phases

#### Phase 1: Core API Service Implementation

1. Create a weather service interface in `src/weather_app/backend/services/weather_service.py`
   - Define a common interface for all weather providers
   - Implement provider detection/selection logic

2. Implement NWS API provider
   - Geocoding to lat/long
   - Points endpoint to grid mapping
   - Forecast retrieval
   - Error handling for out-of-US requests

3. Implement alternative API provider (OpenWeatherMap recommended)
   - API key configuration
   - Global weather data retrieval
   - Standardize response format to match our models

4. Create unified data models in `src/weather_app/backend/models/weather.py`
   - Current weather
   - Forecast (daily)
   - Hourly forecast
   - Alerts

#### Phase 2: Backend API Endpoints

1. Enhance the existing backend with new endpoints in `src/weather_app/backend/api/app.py`:
   - `/api/weather/current?location={location}` - Current weather
   - `/api/weather/forecast?location={location}` - 7-day forecast
   - `/api/weather/hourly?location={location}` - Hourly forecast
   - `/api/weather/alerts?location={location}` - Weather alerts

2. Implement comprehensive error handling:
   - Location not found
   - API service unavailable
   - Rate limiting
   - Invalid responses

3. Add caching layer to minimize API calls:
   - Cache results for 30-60 minutes
   - Implement cache invalidation strategy

#### Phase 3: Frontend Integration

1. Enhance location form component in `src/weather_app/frontend/components/location_form.py`
   - Add validation for locations
   - Implement geocoding support

2. Update existing display components:
   - `current_weather_display.py`
   - `forecast_display.py`
   - `hourly_forecast.py`
   - `wind_display.py`
   - `humidity_display.py`

3. Add new components for:
   - Weather alerts display
   - Location detection
   - Unit conversion (imperial/metric)

#### Phase 4: Testing and Validation

1. Unit tests for all API service implementations
   - Test US locations with NWS API
   - Test international locations with alternative API
   - Test error handling and edge cases

2. Integration tests for backend endpoints
   - End-to-end request testing
   - Response validation

3. Frontend component tests
   - UI rendering tests
   - Data processing tests

## Technical Implementation Details

### NWS API Implementation

```python
# Example code for NWS API implementation
class NWSWeatherProvider(WeatherProvider):
    BASE_URL = "https://api.weather.gov"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "(myweatherapp.com, contact@myweatherapp.com)",
            "Accept": "application/geo+json"
        })
    
    async def get_grid_data(self, lat, lon):
        """Get grid data for a location"""
        url = f"{self.BASE_URL}/points/{lat},{lon}"
        response = await self.fetch(url)
        return response.json()
    
    async def get_forecast(self, lat, lon):
        """Get forecast for a location using grid data"""
        grid_data = await self.get_grid_data(lat, lon)
        forecast_url = grid_data["properties"]["forecast"]
        response = await self.fetch(forecast_url)
        return self._transform_forecast(response.json())
    
    def _transform_forecast(self, nws_forecast):
        """Transform NWS forecast to our standard model"""
        # Transformation logic here
        return standardized_forecast
```

### Alternative API Implementation

```python
# Example code for OpenWeatherMap implementation
class OpenWeatherMapProvider(WeatherProvider):
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
    
    async def get_current_weather(self, lat, lon):
        """Get current weather for a location"""
        url = f"{self.BASE_URL}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = await self.fetch(url)
        return self._transform_current(response.json())
    
    async def get_forecast(self, lat, lon):
        """Get forecast for a location"""
        url = f"{self.BASE_URL}/forecast/daily?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = await self.fetch(url)
        return self._transform_forecast(response.json())
    
    def _transform_current(self, owm_current):
        """Transform OpenWeatherMap current data to our standard model"""
        # Transformation logic here
        return standardized_current
```

### Provider Selection Logic

```python
# Example code for provider selection
class WeatherService:
    def __init__(self, config):
        self.nws_provider = NWSWeatherProvider()
        self.global_provider = OpenWeatherMapProvider(config.get("openweathermap_api_key"))
        self.geocoder = GeocodingService()
    
    async def get_weather(self, location):
        """Get weather for a location using the appropriate provider"""
        lat, lon, country = await self.geocoder.geocode(location)
        
        # Use NWS for US locations
        if country == "US":
            try:
                return await self.nws_provider.get_current_weather(lat, lon)
            except Exception as e:
                # Fall back to global provider if NWS fails
                logger.warning(f"NWS API failed: {e}, falling back to global provider")
                return await self.global_provider.get_current_weather(lat, lon)
        else:
            # Use global provider for non-US locations
            return await self.global_provider.get_current_weather(lat, lon)
```

## Configuration and API Keys

1. Update configuration files to include API keys:
   - `src/weather_app/backend/config/config_development.json`
   - `src/weather_app/backend/config/config_production.json`

2. Ensure API keys are managed securely:
   - Use environment variables in production
   - Keep keys out of version control
   - Implement key rotation strategy

## Conclusion

This implementation plan provides a robust strategy for integrating weather data into our Streamlit application. The hybrid approach leverages the strengths of both the NWS API (authoritative US data) and a global weather API (worldwide coverage), while providing fallback mechanisms for reliability.

By following the phased implementation approach, we can incrementally build and test each component, ensuring a stable and user-friendly weather application.