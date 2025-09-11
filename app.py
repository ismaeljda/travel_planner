from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import requests
import threading
import json

from config import Config
from services import (
    FlightSearchService, WeatherService, RyanairLinkService,
    AccommodationService, AmadeusActivitiesService, GoogleHotelsService
)

# Import data from airport_themes.py
from airport_themes import (
    airports_by_country, THEMES,
    get_airports_by_countries, get_coastal_airports_by_countries, 
    get_airport_name, get_airport_info,
    get_airports_by_theme, get_airports_by_themes
)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
flight_service = FlightSearchService()
weather_service = WeatherService(app.config['OPENWEATHER_API_KEY'])
hotel_service = GoogleHotelsService(app.config)
accommodation_service = AccommodationService()
activities_service = AmadeusActivitiesService(app.config)


@app.route('/')
def index():
    return render_template('landing_minimal.html', countries=airports_by_country, themes=THEMES)


@app.route('/search')
def search():
    return render_template('search_modern.html', countries=airports_by_country, themes=THEMES)


@app.route('/search-advanced')
def search_advanced():
    return render_template('index.html', countries=airports_by_country, themes=THEMES)


@app.route('/results')
def results():
    return render_template('results.html')


@app.route('/destination/<airport_code>')
def destination_page(airport_code):
    airport_info = get_airport_info(airport_code)
    return render_template('destination.html', 
                         airport_code=airport_code,
                         airport_info=airport_info,
                         destination_info=airport_info,  # Alias pour compatibilité template
                         themes=THEMES)


@app.route('/api/airports/<country_code>')
def get_airports(country_code):
    if country_code in airports_by_country:
        return jsonify(airports_by_country[country_code]['airports'])
    return jsonify({})


@app.route('/api/search', methods=['POST'])
def search_flights():
    try:
        data = request.json
        
        # Parse search parameters
        search_params = {
            'departure_airports': data.get('departure_airports', []),
            'departure_date_from': data.get('departure_date_from'),
            'departure_date_to': data.get('departure_date_to'),
            'min_stay_duration': int(data.get('min_stay_duration', 4)),
            'theme': data.get('theme')
        }
        
        # Add country-based search if no theme
        if not search_params['theme']:
            search_params.update({
                'target_countries': data.get('target_countries', []),
                'coastal_only': data.get('coastal_only')
            })
        
        # Search flights
        results = flight_service.search_flights(search_params)
        
        # Add weather data if requested
        include_weather = data.get('include_weather', False)
        if include_weather and results:
            for flight in results:
                weather_data = weather_service.get_weather(flight['destination'])
                if weather_data:
                    flight['weather'] = weather_data
        
        return jsonify({
            'success': True,
            'results': results[:50],  # Limit to top 50 results
            'total_found': len(results)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/weather/<airport_code>')
def get_weather_for_airport(airport_code):
    weather_data = weather_service.get_weather(airport_code)
    if weather_data:
        return jsonify({'success': True, 'weather': weather_data})
    return jsonify({'success': False, 'error': 'Weather data unavailable'})


@app.route('/api/accommodations/<destination>')
def get_accommodations(destination):
    try:
        checkin_date = request.args.get('checkin_date')
        checkout_date = request.args.get('checkout_date')
        
        if not checkin_date or not checkout_date:
            return jsonify({'success': False, 'error': 'Missing checkin_date or checkout_date'})
            
        results = accommodation_service.search_accommodations(destination, checkin_date, checkout_date)
        return jsonify({'success': True, 'accommodations': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/activities/<destination>')
def get_activities(destination):
    try:
        theme = request.args.get('theme')
        full_fetch = request.args.get('full_fetch', 'false').lower() == 'true'
        
        activities = activities_service.get_activities_for_destination(
            destination, 
            theme=theme, 
            full_fetch=full_fetch
        )
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/activity-categories')
def get_activity_categories():
    return jsonify(THEMES)


@app.route('/api/hotels/search')
def search_hotels():
    """Search for hotels using Google Hotels via SERP API"""
    try:
        # Get search parameters
        destination = request.args.get('destination')
        checkin_date = request.args.get('checkin')
        checkout_date = request.args.get('checkout')
        adults = int(request.args.get('adults', 2))
        
        if not all([destination, checkin_date, checkout_date]):
            return jsonify({'error': 'Missing required parameters: destination, checkin, checkout'}), 400
        
        # Get filter parameters
        filters = {}
        if request.args.get('price_min'):
            filters['price_min'] = int(request.args.get('price_min'))
        if request.args.get('price_max'):
            filters['price_max'] = int(request.args.get('price_max'))
        if request.args.get('hotel_class'):
            filters['hotel_class'] = request.args.get('hotel_class')
        if request.args.get('hotel_type'):
            filters['hotel_type'] = request.args.get('hotel_type')
        if request.args.get('free_cancellation') == 'true':
            filters['free_cancellation'] = True
        if request.args.get('sort'):
            filters['sort'] = request.args.get('sort')
        
        # Search hotels
        result = hotel_service.search_hotels(
            destination, checkin_date, checkout_date, adults, **filters
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"Hotel search API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/recap')
def trip_recap():
    return render_template('recap.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)