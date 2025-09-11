from datetime import datetime, timedelta
from ryanair import Ryanair
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from airport_themes import (
    get_airports_by_countries, get_coastal_airports_by_countries, 
    get_airport_name, get_airport_info,
    get_airports_by_theme
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
                                from services.ryanair_service import RyanairLinkService
                                
                                # Create smart Ryanair booking link
                                booking_link = RyanairLinkService.create_booking_link(
                                    trip.outbound.origin,
                                    trip.outbound.destination,
                                    trip.outbound.departureTime,
                                    trip.inbound.departureTime
                                )
                                
                                # Round prices to nearest 0.5 or integer
                                def round_price(price):
                                    rounded = round(price * 2) / 2
                                    return int(rounded) if rounded == int(rounded) else rounded
                                
                                results.append({
                                    'origin': trip.outbound.origin,
                                    'destination': trip.outbound.destination,
                                    'outbound_price': round_price(trip.outbound.price),
                                    'inbound_price': round_price(trip.inbound.price),
                                    'total_price': round_price(trip.totalPrice),
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