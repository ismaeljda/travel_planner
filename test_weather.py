#!/usr/bin/env python3
"""Test the weather API integration"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Test weather API
api_key = os.getenv('OPENWEATHER_API_KEY', '622804b9c0f2b495e0142ffe73325074')
print(f"Using API key: {api_key[:10]}...")

# Test with Barcelona
city = "Barcelona"
base_url = "http://api.openweathermap.org/data/2.5/weather"

params = {
    'q': city,
    'appid': api_key,
    'units': 'metric',
    'lang': 'fr'
}

try:
    print(f"Testing weather for {city}...")
    response = requests.get(base_url, params=params, timeout=10)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        weather = response.json()
        print("SUCCESS: Weather API working!")
        print(f"Temperature: {weather['main']['temp']} C")
        print(f"Description: {weather['weather'][0]['description']}")
        print(f"Humidity: {weather['main']['humidity']}%")
        
        if 'wind' in weather:
            print(f"Wind: {weather['wind']['speed']} m/s")
        else:
            print("Wind: No data")
            
    else:
        print(f"ERROR {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*50)
print("If this works, the weather should appear in the web app!")
print("Make sure 'Inclure la météo' is checked when searching.")