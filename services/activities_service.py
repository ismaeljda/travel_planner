import requests
import re
from amadeus import Client, ResponseError
from airport_themes import get_airport_info


class AmadeusActivitiesService:
    def __init__(self, app_config):
        """Initialize with app config to access API keys"""
        self.config = app_config
        self.amadeus = Client(
            client_id=app_config['AMADEUS_API_KEY'],
            client_secret=app_config['AMADEUS_API_SECRET']
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