"""
Google Hotels Service for searching hotels using SERP API
"""
import requests
import re
import time
from airport_themes import get_airport_info


class GoogleHotelsService:
    def __init__(self, config):
        """
        Initialize the Google Hotels Service
        
        Args:
            config: Configuration object containing API keys
        """
        self.serpapi_key = config.get('SERPAPI_KEY')
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
                additional_hotels = self._get_additional_hotels_with_variants(params, city_name)
                
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