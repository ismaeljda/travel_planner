import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from airport_themes import get_airport_info


class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
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