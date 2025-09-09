from airport_themes import get_airport_info


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