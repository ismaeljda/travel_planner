import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # API Keys - These need to be obtained from respective services
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or 'your_openweather_api_key'
    BOOKING_API_KEY = os.environ.get('BOOKING_API_KEY') or 'your_booking_api_key'
    GOOGLE_HOTELS_API_KEY = os.environ.get('GOOGLE_HOTELS_API_KEY') or 'your_google_hotels_api_key'
    
    # Amadeus API Keys
    AMADEUS_API_KEY = os.environ.get('API_KEY') or 'your_amadeus_api_key'
    AMADEUS_API_SECRET = os.environ.get('API_SECRET') or 'your_amadeus_api_secret'
    
    # SERP API for Google Hotels
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY') or 'your_serpapi_key'
    
    # Cache settings
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3600))  # 1 hour default
    
    # Rate limiting
    RATE_LIMIT = os.environ.get('RATE_LIMIT', '100 per hour')
    
    # Debug mode
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'