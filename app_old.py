from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import requests
from ryanair import Ryanair
import threading
import json
from config import Config
from amadeus import Client, ResponseError

app = Flask(__name__)
app.config.from_object(Config)

# Import data from airport_themes.py
from airport_themes import (
    airports_by_country, THEMES,
    get_airports_by_countries, get_coastal_airports_by_countries, 
    get_airport_name, get_airport_info,
    get_airports_by_theme, get_airports_by_themes
)

class FlightSearchService:
    def __init__(self):
        self.ryanair = Ryanair()
    
    def search_flights(self, search_params):
        """Search for flights based on search parameters"""
        results = []
        
        departure_airports = search_params['departure_airports']
        departure_date_from = search_params['departure_date_from']
        departure_date_to = search_params['departure_date_to']
        min_stay_duration = search_params['min_stay_duration']
        
        # Get target destinations based on theme or countries
        if 'theme' in search_params and search_params['theme']:
            # Theme-based search
            target_destinations = get_airports_by_theme(search_params['theme'])
        else:
            # Traditional country-based search
            target_countries = search_params['target_countries']
            coastal_only = search_params.get('coastal_only', None)
            
            if coastal_only is True:
                target_destinations = get_coastal_airports_by_countries(target_countries, coastal_only=True)
            elif coastal_only is False:
                target_destinations = get_coastal_airports_by_countries(target_countries, coastal_only=False)
            else:
                target_destinations = get_airports_by_countries(target_countries)
        
        for origin in departure_airports:
            try:
                earliest_departure = datetime.strptime(departure_date_from, '%Y-%m-%d')
                latest_departure = datetime.strptime(departure_date_to, '%Y-%m-%d')
                
                return_date_from = (earliest_departure + timedelta(days=min_stay_duration)).strftime('%Y-%m-%d')
                return_date_to = (latest_departure + timedelta(days=min_stay_duration)).strftime('%Y-%m-%d')
                
                for destination in target_destinations:
                    try:
                        trips = self.ryanair.get_cheapest_return_flights(
                            origin, 
                            departure_date_from, 
                            departure_date_to, 
                            return_date_from, 
                            return_date_to, 
                            destination_airport=destination
                        )
                        
                        if trips:
                            for trip in trips:
                                # Create smart Ryanair booking link
                                booking_link = ryanair_link_service.create_booking_link(
                                    trip.outbound.origin,
                                    trip.outbound.destination,
                                    trip.outbound.departureTime,
                                    trip.inbound.departureTime
                                )
                                
                                results.append({
                                    'origin': trip.outbound.origin,
                                    'destination': trip.outbound.destination,
                                    'outbound_price': trip.outbound.price,
                                    'inbound_price': trip.inbound.price,
                                    'total_price': trip.totalPrice,
                                    'departure_time': trip.outbound.departureTime,
                                    'return_time': trip.inbound.departureTime,
                                    'origin_name': get_airport_name(trip.outbound.origin),
                                    'destination_info': get_airport_info(trip.outbound.destination),
                                    'ryanair_link': booking_link
                                })
                    except Exception as e:
                        continue
                        
            except Exception as e:
                continue
        
        # Sort by price
        results.sort(key=lambda x: x['total_price'])
        return results

class WeatherService:
    def __init__(self):
        self.api_key = app.config['OPENWEATHER_API_KEY']
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, airport_code):
        """Get weather for an airport location"""
        try:
            if not self.api_key or self.api_key == "your_openweather_api_key":
                return None
                
            airport_info = get_airport_info(airport_code)
            airport_name = airport_info['name']
            
            # Better city extraction from airport name
            city = self.extract_city_from_airport_name(airport_name, airport_code)
            
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'fr'
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def extract_city_from_airport_name(self, airport_name, airport_code):
        """Extract city name from airport name with better logic"""
        if not airport_name:
            return airport_code
            
        # Dictionary of known airport codes to city names
        airport_city_map = {
            'BCN': 'Barcelona', 'MAD': 'Madrid', 'PMI': 'Palma',
            'FCO': 'Rome', 'MXP': 'Milan', 'VCE': 'Venice',
            'CDG': 'Paris', 'ORY': 'Paris', 'NCE': 'Nice',
            'LIS': 'Lisbon', 'OPO': 'Porto', 'FAO': 'Faro',
            'ATH': 'Athens', 'SKG': 'Thessaloniki',
            'DUB': 'Dublin', 'ORK': 'Cork',
        }
        
        if airport_code in airport_city_map:
            return airport_city_map[airport_code]
        
        # Extract from airport name
        name_lower = airport_name.lower()
        
        # Remove common airport words
        remove_words = ['airport', 'international', 'airfield', 'aéroport', 'aeroporto']
        for word in remove_words:
            name_lower = name_lower.replace(word, '')
        
        # Take first significant word
        parts = [part.strip() for part in name_lower.split() if len(part.strip()) > 2]
        return parts[0].capitalize() if parts else airport_code

class RyanairLinkService:
    @staticmethod
    def create_booking_link(origin, destination, departure_date, return_date, adults=1):
        """Create a smart Ryanair booking link with pre-filled parameters"""
        base_url = "https://www.ryanair.com/fr/fr/trip/flights/select"
        
        # Format dates to YYYY-MM-DD
        if isinstance(departure_date, str):
            # Extract date from datetime string if needed
            dep_date = departure_date.split('T')[0] if 'T' in departure_date else departure_date.split(' ')[0]
        else:
            dep_date = departure_date
            
        if isinstance(return_date, str):
            ret_date = return_date.split('T')[0] if 'T' in return_date else return_date.split(' ')[0]
        else:
            ret_date = return_date
        
        params = {
            'adults': adults,
            'teens': 0,
            'children': 0,
            'infants': 0,
            'dateOut': dep_date,
            'dateIn': ret_date,
            'isConnectedFlight': 'false',
            'discount': 0,
            'promoCode': '',
            'isReturn': 'true',
            'originIata': origin,
            'destinationIata': destination,
            'tpAdults': adults,
            'tpTeens': 0,
            'tpChildren': 0,
            'tpInfants': 0,
            'tpStartDate': dep_date,
            'tpEndDate': ret_date,
            'tpDiscount': 0,
            'tpPromoCode': '',
            'tpOriginIata': origin,
            'tpDestinationIata': destination
        }
        
        # Build URL with parameters
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"

