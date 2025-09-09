# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application that searches for cheap Ryanair flights between airports across Europe. The application provides a user-friendly web interface for searching flights by theme (beach, city trip, party, etc.) or by specific countries.

## Dependencies

- `flask` - Web framework
- `ryanair` - Python package for accessing Ryanair flight data  
- `requests` - For API calls
- `python-dotenv` - For environment variables
- Other dependencies in requirements.txt

## Running the Project

```bash
python app.py
```

The application will start on http://localhost:5000

## Code Architecture

The project is now organized into clean, modular files:

### Main Files:
- `app.py` - Main Flask application with routes
- `config.py` - Configuration settings and environment variables
- `airport_themes.py` - Airport data organized by country and themes

### Services Directory:
- `services/flight_service.py` - FlightSearchService for searching Ryanair flights
- `services/weather_service.py` - WeatherService for airport weather data
- `services/ryanair_service.py` - RyanairLinkService for generating booking links

### Templates & Static:
- `templates/` - HTML templates for the web interface
- `static/` - CSS, JavaScript, and image files

### Legacy Files:
- `app_old.py` - Original large app.py (kept as backup with hotel/activity services)

## Configuration

Environment variables should be set in `.env`:
- `OPENWEATHER_API_KEY` - For weather data
- `SERPAPI_KEY` - For hotel search (if using complex services)
- `API_KEY` and `API_SECRET` - For Amadeus activities API

## Error Handling

The application includes comprehensive error handling for API failures and gracefully continues searching even when individual routes fail.