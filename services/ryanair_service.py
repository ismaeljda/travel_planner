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