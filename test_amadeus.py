#!/usr/bin/env python3
"""Test the Amadeus API integration"""

import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()

# Test Amadeus API
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

print(f"Testing Amadeus API...")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print(f"API Secret: {api_secret[:10]}...{api_secret[-4:]}")

try:
    # Create Amadeus client
    amadeus = Client(
        client_id=api_key,
        client_secret=api_secret
    )
    
    # Test with Barcelona coordinates
    latitude = 41.3851
    longitude = 2.1734
    
    print(f"\nTesting Points of Interest for Barcelona ({latitude}, {longitude})...")
    
    response = amadeus.reference_data.locations.points_of_interest.get(
        latitude=latitude,
        longitude=longitude,
        radius=30  # 30km radius
    )
    
    print(f"Status: {response.status_code}")
    
    if response.data:
        print(f"SUCCESS: Found {len(response.data)} points of interest!")
        print("\nFirst 5 activities:")
        
        for i, poi in enumerate(response.data[:5]):
            name = poi.get('name', 'Unknown')
            category = poi.get('category', 'Unknown')
            tags = poi.get('tags', [])
            relevance = poi.get('relevance', 0)
            
            print(f"{i+1}. {name}")
            print(f"   Category: {category}")
            print(f"   Tags: {', '.join(tags) if tags else 'None'}")
            print(f"   Relevance: {relevance}")
            print()
            
    else:
        print("No data returned")
        
except ResponseError as error:
    print(f"ERROR: Amadeus API error: {error}")
    print(f"Status: {error.response.status_code}")
    print(f"Response: {error.response.body}")
    
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*50)
print("If this works, activities should appear in the web app!")
print("Make sure 'Activites & Points d'interet' is checked when searching.")