class GoogleHotelsService:
    def __init__(self):
        self.serpapi_key = app.config['SERPAPI_KEY']
        self.base_url = "https://serpapi.com/search.json"
    
    def search_hotels(self, destination, checkin_date, checkout_date, adults=2, **filters):
        """Search for hotels using SERP API Google Hotels"""
        try:
            # Extract city name from airport code
            airport_info = get_airport_info(destination)
            city_name = self._extract_city_from_airport(airport_info.get('name', ''))
            
            # Build SERP API parameters
            params = {
                'engine': 'google_hotels',
                'q': city_name,
                'check_in_date': checkin_date,
                'check_out_date': checkout_date,
                'adults': adults,
                'api_key': self.serpapi_key,
                'hl': 'fr',  # Language
                'gl': 'fr',  # Geolocation
                'no_cache': 'false',  # Enable caching for better performance
                'num': '100',  # Request more results (default is often 20-25)
                'start': '0'  # Starting position for results
            }
            
            # Add filters if provided
            if filters.get('price_min'):
                params['price_min'] = filters['price_min']
            if filters.get('price_max'):
                params['price_max'] = filters['price_max']
            if filters.get('hotel_class'):
                params['hotel_class'] = filters['hotel_class']
            if filters.get('free_cancellation'):
                params['free_cancellation'] = '1'
            # Note: Don't pass sort_by to SERP API as it limits results
            # We'll sort on our side after getting all results
            # if filters.get('sort'):
            #     params['sort_by'] = filters['sort']  # 8: lowest price, 1: highest rating
                
            print(f"DEBUG: Searching hotels for {city_name} with params: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"SERP API error: HTTP {response.status_code}")
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            data = response.json()
            
            if 'error' in data:
                print(f"SERP API error: {data['error']}")
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            hotels = []
            properties = data.get('properties', [])
            
            # Debug: Print full data structure to understand limitations
            print(f"DEBUG: SERP API response keys: {list(data.keys())}")
            print(f"DEBUG: Found {len(properties)} hotels from Google Hotels")
            
            # Check if there are pagination indicators
            has_more_pages = False
            if 'serpapi_pagination' in data:
                pagination = data['serpapi_pagination']
                print(f"DEBUG: Pagination available: {pagination}")
                has_more_pages = 'next' in pagination
            
            # Check total results if available
            total_available = None
            if 'search_information' in data:
                search_info = data['search_information']
                print(f"DEBUG: Search info: {search_info}")
                if 'total_results' in search_info:
                    total_available = search_info['total_results']
                    print(f"DEBUG: API says {total_available} total results available")
            
            for hotel in properties[:50]:  # Increased limit to get more results  
                # Try multiple price extraction methods
                rate_info = hotel.get('rate_per_night', {})
                if not rate_info:
                    # Try alternative price fields
                    rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                
                price_display = self._extract_price(rate_info)
                price_numeric = self._extract_price_numeric(rate_info)
                
                # If still no price, try extracting from raw data
                if not price_display and not price_numeric:
                    price_display = self._extract_price(hotel)
                    price_numeric = self._extract_price_numeric(hotel)
                
                hotel_data = {
                    'name': hotel.get('name', 'Hotel'),
                    'rating': hotel.get('overall_rating', 0),
                    'price': price_display,
                    'price_numeric': price_numeric,  # For sorting and filtering
                    'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                    'description': hotel.get('description', ''),
                    'amenities': hotel.get('amenities', [])[:5],  # Top 5 amenities
                    'booking_url': hotel.get('booking_link', ''),
                    'stars': self._extract_stars(hotel.get('hotel_class')),
                    'stars_display': hotel.get('hotel_class', ''),
                    'location_rating': hotel.get('location_rating', 0),
                    'reviews': hotel.get('reviews', 0),
                    'free_cancellation': hotel.get('free_cancellation', False),
                    'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                    'type': self._categorize_hotel(hotel),
                    'details_url': hotel.get('link', '')  # Link for more info
                }
                
                # Apply client-side hotel type filter
                if filters.get('hotel_type'):
                    filter_type = filters['hotel_type'].lower()
                    hotel_type = hotel_data['type'].lower()
                    
                    # Match filter with hotel type
                    if filter_type == 'hotel' and 'hotel' not in hotel_type and 'boutique' not in hotel_type:
                        continue
                    elif filter_type == 'hostel' and 'hostel' not in hotel_type:
                        continue
                    elif filter_type == 'resort' and 'resort' not in hotel_type:
                        continue
                    elif filter_type == 'apartment' and 'apartment' not in hotel_type:
                        continue
                    elif filter_type == 'boutique' and 'boutique' not in hotel_type:
                        continue
                
                # Apply price range filter (only if price is available)
                if filters.get('price_min') or filters.get('price_max'):
                    if hotel_data['price_numeric']:
                        price_num = hotel_data['price_numeric']
                        if filters.get('price_min') and price_num < int(filters['price_min']):
                            print(f"DEBUG: Filtering out {hotel_data['name']} - price {price_num} < {filters['price_min']}")
                            continue
                        if filters.get('price_max') and price_num > int(filters['price_max']):
                            print(f"DEBUG: Filtering out {hotel_data['name']} - price {price_num} > {filters['price_max']}")
                            continue
                    # If no price_numeric, keep hotel but note it
                    elif filters.get('price_min') or filters.get('price_max'):
                        print(f"DEBUG: Keeping {hotel_data['name']} without price for filtering")
                
                hotels.append(hotel_data)
            
            # Strategy: Try with different search parameters to get more variety
            if len(hotels) < 35:
                print("DEBUG: Attempting to get more hotels with different search strategies...")
                additional_hotels = self._get_additional_hotels_with_variants(base_params, city_name)
                
                # Add unique additional hotels
                existing_names = {h['name'] for h in hotels}
                added_count = 0
                for hotel in additional_hotels:
                    if hotel['name'] not in existing_names:
                        hotels.append(hotel)
                        existing_names.add(hotel['name'])
                        added_count += 1
                
                print(f"DEBUG: Added {added_count} additional unique hotels from variants")
            
            # Try to get more results if pagination is available and we have fewer than 40 hotels
            if has_more_pages and len(hotels) < 40:
                print("DEBUG: Attempting to get more results with pagination...")
                additional_hotels = self._get_paginated_results(params, city_name, has_more_pages, len(hotels))
                
                # Add unique additional hotels
                existing_names = {h['name'] for h in hotels}
                for hotel in additional_hotels:
                    if hotel['name'] not in existing_names:
                        hotels.append(hotel)
                        existing_names.add(hotel['name'])
                
                print(f"DEBUG: After pagination, total hotels: {len(hotels)}")
            
            # Apply sorting
            if filters.get('sort') == '8':  # Price ascending
                # Separate hotels with and without prices
                hotels_with_prices = [h for h in hotels if h['price_numeric']]
                hotels_without_prices = [h for h in hotels if not h['price_numeric']]
                # Sort hotels with prices by price, put hotels without prices at the end
                hotels_with_prices.sort(key=lambda x: x['price_numeric'])
                hotels = hotels_with_prices + hotels_without_prices
            elif filters.get('sort') == '1':  # Rating descending
                hotels.sort(key=lambda x: x['rating'] if x['rating'] else 0, reverse=True)
            
            return {
                'hotels': hotels,
                'total_results': len(hotels),
                'city': city_name,
                'search_params': params
            }
            
        except Exception as e:
            print(f"Google Hotels service error: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return self._get_fallback_hotels(city_name if 'city_name' in locals() else destination, checkin_date, checkout_date)
    
    def _extract_price(self, rate_info):
        """Extract price from rate information"""
        if not rate_info:
            return None
            
        print(f"DEBUG: Extracting price from: {rate_info}")  # Debug
            
        if isinstance(rate_info, dict):
            # Try different price fields in order of preference
            price_fields = [
                'lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 
                'total', 'price', 'rate', 'amount', 'cost', 'value'
            ]
            price = None
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info.get(field)
                    print(f"DEBUG: Found price in field '{field}': {price}")
                    break
                    
            if price:
                # Remove any existing currency symbols and convert to EUR
                price_str = str(price)
                # Handle unicode currency symbols
                price_clean = price_str.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '€').replace('\\u00a0', '').replace('€', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
                
                # Extract numbers from string
                import re
                numbers = re.findall(r'\d+\.?\d*', price_clean)
                if numbers:
                    try:
                        price_num = float(numbers[0])
                        # Convert from USD to EUR if USD detected
                        if '$' in price_str or 'US' in price_str or 'USD' in price_str:
                            price_num *= 0.85
                        print(f"DEBUG: Extracted price: {price_num}€")
                        return f"{int(price_num)}€"
                    except Exception as e:
                        print(f"DEBUG: Error parsing price {price}: {e}")
                        pass
            else:
                # Try to find any numeric values in the entire dict
                for key, value in rate_info.items():
                    if isinstance(value, (int, float)) and value > 0 and value < 10000:
                        price_num = float(value) * 0.85  # Assume USD and convert
                        print(f"DEBUG: Found fallback price in '{key}': {price_num}€")
                        return f"{int(price_num)}€"
                        
        elif isinstance(rate_info, str):
            # Handle string prices directly
            price_clean = rate_info.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
            import re
            numbers = re.findall(r'\d+\.?\d*', price_clean)
            if numbers:
                try:
                    price_num = float(numbers[0])
                    if '$' in rate_info or 'US' in rate_info or 'USD' in rate_info:
                        price_num *= 0.85
                    return f"{int(price_num)}€"
                except:
                    pass
        elif isinstance(rate_info, (int, float)) and rate_info > 0:
            # Handle numeric prices directly
            price_num = float(rate_info) * 0.85  # Assume USD
            return f"{int(price_num)}€"
        
        print(f"DEBUG: Could not extract price from: {rate_info}")  # Debug
        return None
    
    def _extract_price_numeric(self, rate_info):
        """Extract price as numeric value for filtering and sorting"""
        if not rate_info:
            return None
            
        if isinstance(rate_info, dict):
            price_fields = [
                'lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 
                'total', 'price', 'rate', 'amount', 'cost', 'value'
            ]
            price = None
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info.get(field)
                    break
                    
            if price:
                price_str = str(price)
                price_clean = price_str.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').strip()
                
                import re
                numbers = re.findall(r'\d+\.?\d*', price_clean)
                if numbers:
                    try:
                        price_num = float(numbers[0])
                        # Convert from USD to EUR if USD detected
                        if '$' in price_str or 'US' in price_str or 'USD' in price_str:
                            price_num *= 0.85
                        return int(price_num)
                    except:
                        pass
            else:
                # Try to find any numeric values in the entire dict
                for key, value in rate_info.items():
                    if isinstance(value, (int, float)) and value > 0 and value < 10000:
                        return int(float(value) * 0.85)  # Assume USD and convert
                        
        elif isinstance(rate_info, str):
            price_clean = rate_info.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
            import re
            numbers = re.findall(r'\d+\.?\d*', price_clean)
            if numbers:
                try:
                    price_num = float(numbers[0])
                    if '$' in rate_info or 'US' in rate_info or 'USD' in rate_info:
                        price_num *= 0.85
                    return int(price_num)
                except:
                    pass
        elif isinstance(rate_info, (int, float)) and rate_info > 0:
            # Handle numeric prices directly
            return int(float(rate_info) * 0.85)  # Assume USD
        
        return None
    
    def _get_paginated_results(self, base_params, city_name, has_more_pages, current_count):
        """Get additional hotel results using pagination"""
        additional_hotels = []
        page = 1
        max_pages = 3  # Limit to avoid excessive API calls
        
        while has_more_pages and page < max_pages and len(additional_hotels) < 30:
            try:
                # Create new params for next page
                paginated_params = base_params.copy()
                paginated_params['start'] = str(current_count + (page - 1) * 20)  # Offset for pagination
                
                print(f"DEBUG: Requesting page {page + 1} with start={paginated_params['start']}")
                
                response = requests.get(self.base_url, params=paginated_params, timeout=15)
                
                if response.status_code != 200:
                    print(f"DEBUG: Pagination request failed with status {response.status_code}")
                    break
                
                data = response.json()
                
                if 'error' in data:
                    print(f"DEBUG: Pagination error: {data['error']}")
                    break
                
                properties = data.get('properties', [])
                print(f"DEBUG: Page {page + 1} returned {len(properties)} hotels")
                
                if not properties:
                    break
                
                # Process hotels from this page
                for hotel in properties[:25]:  # Limit per page
                    rate_info = hotel.get('rate_per_night', {})
                    if not rate_info:
                        rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                    
                    price_display = self._extract_price(rate_info)
                    price_numeric = self._extract_price_numeric(rate_info)
                    
                    if not price_display and not price_numeric:
                        price_display = self._extract_price(hotel)
                        price_numeric = self._extract_price_numeric(hotel)
                    
                    hotel_data = {
                        'name': hotel.get('name', 'Hotel'),
                        'rating': hotel.get('overall_rating', 0),
                        'price': price_display,
                        'price_numeric': price_numeric,
                        'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                        'description': hotel.get('description', ''),
                        'amenities': hotel.get('amenities', [])[:5],
                        'booking_url': hotel.get('booking_link', ''),
                        'stars': self._extract_stars(hotel.get('hotel_class')),
                        'stars_display': hotel.get('hotel_class', ''),
                        'location_rating': hotel.get('location_rating', 0),
                        'reviews': hotel.get('reviews', 0),
                        'free_cancellation': hotel.get('free_cancellation', False),
                        'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                        'type': self._categorize_hotel(hotel),
                        'details_url': hotel.get('link', '')
                    }
                    
                    additional_hotels.append(hotel_data)
                
                # Check if more pages are available
                has_more_pages = 'serpapi_pagination' in data and 'next' in data['serpapi_pagination']
                page += 1
                
            except Exception as e:
                print(f"DEBUG: Pagination error on page {page}: {e}")
                break
        
        print(f"DEBUG: Pagination collected {len(additional_hotels)} additional hotels")
        return additional_hotels
    
    def _get_additional_hotels_with_variants(self, base_params, city_name):
        """Try different search parameters to get more hotel variety"""
        additional_hotels = []
        
        # Different search variants to try
        variants = [
            # Try with different geolocation
            {'gl': 'us', 'hl': 'en'},  # US perspective
            {'gl': 'uk', 'hl': 'en'},  # UK perspective
            
            # Try searching with broader location terms
            {'q': f"hotels near {city_name}"},
            {'q': f"{city_name} accommodation"},
            
            # Try with different currency/region settings
            {'gl': 'de', 'hl': 'de'},  # German perspective (EUR currency)
        ]
        
        for variant_index, variant in enumerate(variants):
            try:
                variant_params = base_params.copy()
                variant_params.update(variant)
                
                print(f"DEBUG: Trying variant {variant_index + 1}: {variant}")
                
                response = requests.get(self.base_url, params=variant_params, timeout=10)
                
                if response.status_code != 200:
                    print(f"DEBUG: Variant {variant_index + 1} failed with status {response.status_code}")
                    continue
                
                data = response.json()
                
                if 'error' in data:
                    print(f"DEBUG: Variant {variant_index + 1} error: {data['error']}")
                    continue
                
                properties = data.get('properties', [])
                print(f"DEBUG: Variant {variant_index + 1} returned {len(properties)} hotels")
                
                # Process hotels from this variant (limit to avoid too many)
                for hotel in properties[:15]:  # Limit per variant
                    rate_info = hotel.get('rate_per_night', {})
                    if not rate_info:
                        rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                    
                    price_display = self._extract_price(rate_info)
                    price_numeric = self._extract_price_numeric(rate_info)
                    
                    if not price_display and not price_numeric:
                        price_display = self._extract_price(hotel)
                        price_numeric = self._extract_price_numeric(hotel)
                    
                    hotel_data = {
                        'name': hotel.get('name', 'Hotel'),
                        'rating': hotel.get('overall_rating', 0),
                        'price': price_display,
                        'price_numeric': price_numeric,
                        'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                        'description': hotel.get('description', ''),
                        'amenities': hotel.get('amenities', [])[:5],
                        'booking_url': hotel.get('booking_link', ''),
                        'stars': self._extract_stars(hotel.get('hotel_class')),
                        'stars_display': hotel.get('hotel_class', ''),
                        'location_rating': hotel.get('location_rating', 0),
                        'reviews': hotel.get('reviews', 0),
                        'free_cancellation': hotel.get('free_cancellation', False),
                        'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                        'type': self._categorize_hotel(hotel),
                        'details_url': hotel.get('link', '')
                    }
                    
                    additional_hotels.append(hotel_data)
                
                # Don't overwhelm API - small delay between requests
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"DEBUG: Variant {variant_index + 1} exception: {e}")
                continue
        
        print(f"DEBUG: Variants collected {len(additional_hotels)} total additional hotels")
        return additional_hotels
    
    def _extract_stars(self, hotel_class_str):
        """Extract number of stars from hotel class string"""
        if not hotel_class_str:
            return 0
            
        import re
        # Look for patterns like "4 étoiles", "4-star", "4 star", etc.
        numbers = re.findall(r'(\d+)', str(hotel_class_str))
        if numbers:
            try:
                stars = int(numbers[0])
                if 1 <= stars <= 5:  # Valid star range
                    return stars
            except:
                pass
        return 0
    
    def _categorize_hotel(self, hotel_data):
        """Categorize hotel type based on data"""
        name = hotel_data.get('name', '').lower()
        
        if any(word in name for word in ['hostel', 'auberge', 'backpack']):
            return 'Hostel'
        elif any(word in name for word in ['resort', 'spa']):
            return 'Resort'
        elif any(word in name for word in ['apartment', 'appart', 'residence']):
            return 'Apartment'
        elif any(word in name for word in ['boutique', 'design']):
            return 'Boutique Hotel'
        else:
            return 'Hotel'
    
    def _extract_city_from_airport(self, airport_name):
        """Extract city name from airport name"""
        if not airport_name:
            return "City"
            
        name_lower = airport_name.lower()
        
        # Remove common airport words
        remove_words = ['airport', 'international', 'airfield', 'aéroport', 'aeroporto', '-', 'charles', 'de', 'gaulle']
        for word in remove_words:
            name_lower = name_lower.replace(word, ' ')
        
        # Split and get meaningful parts
        parts = [part.strip() for part in name_lower.split() if len(part.strip()) > 2]
        if parts:
            # Return the first meaningful city name
            return parts[0].title()
        return "City"
    
    def _get_fallback_hotels(self, city_name, checkin_date, checkout_date):
        """Fallback when SERP API fails"""
        return {
            'hotels': [],
            'booking_links': [
                {
                    'name': 'Booking.com',
                    'url': f"https://www.booking.com/searchresults.html?ss={city_name}&checkin={checkin_date}&checkout={checkout_date}",
                    'type': 'booking_platform'
                },
                {
                    'name': 'Hotels.com', 
                    'url': f"https://www.hotels.com/search.do?q-destination={city_name}&q-check-in={checkin_date}&q-check-out={checkout_date}",
                    'type': 'hotel_platform'
                }
            ],
            'total_results': 0,
            'city': city_name
        }

class AccommodationService:
    def __init__(self):
        # Booking.com API key (alternative to Hostelworld)
        self.booking_api_key = "YOUR_BOOKING_API_KEY"
        self.google_hotels_api_key = "YOUR_GOOGLE_HOTELS_API_KEY"
    
    def search_accommodations(self, destination, checkin_date, checkout_date):
        """Search for accommodations using web scraping or available APIs"""
        accommodations = {
            'hostels': [],
            'hotels': []
        }
        
        try:
            # Alternative: Use Booking.com API or web scraping
            # For now, return suggested booking links
            airport_info = get_airport_info(destination)
            city_name = self.extract_city_from_airport(airport_info['name'])
            
            accommodations['booking_links'] = [
                {
                    'name': 'Booking.com',
                    'url': f"https://www.booking.com/searchresults.html?ss={city_name}&checkin={checkin_date}&checkout={checkout_date}",
                    'type': 'booking_platform'
                },
                {
                    'name': 'Hostelworld',
                    'url': f"https://www.hostelworld.com/search?search_text={city_name}&date_from={checkin_date}&date_to={checkout_date}",
                    'type': 'hostel_platform'
                },
                {
                    'name': 'Airbnb',
                    'url': f"https://www.airbnb.com/s/{city_name}",
                    'type': 'apartment_platform'
                }
            ]
            
            return accommodations
            
        except Exception as e:
            print(f"Error searching accommodations: {e}")
            return accommodations
    
    def extract_city_from_airport(self, airport_name):
        """Extract city name from airport name"""
        if not airport_name:
            return ""
        # Simple extraction - take first word before "Airport"
        parts = airport_name.split()
        for i, part in enumerate(parts):
            if 'Airport' in part or 'International' in part:
                return ' '.join(parts[:i]) if i > 0 else parts[0]
        return parts[0] if parts else ""

class AmadeusActivitiesService:
    def __init__(self):
        self.amadeus = Client(
            client_id=app.config['AMADEUS_API_KEY'],
            client_secret=app.config['AMADEUS_API_SECRET']
        )
        
        # Mapping aéroports vers coordonnées principales des villes
        self.airport_coordinates = {
            'BCN': (41.3851, 2.1734),    # Barcelona
            'MAD': (40.4168, -3.7038),  # Madrid
            'PMI': (39.5696, 2.6502),   # Palma
            'FCO': (41.9028, 12.4964),  # Rome
            'VCE': (45.4408, 12.3155),  # Venice
            'MXP': (45.4642, 8.7064),   # Milan
            'NAP': (40.8518, 14.2681),  # Naples
            'CDG': (48.8566, 2.3522),   # Paris
            'NCE': (43.7102, 7.2620),   # Nice
            'LIS': (38.7223, -9.1393),  # Lisbon
            'OPO': (41.1579, -8.6291),  # Porto
            'ATH': (37.9755, 23.7348),  # Athens
            'SKG': (40.6401, 22.9444),  # Thessaloniki
            'DUB': (53.3498, -6.2603),  # Dublin
            'STN': (51.5074, -0.1278),  # London
            'LTN': (51.5074, -0.1278),  # London
            'LGW': (51.5074, -0.1278),  # London
            'AMS': (52.3676, 4.9041),   # Amsterdam
            'BER': (52.5200, 13.4050),  # Berlin
            'MUC': (48.1351, 11.5820),  # Munich
            'PRG': (50.0755, 14.4378),  # Prague
            'BUD': (47.4979, 19.0402),  # Budapest
            'WAW': (52.2297, 21.0122),  # Warsaw
            'VIE': (48.2082, 16.3738),  # Vienna
            'ZUR': (47.3769, 8.5417),   # Zurich
            'CPH': (55.6761, 12.5683),  # Copenhagen
            'OSL': (59.9139, 10.7522),  # Oslo
            'ARN': (59.3293, 18.0686),  # Stockholm
        }
    
    def get_airport_coordinates(self, airport_code):
        """Get coordinates for airport or city"""
        return self.airport_coordinates.get(airport_code, None)
    
    def get_activities_for_destination(self, airport_code, theme=None, full_fetch=False):
        """Get activities suggestions for a destination based on theme - 100% dynamic"""
        # For search results, return quick activities to avoid slowing down
        if not full_fetch:
            return self._get_quick_activities_preview(airport_code)
            
        try:
            # For destination pages, use full dynamic APIs
            dynamic_activities = self._get_dynamic_activities(airport_code, theme)
            if dynamic_activities:
                return dynamic_activities
                
        except Exception as e:
            print(f"Dynamic API error: {e}")
            
        # Last resort: minimal fallback
        return self._generate_minimal_fallback_activities(airport_code)
    
    def _get_quick_activities_preview(self, airport_code):
        """Get a quick preview of activities for search results without API calls"""
        airport_info = get_airport_info(airport_code)
        city_name = self._extract_city_name_from_airport(airport_info.get('name', ''))
        
        # Return a few generic but realistic activities quickly
        preview_activities = {
            'culture': [
                {'name': f'Sites historiques de {city_name}', 'category': 'culture', 'subcategory': 'monuments', 'rating': 8.2, 'price_range': '€', 'description': 'Découverte du patrimoine local'}
            ],
            'gastronomie': [
                {'name': f'Restaurants locaux à {city_name}', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 8.0, 'price_range': '€€', 'description': 'Spécialités culinaires régionales'}
            ],
            'nature': [
                {'name': f'Espaces verts de {city_name}', 'category': 'nature', 'subcategory': 'parcs', 'rating': 7.8, 'price_range': 'Gratuit', 'description': 'Parcs et jardins pour se détendre'}
            ]
        }
        
        if airport_info.get('coastal', False):
            preview_activities['detente'] = [
                {'name': f'Côte de {city_name}', 'category': 'detente', 'subcategory': 'plage', 'rating': 8.4, 'price_range': 'Gratuit', 'description': 'Plages et front de mer'}
            ]
            
        return preview_activities
    
    def _get_amadeus_activities(self, airport_code):
        """Try to get activities from Amadeus Tours and Activities API"""
        try:
            coordinates = self.get_airport_coordinates(airport_code)
            if not coordinates:
                return []
            
            latitude, longitude = coordinates
            
            # Try Tours and Activities API instead
            response = self.amadeus.shopping.activities.get(
                latitude=latitude,
                longitude=longitude
            )
            
            activities = []
            if response.data:
                for activity in response.data:
                    activity_data = {
                        'name': activity.get('name', 'Activité'),
                        'category': self._categorize_amadeus_activity(activity),
                        'subcategory': self._get_amadeus_subcategory(activity),
                        'rating': activity.get('rating', {}).get('value', 0),
                        'price_range': self._convert_price_to_range(activity.get('price', {})),
                        'description': activity.get('description', ''),
                        'bookingLink': activity.get('bookingLink', ''),
                        'pictures': activity.get('pictures', [])
                    }
                    activities.append(activity_data)
            
            return activities
            
        except ResponseError as error:
            print(f"Amadeus Tours API error: {error}")
            return []
        except Exception as e:
            print(f"Amadeus service error: {e}")
            return []
    
    def _get_static_activities(self, airport_code, theme=None):
        """Get curated static activities for popular destinations with extensive database"""
        # Static activities database removed - 100% dynamic system now
        # Legacy method redirected to minimal fallback
        return self._generate_minimal_fallback_activities(airport_code)
    
    def _old_get_static_activities_removed(self, airport_code, theme=None):
        """REMOVED: Static database for 100% dynamic system"""
        static_activities = {
            'BCN': {
                'gastronomie': [
                    {'name': 'Tapas Tour Born District', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 9.1, 'price_range': '€€', 'description': 'Découverte des meilleurs bars à tapas du quartier historique'},
                    {'name': 'Marché La Boquería', 'category': 'gastronomie', 'subcategory': 'street_food', 'rating': 8.8, 'price_range': '€', 'description': 'Marché emblématique avec produits frais et spécialités locales'},
                    {'name': 'Cal Pep', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 9.3, 'price_range': '€€€', 'description': 'Restaurant de fruits de mer réputé'},
                    {'name': 'Cooking Class Paella', 'category': 'gastronomie', 'subcategory': 'experiences_culinaires', 'rating': 8.9, 'price_range': '€€', 'description': 'Cours de cuisine paella avec chef local'}
                ],
                'culture': [
                    {'name': 'Sagrada Família', 'category': 'culture', 'subcategory': 'monuments', 'rating': 9.2, 'price_range': '€€', 'description': 'Chef-d\'œuvre de Gaudí, symbole de Barcelone'},
                    {'name': 'Musée Picasso', 'category': 'culture', 'subcategory': 'musees', 'rating': 8.4, 'price_range': '€€', 'description': 'Collection exceptionnelle des œuvres de jeunesse de Picasso'},
                    {'name': 'Quartier Gothique', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 8.5, 'price_range': 'Gratuit', 'description': 'Déambulation dans les ruelles médiévales'},
                    {'name': 'Palau de la Música Catalana', 'category': 'culture', 'subcategory': 'spectacles', 'rating': 9.0, 'price_range': '€€€', 'description': 'Concert dans une salle art nouveau magnifique'}
                ],
                'nature': [
                    {'name': 'Park Güell', 'category': 'nature', 'subcategory': 'parcs', 'rating': 8.8, 'price_range': '€', 'description': 'Parc artistique de Gaudí avec vue panoramique'},
                    {'name': 'Plage Barceloneta', 'category': 'nature', 'subcategory': 'excursions', 'rating': 8.0, 'price_range': 'Gratuit', 'description': 'Plage urbaine animée en bord de Méditerranée'},
                    {'name': 'Montjuïc', 'category': 'nature', 'subcategory': 'randonnees', 'rating': 8.2, 'price_range': 'Gratuit', 'description': 'Colline avec jardins, musées et points de vue'},
                    {'name': 'Kayak Costa Brava', 'category': 'nature', 'subcategory': 'activites_sportives', 'rating': 8.6, 'price_range': '€€', 'description': 'Excursion en kayak le long de la côte sauvage'}
                ],
                'loisirs': [
                    {'name': 'Las Ramblas Shopping', 'category': 'loisirs', 'subcategory': 'shopping', 'rating': 7.5, 'price_range': '€€', 'description': 'Avenue piétonne avec boutiques et artistes de rue'},
                    {'name': 'Opium Barcelona', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 8.7, 'price_range': '€€€', 'description': 'Club de plage avec terrasse sur la mer'},
                    {'name': 'Festival Primavera Sound', 'category': 'loisirs', 'subcategory': 'festivals', 'rating': 9.2, 'price_range': '€€€€', 'description': 'Festival de musique internationale (mai-juin)'},
                    {'name': 'Escape Room Gothic', 'category': 'loisirs', 'subcategory': 'experiences_insolites', 'rating': 8.3, 'price_range': '€€', 'description': 'Jeu d\'évasion dans le quartier gothique'}
                ],
                'detente': [
                    {'name': 'Aire de Barcelona Spa', 'category': 'detente', 'subcategory': 'spa', 'rating': 8.9, 'price_range': '€€€', 'description': 'Bains arabes dans un cadre historique'},
                    {'name': 'Plage Mar Bella', 'category': 'detente', 'subcategory': 'plage', 'rating': 7.8, 'price_range': 'Gratuit', 'description': 'Plage plus tranquille avec espaces naturistes'},
                    {'name': 'Café Central', 'category': 'detente', 'subcategory': 'cafes_tranquilles', 'rating': 8.1, 'price_range': '€', 'description': 'Café historique avec terrasse dans le Born'},
                    {'name': 'Parc de la Ciutadella', 'category': 'detente', 'subcategory': 'spots_tranquilles', 'rating': 8.0, 'price_range': 'Gratuit', 'description': 'Grand parc urbain parfait pour se reposer'}
                ]
            },
            'FCO': {
                'gastronomie': [
                    {'name': 'Trastevere Food Tour', 'category': 'gastronomie', 'subcategory': 'food_tour', 'rating': 9.1, 'price_range': '€€', 'description': 'Découverte culinaire dans le quartier bohème'},
                    {'name': 'Marché Campo de\' Fiori', 'category': 'gastronomie', 'subcategory': 'street_food', 'rating': 8.5, 'price_range': '€', 'description': 'Marché historique avec produits frais le matin'},
                    {'name': 'Da Enzo al 29', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 9.2, 'price_range': '€€', 'description': 'Trattoria authentique sans menu touristique'},
                    {'name': 'Cours de Cuisine Romaine', 'category': 'gastronomie', 'subcategory': 'experiences_culinaires', 'rating': 8.8, 'price_range': '€€€', 'description': 'Apprentissage des pâtes fraîches et recettes traditionnelles'}
                ],
                'culture': [
                    {'name': 'Colisée & Forum Romain', 'category': 'culture', 'subcategory': 'monuments', 'rating': 9.5, 'price_range': '€€', 'description': 'Amphithéâtre emblématique et centre de l\'Empire romain'},
                    {'name': 'Musées du Vatican', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.8, 'price_range': '€€€', 'description': 'Chapelle Sixtine et collections pontificales'},
                    {'name': 'Quartier du Trastevere', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 8.7, 'price_range': 'Gratuit', 'description': 'Quartier médiéval authentique avec ruelles pavées'},
                    {'name': 'Opéra de Rome', 'category': 'culture', 'subcategory': 'spectacles', 'rating': 9.0, 'price_range': '€€€€', 'description': 'Programmation lyrique dans un cadre somptueux'}
                ],
                'nature': [
                    {'name': 'Villa Borghese', 'category': 'nature', 'subcategory': 'parcs', 'rating': 8.6, 'price_range': 'Gratuit', 'description': 'Parc central avec galerie d\'art et lac'},
                    {'name': 'Thermes de Caracalla', 'category': 'nature', 'subcategory': 'sites_historiques', 'rating': 8.9, 'price_range': '€€', 'description': 'Ruines monumentales des bains romains'},
                    {'name': 'Ostia Antica', 'category': 'nature', 'subcategory': 'excursions', 'rating': 8.4, 'price_range': '€€', 'description': 'Cité antique préservée près de Rome'},
                    {'name': 'Vélo sur la Via Appia', 'category': 'nature', 'subcategory': 'activites_sportives', 'rating': 8.2, 'price_range': '€', 'description': 'Parcours cyclable sur l\'ancienne voie romaine'}
                ]
            },
            'CDG': {
                'gastronomie': [
                    {'name': 'Tour Gastronomique Marais', 'category': 'gastronomie', 'subcategory': 'food_tour', 'rating': 9.0, 'price_range': '€€€', 'description': 'Découverte des spécialités du quartier historique'},
                    {'name': 'Marché des Enfants Rouges', 'category': 'gastronomie', 'subcategory': 'street_food', 'rating': 8.7, 'price_range': '€€', 'description': 'Plus ancien marché couvert de Paris'},
                    {'name': 'L\'Ami Jean', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 9.1, 'price_range': '€€€', 'description': 'Bistrot parisien authentique et convivial'},
                    {'name': 'École de Cuisine Alain Ducasse', 'category': 'gastronomie', 'subcategory': 'experiences_culinaires', 'rating': 9.5, 'price_range': '€€€€', 'description': 'Cours de cuisine française haut de gamme'}
                ],
                'culture': [
                    {'name': 'Musée du Louvre', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.4, 'price_range': '€€', 'description': 'Plus grand musée du monde avec la Joconde'},
                    {'name': 'Cathédrale Notre-Dame', 'category': 'culture', 'subcategory': 'monuments', 'rating': 9.2, 'price_range': 'Gratuit', 'description': 'Chef-d\'œuvre gothique au cœur de Paris'},
                    {'name': 'Montmartre', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 8.9, 'price_range': 'Gratuit', 'description': 'Quartier des artistes avec Sacré-Cœur'},
                    {'name': 'Opéra Garnier', 'category': 'culture', 'subcategory': 'spectacles', 'rating': 9.3, 'price_range': '€€€€', 'description': 'Opéra somptueux du 19ème siècle'}
                ]
            },
            'AMS': {
                'gastronomie': [
                    {'name': 'Cheese & Stroopwafel Tour', 'category': 'gastronomie', 'subcategory': 'food_tour', 'rating': 8.9, 'price_range': '€€', 'description': 'Dégustation des spécialités néerlandaises'},
                    {'name': 'Foodhallen', 'category': 'gastronomie', 'subcategory': 'street_food', 'rating': 8.4, 'price_range': '€€', 'description': 'Hall gastronomique avec cuisines du monde'},
                    {'name': 'Restaurant Greetje', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 9.0, 'price_range': '€€€', 'description': 'Cuisine néerlandaise moderne et créative'}
                ],
                'culture': [
                    {'name': 'Rijksmuseum', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.2, 'price_range': '€€', 'description': 'Art et histoire des Pays-Bas, Rembrandt et Vermeer'},
                    {'name': 'Van Gogh Museum', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.0, 'price_range': '€€', 'description': 'Plus grande collection au monde de Van Gogh'},
                    {'name': 'Jordaan District', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 8.6, 'price_range': 'Gratuit', 'description': 'Quartier pittoresque avec canaux et cafés bruns'}
                ],
                'loisirs': [
                    {'name': 'Red Light District', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 7.9, 'price_range': 'Variable', 'description': 'Quartier historique et nocturne emblématique'},
                    {'name': 'Coffee Shops Tour', 'category': 'loisirs', 'subcategory': 'experiences_insolites', 'rating': 8.0, 'price_range': '€€', 'description': 'Découverte de la culture cannabis locale'},
                    {'name': 'Croisière sur les Canaux', 'category': 'loisirs', 'subcategory': 'experiences_insolites', 'rating': 8.7, 'price_range': '€€', 'description': 'Navigation dans les canaux UNESCO'}
                ]
            },
            'BER': {
                'culture': [
                    {'name': 'Île aux Musées', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.2, 'price_range': '€€', 'description': 'Complexe de 5 musées UNESCO'},
                    {'name': 'Porte de Brandebourg', 'category': 'culture', 'subcategory': 'monuments', 'rating': 9.0, 'price_range': 'Gratuit', 'description': 'Symbole de Berlin et de la réunification'},
                    {'name': 'East Side Gallery', 'category': 'culture', 'subcategory': 'monuments', 'rating': 8.9, 'price_range': 'Gratuit', 'description': 'Vestige du Mur de Berlin transformé en galerie d\'art'}
                ],
                'loisirs': [
                    {'name': 'Berghain', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 9.1, 'price_range': '€€', 'description': 'Club techno légendaire ouvert du samedi au lundi'},
                    {'name': 'Watergate', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 8.8, 'price_range': '€€', 'description': 'Club électro avec terrasse sur la Spree'},
                    {'name': 'Hackescher Markt', 'category': 'loisirs', 'subcategory': 'shopping', 'rating': 8.4, 'price_range': '€€', 'description': 'Quartier branché avec boutiques et bars'}
                ]
            },
            'PMI': {
                'nature': [
                    {'name': 'Cala Mondragó', 'category': 'nature', 'subcategory': 'excursions', 'rating': 9.0, 'price_range': 'Gratuit', 'description': 'Parc naturel avec criques paradisiaques'},
                    {'name': 'Sa Dragonera', 'category': 'nature', 'subcategory': 'excursions', 'rating': 8.7, 'price_range': '€', 'description': 'Île protégée avec sentiers de randonnée'},
                    {'name': 'Kayak Grottes Bleues', 'category': 'nature', 'subcategory': 'activites_sportives', 'rating': 8.9, 'price_range': '€€', 'description': 'Exploration des grottes marines en kayak'}
                ],
                'detente': [
                    {'name': 'Cala Varques', 'category': 'detente', 'subcategory': 'plage', 'rating': 9.2, 'price_range': 'Gratuit', 'description': 'Crique sauvage accessible à pied'},
                    {'name': 'Hammam Al Ándalus', 'category': 'detente', 'subcategory': 'spa', 'rating': 8.8, 'price_range': '€€€', 'description': 'Bains arabes dans le centre de Palma'}
                ]
            },
            'DUB': {
                'gastronomie': [
                    {'name': 'Temple Bar Food Tour', 'category': 'gastronomie', 'subcategory': 'food_tour', 'rating': 8.9, 'price_range': '€€', 'description': 'Dégustation des spécialités irlandaises dans le quartier historique'},
                    {'name': 'Guinness Storehouse', 'category': 'gastronomie', 'subcategory': 'experiences_culinaires', 'rating': 8.7, 'price_range': '€€', 'description': 'Musée et dégustation de la célèbre bière irlandaise'},
                    {'name': 'The Brazen Head', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 8.5, 'price_range': '€€', 'description': 'Plus ancien pub de Dublin (1198) avec musique traditionnelle'},
                    {'name': 'Irish Whiskey Museum', 'category': 'gastronomie', 'subcategory': 'experiences_culinaires', 'rating': 8.6, 'price_range': '€€', 'description': 'Dégustation comparative de whiskies irlandais'}
                ],
                'culture': [
                    {'name': 'Trinity College & Book of Kells', 'category': 'culture', 'subcategory': 'musees', 'rating': 9.2, 'price_range': '€€', 'description': 'Université historique et manuscrit enluminé du IXe siècle'},
                    {'name': 'Château de Dublin', 'category': 'culture', 'subcategory': 'monuments', 'rating': 8.4, 'price_range': '€€', 'description': 'Ancienne résidence du pouvoir britannique en Irlande'},
                    {'name': 'Cathédrale St Patrick', 'category': 'culture', 'subcategory': 'monuments', 'rating': 8.7, 'price_range': '€', 'description': 'Plus grande cathédrale d\'Irlande, lieu de sépulture de Jonathan Swift'},
                    {'name': 'Musée National d\'Irlande', 'category': 'culture', 'subcategory': 'musees', 'rating': 8.8, 'price_range': 'Gratuit', 'description': 'Archéologie irlandaise et trésors celtiques'},
                    {'name': 'Spectacle de Danse Irlandaise', 'category': 'culture', 'subcategory': 'spectacles', 'rating': 8.9, 'price_range': '€€€', 'description': 'Riverdance ou Celtic Nights dans les théâtres dublinois'}
                ],
                'nature': [
                    {'name': 'Phoenix Park', 'category': 'nature', 'subcategory': 'parcs', 'rating': 8.6, 'price_range': 'Gratuit', 'description': 'Un des plus grands parcs urbains d\'Europe avec zoo'},
                    {'name': 'Howth Peninsula', 'category': 'nature', 'subcategory': 'excursions', 'rating': 9.1, 'price_range': 'Gratuit', 'description': 'Randonnée côtière avec vues spectaculaires sur Dublin Bay'},
                    {'name': 'Jardins Botaniques de Dublin', 'category': 'nature', 'subcategory': 'parcs', 'rating': 8.3, 'price_range': 'Gratuit', 'description': 'Jardins historiques avec serres victoriennes'},
                    {'name': 'Dalkey Island', 'category': 'nature', 'subcategory': 'excursions', 'rating': 8.7, 'price_range': '€', 'description': 'Île accessible en bateau avec ruines médiévales'}
                ],
                'loisirs': [
                    {'name': 'Temple Bar District', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 8.8, 'price_range': '€€', 'description': 'Quartier animé avec pubs traditionnels et musique live'},
                    {'name': 'Grafton Street Shopping', 'category': 'loisirs', 'subcategory': 'shopping', 'rating': 8.2, 'price_range': '€€', 'description': 'Rue piétonne principale avec boutiques et artistes de rue'},
                    {'name': 'Dublin Literary Pub Crawl', 'category': 'loisirs', 'subcategory': 'vie_nocturne', 'rating': 9.0, 'price_range': '€€', 'description': 'Tour des pubs fréquentés par Joyce, Wilde et autres écrivains'},
                    {'name': 'Marché de Temple Bar', 'category': 'loisirs', 'subcategory': 'shopping', 'rating': 8.1, 'price_range': '€', 'description': 'Marché alimentaire le samedi, artisanat le dimanche'}
                ],
                'detente': [
                    {'name': 'St Stephen\'s Green', 'category': 'detente', 'subcategory': 'spots_tranquilles', 'rating': 8.4, 'price_range': 'Gratuit', 'description': 'Parc victorien au cœur de la ville, parfait pour une pause'},
                    {'name': 'Dublin Bay Promenade', 'category': 'detente', 'subcategory': 'spots_tranquilles', 'rating': 8.6, 'price_range': 'Gratuit', 'description': 'Promenade en bord de mer de Dun Laoghaire à Howth'},
                    {'name': 'Bewley\'s Café', 'category': 'detente', 'subcategory': 'cafes_tranquilles', 'rating': 8.0, 'price_range': '€', 'description': 'Café historique sur Grafton Street, institution dublinoise'},
                    {'name': 'The Shelbourne Afternoon Tea', 'category': 'detente', 'subcategory': 'cafes_tranquilles', 'rating': 8.9, 'price_range': '€€€', 'description': 'Thé traditionnel dans le palace historique face à St Stephen\'s Green'}
                ]
            }
        }
        
        # Get activities for the destination
        destination_activities = static_activities.get(airport_code, {})
        if destination_activities:
            # Return all activities organized by category
            return destination_activities
        
        # Fallback for destinations not in our database
        return self._generate_generic_activities(airport_code, theme)
    
    def _generate_generic_activities(self, airport_code, theme=None):
        """Generate minimal fallback activities only when Amadeus completely fails"""
        airport_info = get_airport_info(airport_code)
        city_name = self._extract_city_name_from_airport(airport_info.get('name', ''))
        
        # Only return very basic activities as last resort
        generic_activities = {
            'culture': [
                {'name': f'Visite de {city_name}', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 7.5, 'price_range': 'Gratuit', 'description': f'Découverte du centre-ville de {city_name}'}
            ]
        }
        
        if airport_info.get('coastal', False):
            generic_activities['nature'] = [
                {'name': f'Côte de {city_name}', 'category': 'nature', 'subcategory': 'excursions', 'rating': 7.8, 'price_range': 'Gratuit', 'description': 'Exploration du littoral'}
            ]
        
        return generic_activities
    
    def _get_dynamic_activities(self, airport_code, theme=None):
        """Get activities using free dynamic APIs (Wikipedia + OpenStreetMap)"""
        airport_info = get_airport_info(airport_code)
        city_name = self._extract_city_name_from_airport(airport_info.get('name', ''))
        coordinates = self.get_airport_coordinates(airport_code)
        
        activities = {}
        
        try:
            # Get places of interest from OpenStreetMap Overpass API
            osm_activities = self._fetch_osm_activities(city_name, coordinates)
            activities.update(osm_activities)
            print(f"DEBUG: OSM returned {sum(len(v) for v in osm_activities.values()) if osm_activities else 0} activities for {city_name}")
            
            # Get cultural sites from Wikipedia
            wiki_activities = self._fetch_wikipedia_activities(city_name)
            activities.update(wiki_activities)
            print(f"DEBUG: Wikipedia returned {sum(len(v) for v in wiki_activities.values()) if wiki_activities else 0} activities for {city_name}")
            
            # If we got activities, categorize and enhance them
            if activities:
                total_activities = sum(len(v) for v in activities.values())
                print(f"DEBUG: Total dynamic activities for {city_name}: {total_activities}")
                return activities
                
        except Exception as e:
            print(f"Error fetching dynamic activities: {e}")
            import traceback
            traceback.print_exc()
            
        return {}
    
    def _fetch_osm_activities(self, city_name, coordinates):
        """Fetch points of interest from OpenStreetMap Overpass API"""
        if not coordinates:
            return {}
            
        lat, lon = coordinates
        radius = 15000  # 15km radius
        
        # Overpass query to get various POIs
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:10];
        (
          node["tourism"~"^(museum|attraction|gallery|zoo|theme_park|viewpoint)$"](around:{radius},{lat},{lon});
          node["amenity"~"^(restaurant|cafe|pub|bar|fast_food)$"]["name"](around:{radius},{lat},{lon});
          node["leisure"~"^(park|garden|nature_reserve|beach)$"]["name"](around:{radius},{lat},{lon});
          node["shop"~"^(mall|department_store|market)$"]["name"](around:{radius},{lat},{lon});
          node["historic"~"^(monument|castle|church|cathedral)$"]["name"](around:{radius},{lat},{lon});
        );
        out body;
        """
        
        try:
            response = requests.post(overpass_url, data={'data': overpass_query}, timeout=10)
            
            if response.status_code != 200:
                print(f"OSM API HTTP error: {response.status_code}")
                return {}
                
            if not response.text.strip():
                print("OSM API returned empty response")
                return {}
                
            data = response.json()
            
            activities = {
                'gastronomie': [],
                'culture': [],
                'nature': [],
                'loisirs': [],
                'detente': []
            }
            
            elements = data.get('elements', [])[:100]  # Limit to first 100 results for performance
            
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name', 'Lieu d\'intérêt')
                
                if not name or len(name) < 3:
                    continue
                    
                # Stop if we have enough activities total
                total_activities = sum(len(v) for v in activities.values())
                if total_activities >= 40:  # Maximum 40 total activities
                    break
                    
                activity = {
                    'name': name,
                    'rating': round(7.0 + (hash(name) % 20) / 10, 1),  # Random but consistent rating 7.0-8.9
                    'price_range': self._guess_price_range(tags),
                    'description': self._generate_description(name, tags)
                }
                
                # Categorize based on OSM tags
                category = self._categorize_osm_activity(tags)
                if category and category in activities:
                    activity['category'] = category
                    activity['subcategory'] = self._get_osm_subcategory(tags)
                    activities[category].append(activity)
                    
                    # Limit activities per category for optimal UX
                    if len(activities[category]) >= 8:
                        continue
                        
            return {k: v for k, v in activities.items() if v}  # Remove empty categories
            
        except Exception as e:
            print(f"OSM API error: {e}")
            return {}
    
    def _fetch_wikipedia_activities(self, city_name):
        """Fetch cultural activities from Wikipedia"""
        try:
            # Wikipedia API to get page extracts about the city
            wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + city_name.replace(' ', '_')
            response = requests.get(wiki_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                
                # Extract notable places mentioned
                culture_activities = []
                
                # Common cultural keywords to look for
                cultural_keywords = [
                    'museum', 'cathedral', 'church', 'castle', 'palace', 'gallery',
                    'theater', 'theatre', 'opera house', 'university', 'college',
                    'monument', 'square', 'bridge', 'historic', 'heritage'
                ]
                
                words = extract.split()
                for i, word in enumerate(words):
                    for keyword in cultural_keywords:
                        if keyword.lower() in word.lower():
                            # Try to extract the name (usually nearby words)
                            context = ' '.join(words[max(0, i-3):i+4])
                            if len(context) > 10:
                                activity = {
                                    'name': context.split('.')[0].strip()[:50],
                                    'category': 'culture',
                                    'subcategory': 'monuments' if keyword in ['monument', 'castle', 'bridge'] else 'musees',
                                    'rating': round(7.5 + (hash(context) % 15) / 10, 1),
                                    'price_range': '€€' if keyword in ['museum', 'gallery', 'opera'] else 'Gratuit',
                                    'description': f"Site culturel emblématique de {city_name}"
                                }
                                culture_activities.append(activity)
                                break
                                
                if culture_activities:
                    return {'culture': culture_activities[:4]}  # Max 4 from Wikipedia
                    
        except Exception as e:
            print(f"Wikipedia API error: {e}")
            
        return {}
    
    def _categorize_osm_activity(self, tags):
        """Categorize OSM activity based on tags"""
        if 'amenity' in tags:
            amenity = tags['amenity']
            if amenity in ['restaurant', 'cafe', 'pub', 'bar', 'fast_food']:
                return 'gastronomie'
        elif 'tourism' in tags:
            tourism = tags['tourism']
            if tourism in ['museum', 'gallery']:
                return 'culture'
            elif tourism in ['attraction', 'viewpoint']:
                return 'nature'
        elif 'leisure' in tags:
            leisure = tags['leisure']
            if leisure in ['park', 'garden', 'nature_reserve']:
                return 'nature'
            elif leisure in ['beach']:
                return 'detente'
        elif 'shop' in tags:
            return 'loisirs'
        elif 'historic' in tags:
            return 'culture'
            
        return None
    
    def _get_osm_subcategory(self, tags):
        """Get subcategory from OSM tags"""
        if 'amenity' in tags:
            amenity = tags['amenity']
            if amenity in ['restaurant', 'fast_food']:
                return 'restaurants_locaux'
            elif amenity in ['cafe']:
                return 'cafes_tranquilles'
            elif amenity in ['pub', 'bar']:
                return 'vie_nocturne'
        elif 'tourism' in tags:
            if tags['tourism'] == 'museum':
                return 'musees'
            elif tags['tourism'] in ['attraction', 'viewpoint']:
                return 'excursions'
        elif 'leisure' in tags:
            if tags['leisure'] in ['park', 'garden']:
                return 'parcs'
        elif 'shop' in tags:
            return 'shopping'
        elif 'historic' in tags:
            return 'monuments'
            
        return 'autres'
    
    def _guess_price_range(self, tags):
        """Guess price range based on OSM tags"""
        if 'amenity' in tags:
            amenity = tags['amenity']
            if amenity == 'fast_food':
                return '€'
            elif amenity in ['restaurant', 'pub']:
                return '€€'
            elif amenity in ['cafe', 'bar']:
                return '€'
        elif 'tourism' in tags:
            tourism = tags['tourism']
            if tourism in ['museum', 'gallery']:
                return '€€'
            elif tourism in ['viewpoint', 'attraction']:
                return 'Gratuit'
        elif 'leisure' in tags:
            return 'Gratuit'
        elif 'historic' in tags:
            return 'Gratuit'
            
        return '€'
    
    def _generate_description(self, name, tags):
        """Generate description based on OSM tags"""
        if 'amenity' in tags:
            amenity = tags['amenity']
            if amenity == 'restaurant':
                return f"Restaurant local recommandé à {name}"
            elif amenity == 'cafe':
                return f"Café accueillant parfait pour une pause"
            elif amenity == 'pub':
                return f"Pub traditionnel avec ambiance locale"
        elif 'tourism' in tags:
            tourism = tags['tourism']
            if tourism == 'museum':
                return f"Musée incontournable avec collections uniques"
            elif tourism == 'attraction':
                return f"Attraction touristique populaire"
            elif tourism == 'viewpoint':
                return f"Point de vue panoramique exceptionnel"
        elif 'leisure' in tags:
            leisure = tags['leisure']
            if leisure in ['park', 'garden']:
                return f"Espace vert paisible pour se détendre"
        elif 'historic' in tags:
            return f"Site historique emblématique du patrimoine local"
            
        return f"Lieu d'intérêt à découvrir"
    
    def _generate_minimal_fallback_activities(self, airport_code):
        """Generate minimal fallback activities using city name"""
        airport_info = get_airport_info(airport_code)
        city_name = self._extract_city_name_from_airport(airport_info.get('name', ''))
        
        return {
            'culture': [
                {'name': f'Centre historique de {city_name}', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 7.5, 'price_range': 'Gratuit', 'description': f'Exploration du patrimoine architectural'}
            ],
            'gastronomie': [
                {'name': f'Cuisine locale de {city_name}', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 7.8, 'price_range': '€€', 'description': 'Découverte des spécialités régionales'}
            ],
            'nature': [
                {'name': f'Environs naturels de {city_name}', 'category': 'nature', 'subcategory': 'excursions', 'rating': 7.6, 'price_range': 'Gratuit', 'description': 'Exploration des espaces naturels environnants'}
            ]
        }
    
    def _extract_city_name_from_airport(self, airport_name):
        """Extract city name from airport name"""
        if not airport_name:
            return "la ville"
        
        # Remove common airport-related words
        city_name = airport_name.lower()
        remove_words = ['airport', 'international', 'airfield', 'aéroport', 'aeroporto']
        for word in remove_words:
            city_name = city_name.replace(word, '')
        
        # Take first significant word
        parts = [part.strip() for part in city_name.split() if len(part.strip()) > 2]
        return parts[0].capitalize() if parts else "la ville"
    
    def _determine_activity_type(self, name, category):
        """Determine activity type from name and category"""
        name_lower = name.lower()
        category_lower = category.lower()
        
        if any(word in name_lower for word in ['restaurant', 'café', 'bar', 'food']):
            return 'restaurant'
        elif any(word in name_lower for word in ['museum', 'gallery', 'art', 'culture']):
            return 'culture'
        elif any(word in name_lower for word in ['beach', 'plage', 'sea']):
            return 'beach'
        elif any(word in name_lower for word in ['club', 'bar', 'nightlife', 'disco']):
            return 'nightlife'
        elif any(word in name_lower for word in ['park', 'garden', 'nature', 'outdoor']):
            return 'nature'
        elif any(word in name_lower for word in ['shop', 'market', 'store']):
            return 'shopping'
        else:
            return 'sights'
    
    def categorize_activity(self, category, tags):
        """Categorize activity type"""
        category_lower = category.lower()
        tags_lower = [tag.lower() for tag in tags]
        
        if 'restaurant' in category_lower or 'food' in category_lower:
            return 'restaurant'
        elif 'museum' in category_lower or 'art' in category_lower:
            return 'culture'
        elif 'beach' in category_lower or any('beach' in tag for tag in tags_lower):
            return 'beach'
        elif 'nightlife' in category_lower or 'bar' in category_lower:
            return 'nightlife'
        elif 'outdoor' in category_lower or 'park' in category_lower:
            return 'nature'
        elif 'shopping' in category_lower:
            return 'shopping'
        else:
            return 'sights'
    
    def matches_theme(self, activity, theme):
        """Check if activity matches the selected theme"""
        activity_type = activity['type']
        
        theme_mappings = {
            'couple': ['culture', 'restaurant', 'sights'],
            'party': ['nightlife', 'restaurant', 'shopping'],
            'beach': ['beach', 'nature', 'restaurant'],
            'nature': ['nature', 'sights'],
            'mountain': ['nature', 'sights'],
            'city_trip': ['culture', 'shopping', 'sights', 'restaurant']
        }
        
        return activity_type in theme_mappings.get(theme, [])
    
    def _categorize_amadeus_activity(self, activity):
        """Categorize Amadeus activity into our main categories"""
        name = activity.get('name', '').lower()
        category = activity.get('category', '').lower()
        tags = [tag.lower() for tag in activity.get('tags', [])]
        
        # Check for food/restaurant activities
        if any(word in name or word in category for word in ['restaurant', 'food', 'cuisine', 'gastronom']):
            return 'gastronomie'
        elif any(word in tags for word in ['food', 'restaurant', 'culinary']):
            return 'gastronomie'
            
        # Check for cultural activities
        elif any(word in name or word in category for word in ['museum', 'gallery', 'art', 'culture', 'monument', 'historic']):
            return 'culture'
        elif any(word in tags for word in ['culture', 'art', 'museum', 'historic']):
            return 'culture'
            
        # Check for nature activities
        elif any(word in name or word in category for word in ['nature', 'outdoor', 'park', 'garden', 'hiking', 'beach']):
            return 'nature'
        elif any(word in tags for word in ['nature', 'outdoor', 'beach', 'park']):
            return 'nature'
            
        # Check for leisure activities
        elif any(word in name or word in category for word in ['shopping', 'nightlife', 'bar', 'club', 'entertainment']):
            return 'loisirs'
        elif any(word in tags for word in ['shopping', 'nightlife', 'entertainment']):
            return 'loisirs'
            
        # Check for wellness activities
        elif any(word in name or word in category for word in ['spa', 'wellness', 'relaxation', 'massage']):
            return 'detente'
        elif any(word in tags for word in ['spa', 'wellness', 'relaxation']):
            return 'detente'
            
        # Default to culture for sights and general activities
        else:
            return 'culture'
    
    def _get_amadeus_subcategory(self, activity):
        """Get specific subcategory for Amadeus activity"""
        name = activity.get('name', '').lower()
        category = activity.get('category', '').lower()
        
        # Gastronomie subcategories
        if 'restaurant' in name or 'restaurant' in category:
            return 'restaurants_locaux'
        elif 'market' in name or 'food tour' in name:
            return 'food_tour'
        elif 'cooking' in name or 'culinary' in name:
            return 'experiences_culinaires'
            
        # Culture subcategories
        elif 'museum' in name or 'gallery' in name:
            return 'musees'
        elif 'monument' in name or 'historic' in name:
            return 'monuments'
        elif 'show' in name or 'concert' in name or 'theater' in name:
            return 'spectacles'
            
        # Nature subcategories
        elif 'park' in name or 'garden' in name:
            return 'parcs'
        elif 'hiking' in name or 'walking' in name:
            return 'randonnees'
        elif 'tour' in name or 'excursion' in name:
            return 'excursions'
        elif 'sport' in name or 'activity' in name:
            return 'activites_sportives'
            
        # Default subcategory
        return 'experiences_insolites'
    
    def _convert_price_to_range(self, price_info):
        """Convert Amadeus price to our price range format"""
        if not price_info or 'amount' not in price_info:
            return '€'
        
        try:
            amount = float(price_info['amount'])
            if amount < 20:
                return '€'
            elif amount < 50:
                return '€€'
            elif amount < 100:
                return '€€€'
            else:
                return '€€€€'
        except:
            return '€'
    
    def _organize_amadeus_activities(self, activities):
        """Organize Amadeus activities by category"""
        organized = {
            'gastronomie': [],
            'culture': [],
            'nature': [],
            'loisirs': [],
            'detente': []
        }
        
        for activity in activities:
            category = activity.get('category', 'culture')
            if category in organized:
                organized[category].append(activity)
        
        return organized
    
    def _apply_filters(self, activities_data, filters):
        """Apply filters to activities data"""
        if not filters:
            return activities_data
        
        # If activities_data is organized by category (dict)
        if isinstance(activities_data, dict):
            filtered_data = {}
            
            # Category filters
            if 'categories' in filters and filters['categories']:
                for category in filters['categories']:
                    if category in activities_data:
                        filtered_data[category] = activities_data[category]
            else:
                filtered_data = activities_data.copy()
            
            # Price range filter
            if 'price_range' in filters and filters['price_range']:
                for category in filtered_data:
                    filtered_data[category] = [
                        activity for activity in filtered_data[category]
                        if activity.get('price_range', '') in filters['price_range']
                    ]
            
            # Rating filter
            if 'min_rating' in filters and filters['min_rating']:
                min_rating = float(filters['min_rating'])
                for category in filtered_data:
                    filtered_data[category] = [
                        activity for activity in filtered_data[category]
                        if activity.get('rating', 0) >= min_rating
                    ]
            
            return filtered_data
        
        # If activities_data is a list
        else:
            filtered_activities = activities_data
            
            if 'categories' in filters and filters['categories']:
                filtered_activities = [
                    activity for activity in filtered_activities
                    if activity.get('category', '') in filters['categories']
                ]
            
            return filtered_activities
    
    def get_activity_icons_by_category(self):
        """Get icons mapping for activity categories and subcategories"""
        return {
            'gastronomie': {
                'icon': '🍽️',
                'subcategories': {
                    'restaurants_locaux': '🍽️',
                    'street_food': '🌭',
                    'bars_cafes': '☕',
                    'experiences_culinaires': '👨‍🍳',
                    'food_tour': '🍽️'
                }
            },
            'culture': {
                'icon': '🏛️',
                'subcategories': {
                    'musees': '🏛️',
                    'monuments': '🏴',
                    'quartiers_traditionnels': '🏘️',
                    'spectacles': '🎭'
                }
            },
            'nature': {
                'icon': '🌳',
                'subcategories': {
                    'parcs': '🌳',
                    'randonnees': '🥾',
                    'excursions': '🗺️',
                    'activites_sportives': '🏄'
                }
            },
            'loisirs': {
                'icon': '🛍️',
                'subcategories': {
                    'shopping': '🛍️',
                    'festivals': '🎉',
                    'experiences_insolites': '🌭',
                    'vie_nocturne': '🍻'
                }
            },
            'detente': {
                'icon': '🧘',
                'subcategories': {
                    'spa': '🧘',
                    'plage': '🏖️',
                    'cafes_tranquilles': '☕',
                    'spots_tranquilles': '🌿'
                }
            },
            'logistique': {
                'icon': '🚗',
                'subcategories': {
                    'transports': '🚆',
                    'tours_guides': '👥',
                    'excursions_journee': '🗺️',
                    'spots_photo': '📷'
                }
            }
        }
    
    def get_activity_icon(self, category, subcategory=None):
        """Get icon for activity category and subcategory"""
        icons = self.get_activity_icons_by_category()
        if category in icons:
            if subcategory and subcategory in icons[category]['subcategories']:
                return icons[category]['subcategories'][subcategory]
            return icons[category]['icon']
        return '📍'

# Initialize services
flight_service = FlightSearchService()
weather_service = WeatherService()
accommodation_service = AccommodationService()
google_hotels_service = GoogleHotelsService()
ryanair_link_service = RyanairLinkService()
activities_service = AmadeusActivitiesService()

@app.route('/')
def index():
    """Landing page with themes"""
    return render_template('landing.html')

@app.route('/search')
def search():
    """Search page with theme support"""
    theme = request.args.get('theme')
    return render_template('search.html', 
                         countries=airports_by_country,
                         themes=THEMES,
                         selected_theme=theme)

@app.route('/destination/<airport_code>')
def destination_page(airport_code):
    """Detailed destination page with activities and information - can be accessed with or without flight data"""
    
    # Check if we have flight data from search results
    has_flight_data = request.args.get('origin') is not None
    
    if has_flight_data:
        # Coming from search results - show flight info
        flight_data = {
            'origin': request.args.get('origin'),
            'destination': airport_code,
            'departure_time': request.args.get('departure_time'),
            'return_time': request.args.get('return_time'),
            'total_price': request.args.get('total_price'),
            'outbound_price': request.args.get('outbound_price'),
            'inbound_price': request.args.get('inbound_price'),
            'ryanair_link': request.args.get('ryanair_link')
        }
        origin_name = get_airport_name(flight_data['origin']) if flight_data['origin'] else ''
    else:
        # Direct access to destination page
        flight_data = None
        origin_name = ''
    
    theme = request.args.get('theme')
    
    # Get destination info
    destination_info = get_airport_info(airport_code)
    
    # Get weather
    weather = None
    try:
        weather = weather_service.get_weather(airport_code)
    except:
        pass
    
    # Get full activities for destination page with dynamic APIs
    all_activities = activities_service.get_activities_for_destination(airport_code, theme, full_fetch=True)
    
    # Get accommodation suggestions - handle dates safely
    checkin_date = ''
    checkout_date = ''
    
    if has_flight_data and flight_data.get('departure_time'):
        departure_time = flight_data.get('departure_time')
        if departure_time:
            checkin_date = departure_time.split('T')[0]
    if has_flight_data and flight_data.get('return_time'):
        return_time = flight_data.get('return_time')
        if return_time:
            checkout_date = return_time.split('T')[0]
    
    accommodations = accommodation_service.search_accommodations(
        airport_code,
        checkin_date,
        checkout_date
    )
    
    return render_template('destination.html',
                         flight=flight_data,
                         destination_info=destination_info,
                         origin_name=origin_name,
                         weather=weather,
                         activities=all_activities,
                         accommodations=accommodations,
                         theme=theme,
                         themes=THEMES,
                         has_flight_data=has_flight_data,
                         airport_code=airport_code)

@app.route('/api/airports/<country_code>')
def get_airports(country_code):
    """Get airports for a specific country"""
    if country_code in airports_by_country:
        return jsonify(airports_by_country[country_code]['airports'])
    return jsonify({})

@app.route('/api/search', methods=['POST'])
def search_flights():
    """Search for flights"""
    try:
        search_params = request.json
        
        # Validate required parameters
        if 'theme' in search_params and search_params['theme']:
            # Theme-based search: target_countries is optional
            required_params = ['departure_airports', 'departure_date_from', 'departure_date_to', 'min_stay_duration']
        else:
            # Traditional search: target_countries is required
            required_params = ['departure_airports', 'target_countries', 'departure_date_from', 'departure_date_to', 'min_stay_duration']
        
        for param in required_params:
            if param not in search_params:
                return jsonify({'error': f'Missing parameter: {param}'}), 400
        
        # Search flights
        results = flight_service.search_flights(search_params)
        
        # Add weather information if requested
        if search_params.get('include_weather', False):
            print(f"DEBUG: Adding weather info for {len(results)} results")
            for result in results:
                weather = weather_service.get_weather(result['destination'])
                result['weather'] = weather
                if weather:
                    print(f"DEBUG: Weather for {result['destination']}: {weather['main']['temp']}°C")
                else:
                    print(f"DEBUG: No weather data for {result['destination']}")
        
        # Add accommodation information if requested
        if search_params.get('include_accommodations', False):
            for result in results:
                accommodations = accommodation_service.search_accommodations(
                    result['destination'],
                    result['departure_time'][:10],  # Extract date
                    result['return_time'][:10]
                )
                result['accommodations'] = accommodations
        
        # Add activities information if requested
        if search_params.get('include_activities', False):
            print(f"DEBUG: Adding activities info for {len(results)} results")
            
            # Extract activity filters from search params
            activity_filters = {}
            if 'activity_categories' in search_params and search_params['activity_categories']:
                activity_filters['categories'] = search_params['activity_categories']
            if 'activity_price_range' in search_params and search_params['activity_price_range']:
                activity_filters['price_range'] = search_params['activity_price_range']
            if 'activity_min_rating' in search_params and search_params['activity_min_rating']:
                activity_filters['min_rating'] = search_params['activity_min_rating']
            
            for result in results:
                activities = activities_service.get_activities_for_destination(
                    result['destination'],
                    activity_filters if activity_filters else None
                )
                result['activities'] = activities
                if activities:
                    if isinstance(activities, dict):
                        total_activities = sum(len(cat_activities) for cat_activities in activities.values())
                        print(f"DEBUG: Found {total_activities} activities for {result['destination']} across {len(activities)} categories")
                    else:
                        print(f"DEBUG: Found {len(activities)} activities for {result['destination']}")
        
        return jsonify({
            'success': True,
            'results': results[:50],  # Limit to 50 results
            'total_found': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<airport_code>')
def get_weather_for_airport(airport_code):
    """Get weather for a specific airport"""
    weather = weather_service.get_weather(airport_code)
    if weather:
        return jsonify(weather)
    return jsonify({'error': 'Weather not found'}), 404

@app.route('/api/accommodations/<destination>')
def get_accommodations(destination):
    """Get accommodations for a destination"""
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    
    if not checkin or not checkout:
        return jsonify({'error': 'Checkin and checkout dates required'}), 400
    
    accommodations = accommodation_service.search_accommodations(destination, checkin, checkout)
    return jsonify(accommodations)

@app.route('/api/activities/<destination>')
def get_activities(destination):
    """Get activities for a destination with filtering options"""
    try:
        # Extract filter parameters
        filters = {}
        
        # Category filter
        categories = request.args.getlist('categories')
        if categories:
            filters['categories'] = categories
        
        # Price range filter  
        price_ranges = request.args.getlist('price_range')
        if price_ranges:
            filters['price_range'] = price_ranges
            
        # Minimum rating filter
        min_rating = request.args.get('min_rating')
        if min_rating:
            filters['min_rating'] = float(min_rating)
        
        # Get activities with filters
        activities = activities_service.get_activities_for_destination(destination, filters)
        
        # Add icon information
        icons = activities_service.get_activity_icons_by_category()
        
        return jsonify({
            'success': True,
            'activities': activities,
            'icons': icons
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity-categories')
def get_activity_categories():
    """Get available activity categories with icons and subcategories"""
    categories = {
        'gastronomie': {
            'name': 'Gastronomie',
            'description': 'Restaurants locaux, street food, marchés, expériences culinaires',
            'subcategories': {
                'restaurants_locaux': 'Restaurants locaux',
                'street_food': 'Street food / marchés', 
                'bars_cafes': 'Bars, cafés, salons de thé',
                'experiences_culinaires': 'Expériences culinaires',
                'food_tour': 'Food tour'
            }
        },
        'culture': {
            'name': 'Culture & Histoire', 
            'description': 'Musées, galeries, monuments, sites historiques',
            'subcategories': {
                'musees': 'Musées, galeries',
                'monuments': 'Monuments, sites historiques',
                'quartiers_traditionnels': 'Quartiers traditionnels',
                'spectacles': 'Spectacles (théâtre, opéra, danse, musique)'
            }
        },
        'nature': {
            'name': 'Nature & Aventure',
            'description': 'Parcs, jardins, randonnées, activités sportives',
            'subcategories': {
                'parcs': 'Parcs, jardins',
                'randonnees': 'Randonnées, balades à vélo',
                'excursions': 'Excursions (mer, montagne, désert, etc.)',
                'activites_sportives': 'Activités sportives'
            }
        },
        'loisirs': {
            'name': 'Loisirs & Vie locale',
            'description': 'Shopping, festivals, événements locaux, vie nocturne',
            'subcategories': {
                'shopping': 'Shopping (boutiques, marchés artisanaux)',
                'festivals': 'Festivals, événements locaux',
                'experiences_insolites': 'Expériences insolites',
                'vie_nocturne': 'Vie nocturne (clubs, concerts, rooftops)'
            }
        },
        'detente': {
            'name': 'Bien-être & Détente',
            'description': 'Spa, massages, plage, retraites',
            'subcategories': {
                'spa': 'Spa, massages',
                'plage': 'Plage, piscines',
                'cafes_tranquilles': 'Cafés / spots tranquilles pour se poser',
                'spots_tranquilles': 'Retraites (yoga, méditation)'
            }
        }
    }
    
    icons = activities_service.get_activity_icons_by_category()
    
    return jsonify({
        'categories': categories,
        'icons': icons
    })

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
        result = google_hotels_service.search_hotels(
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
    """Page récapitulative du séjour"""
    return render_template('recap.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)