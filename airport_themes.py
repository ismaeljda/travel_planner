# Dictionnaire des aéroports avec tags thématiques pour voyageurs jeunes/lowcost

airports_by_country = {
    'belgium': {
        'name': 'Belgique',
        'airports': {
            'CRL': {
                'name': 'Brussels South Charleroi Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip']
            },
            'BRU': {
                'name': 'Brussels Airport',
                'coastal': False, 
                'sea': None,
                'themes': ['city_trip']
            },
            'LGG': {
                'name': 'Liège Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip']
            },
            'OST': {
                'name': 'Ostend-Bruges International Airport',
                'coastal': True,
                'sea': 'North Sea',
                'themes': ['beach', 'couple', 'city_trip']
            },
            'ANR': {
                'name': 'Antwerp International Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip']
            }
        }
    },
    'france': {
        'name': 'France',
        'airports': {
            'CDG': {
                'name': 'Charles de Gaulle Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'ORY': {
                'name': 'Paris Orly Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'NCE': {
                'name': 'Nice Côte d\'Azur Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'couple', 'city_trip']
            },
            'MRS': {
                'name': 'Marseille Provence Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'city_trip']
            },
            'BOD': {
                'name': 'Bordeaux Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'couple', 'nature']
            },
            'NTE': {
                'name': 'Nantes Atlantique Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'nature', 'beach']
            },
            'LYS': {
                'name': 'Lyon-Saint Exupéry Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'nature']
            },
            'TLS': {
                'name': 'Toulouse-Blagnac Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'BIQ': {
                'name': 'Biarritz Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'couple', 'nature']
            },
            'MPL': {
                'name': 'Montpellier Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'city_trip']
            },
            'PGF': {
                'name': 'Perpignan Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'nature']
            },
            'BES': {
                'name': 'Brest Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['nature', 'beach']
            }
        }
    },
    'spain': {
        'name': 'Espagne',
        'airports': {
            'BCN': {
                'name': 'Barcelona-El Prat Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['city_trip', 'party', 'beach', 'couple']
            },
            'MAD': {
                'name': 'Madrid-Barajas Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party', 'couple']
            },
            'PMI': {
                'name': 'Palma Mallorca Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'couple']
            },
            'IBZ': {
                'name': 'Ibiza Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['party', 'beach', 'couple']
            },
            'AGP': {
                'name': 'Málaga Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'couple']
            },
            'VLC': {
                'name': 'Valencia Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'city_trip']
            },
            'ALC': {
                'name': 'Alicante Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'couple']
            },
            'BIO': {
                'name': 'Bilbao Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'nature', 'couple']
            },
            'SVQ': {
                'name': 'Seville Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'LPA': {
                'name': 'Las Palmas Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'nature']
            },
            'TFS': {
                'name': 'Tenerife South Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'nature', 'mountain']
            },
            'ACE': {
                'name': 'Lanzarote Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'nature']
            },
            'FUE': {
                'name': 'Fuerteventura Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'nature']
            },
            'SDR': {
                'name': 'Santander Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['nature', 'beach']
            }
        }
    },
    'italy': {
        'name': 'Italie',
        'airports': {
            'FCO': {
                'name': 'Rome Fiumicino Airport',
                'coastal': True,
                'sea': 'Tyrrhenian',
                'themes': ['city_trip', 'couple', 'beach']
            },
            'CIA': {
                'name': 'Rome Ciampino Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple']
            },
            'MXP': {
                'name': 'Milan Malpensa Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'mountain']
            },
            'BGY': {
                'name': 'Milan Bergamo Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'mountain']
            },
            'VCE': {
                'name': 'Venice Marco Polo Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['couple', 'city_trip', 'beach']
            },
            'NAP': {
                'name': 'Naples International Airport',
                'coastal': True,
                'sea': 'Tyrrhenian',
                'themes': ['beach', 'city_trip', 'couple']
            },
            'BLQ': {
                'name': 'Bologna Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple']
            },
            'FLR': {
                'name': 'Florence Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple']
            },
            'CTA': {
                'name': 'Catania Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'nature', 'mountain']
            },
            'PMO': {
                'name': 'Palermo Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'city_trip', 'couple']
            },
            'BRI': {
                'name': 'Bari Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['beach', 'couple']
            },
            'CAG': {
                'name': 'Cagliari Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'nature']
            },
            'PSA': {
                'name': 'Pisa Airport',
                'coastal': True,
                'sea': 'Tyrrhenian',
                'themes': ['beach', 'city_trip', 'couple']
            }
        }
    },
    'portugal': {
        'name': 'Portugal',
        'airports': {
            'LIS': {
                'name': 'Lisbon Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'couple', 'beach', 'party']
            },
            'OPO': {
                'name': 'Porto Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'couple', 'party']
            },
            'FAO': {
                'name': 'Faro Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'couple', 'party']
            },
            'FNC': {
                'name': 'Funchal Airport (Madeira)',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['nature', 'beach', 'couple', 'mountain']
            }
        }
    },
    'greece': {
        'name': 'Grèce',
        'airports': {
            'ATH': {
                'name': 'Athens International Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'beach']
            },
            'SKG': {
                'name': 'Thessaloniki Airport',
                'coastal': True,
                'sea': 'Aegean',
                'themes': ['city_trip', 'party', 'beach']
            },
            'HER': {
                'name': 'Heraklion Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'party', 'nature']
            },
            'RHO': {
                'name': 'Rhodes Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'couple', 'party']
            },
            'CFU': {
                'name': 'Corfu Airport',
                'coastal': True,
                'sea': 'Ionian',
                'themes': ['beach', 'party', 'couple']
            },
            'CHQ': {
                'name': 'Chania Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['beach', 'nature']
            },
            'KGS': {
                'name': 'Kos Airport',
                'coastal': True,
                'sea': 'Aegean',
                'themes': ['beach', 'party']
            },
            'ZTH': {
                'name': 'Zakynthos Airport',
                'coastal': True,
                'sea': 'Ionian',
                'themes': ['beach', 'party', 'couple']
            },
            'JTR': {
                'name': 'Santorini Airport',
                'coastal': True,
                'sea': 'Aegean',
                'themes': ['couple', 'beach', 'city_trip']
            },
            'MYK': {
                'name': 'Mykonos Airport',
                'coastal': True,
                'sea': 'Aegean',
                'themes': ['party', 'beach', 'couple']
            }
        }
    },
    'uk': {
        'name': 'Royaume-Uni',
        'airports': {
            'STN': {
                'name': 'London Stansted Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'LTN': {
                'name': 'London Luton Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'LGW': {
                'name': 'London Gatwick Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'MAN': {
                'name': 'Manchester Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'EDI': {
                'name': 'Edinburgh Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'nature']
            },
            'LPL': {
                'name': 'Liverpool John Lennon Airport',
                'coastal': True,
                'sea': 'Irish Sea',
                'themes': ['city_trip', 'party']
            },
            'GLA': {
                'name': 'Glasgow Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'nature', 'mountain']
            }
        }
    },
    'ireland': {
        'name': 'Irlande',
        'airports': {
            'DUB': {
                'name': 'Dublin Airport',
                'coastal': True,
                'sea': 'Irish Sea',
                'themes': ['city_trip', 'party', 'couple']
            },
            'ORK': {
                'name': 'Cork Airport',
                'coastal': True,
                'sea': 'Celtic Sea',
                'themes': ['nature', 'city_trip']
            },
            'SNN': {
                'name': 'Shannon Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['nature']
            }
        }
    },
    'germany': {
        'name': 'Allemagne',
        'airports': {
            'BER': {
                'name': 'Berlin Brandenburg Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party', 'couple']
            },
            'MUC': {
                'name': 'Munich Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'mountain', 'party']
            },
            'FRA': {
                'name': 'Frankfurt Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip']
            },
            'HAM': {
                'name': 'Hamburg Airport',
                'coastal': True,
                'sea': 'North Sea',
                'themes': ['city_trip', 'party']
            },
            'CGN': {
                'name': 'Cologne Bonn Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'DUS': {
                'name': 'Düsseldorf Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'STR': {
                'name': 'Stuttgart Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'mountain']
            }
        }
    },
    'netherlands': {
        'name': 'Pays-Bas',
        'airports': {
            'AMS': {
                'name': 'Amsterdam Schiphol Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party', 'couple']
            },
            'EIN': {
                'name': 'Eindhoven Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'MST': {
                'name': 'Maastricht Aachen Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip']
            },
            'RTM': {
                'name': 'Rotterdam The Hague Airport',
                'coastal': True,
                'sea': 'North Sea',
                'themes': ['city_trip']
            }
        }
    },
    'czech_republic': {
        'name': 'République Tchèque',
        'airports': {
            'PRG': {
                'name': 'Prague Václav Havel Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party', 'couple']
            }
        }
    },
    'hungary': {
        'name': 'Hongrie',
        'airports': {
            'BUD': {
                'name': 'Budapest Ferenc Liszt International Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party', 'couple']
            }
        }
    },
    'poland': {
        'name': 'Pologne',
        'airports': {
            'WAW': {
                'name': 'Warsaw Chopin Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            },
            'KRK': {
                'name': 'Kraków Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'party']
            },
            'GDN': {
                'name': 'Gdańsk Airport',
                'coastal': True,
                'sea': 'Baltic Sea',
                'themes': ['city_trip', 'beach', 'party']
            }
        }
    },
    'croatia': {
        'name': 'Croatie',
        'airports': {
            'ZAG': {
                'name': 'Zagreb Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'nature']
            },
            'SPU': {
                'name': 'Split Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['beach', 'party', 'couple']
            },
            'DBV': {
                'name': 'Dubrovnik Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['couple', 'beach', 'city_trip']
            },
            'ZAD': {
                'name': 'Zadar Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['beach', 'couple', 'nature']
            },
            'PUY': {
                'name': 'Pula Airport',
                'coastal': True,
                'sea': 'Adriatic',
                'themes': ['beach', 'couple', 'nature']
            }
        }
    },
    'austria': {
        'name': 'Autriche',
        'airports': {
            'VIE': {
                'name': 'Vienna International Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple']
            },
            'SZG': {
                'name': 'Salzburg Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'mountain', 'nature']
            },
            'INN': {
                'name': 'Innsbruck Airport',
                'coastal': False,
                'sea': None,
                'themes': ['mountain', 'nature']
            }
        }
    },
    'switzerland': {
        'name': 'Suisse',
        'airports': {
            'ZUR': {
                'name': 'Zurich Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'mountain', 'nature']
            },
            'GVA': {
                'name': 'Geneva Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'mountain', 'nature']
            }
        }
    },
    'norway': {
        'name': 'Norvège',
        'airports': {
            'OSL': {
                'name': 'Oslo Gardermoen Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'nature', 'mountain']
            },
            'BGO': {
                'name': 'Bergen Airport',
                'coastal': True,
                'sea': 'North Sea',
                'themes': ['nature', 'mountain']
            },
            'TRD': {
                'name': 'Trondheim Airport',
                'coastal': True,
                'sea': 'Norwegian Sea',
                'themes': ['nature', 'mountain']
            }
        }
    },
    'sweden': {
        'name': 'Suède',
        'airports': {
            'ARN': {
                'name': 'Stockholm Arlanda Airport',
                'coastal': True,
                'sea': 'Baltic Sea',
                'themes': ['city_trip', 'nature', 'couple']
            },
            'GOT': {
                'name': 'Gothenburg Landvetter Airport',
                'coastal': True,
                'sea': 'North Sea',
                'themes': ['city_trip', 'nature']
            }
        }
    },
    'denmark': {
        'name': 'Danemark',
        'airports': {
            'CPH': {
                'name': 'Copenhagen Airport',
                'coastal': True,
                'sea': 'Øresund',
                'themes': ['city_trip', 'couple', 'party']
            }
        }
    },
    'romania': {
        'name': 'Roumanie',
        'airports': {
            'OTP': {
                'name': 'Henri Coandă International Airport (Bucharest)',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'party']
            }
        }
    },
    'bulgaria': {
        'name': 'Bulgarie',
        'airports': {
            'SOF': {
                'name': 'Sofia Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'mountain']
            },
            'VAR': {
                'name': 'Varna Airport',
                'coastal': True,
                'sea': 'Black Sea',
                'themes': ['beach', 'party']
            },
            'BOJ': {
                'name': 'Burgas Airport',
                'coastal': True,
                'sea': 'Black Sea',
                'themes': ['beach', 'party']
            }
        }
    },
    'morocco': {
        'name': 'Maroc',
        'airports': {
            'CMN': {
                'name': 'Mohammed V International Airport (Casablanca)',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['city_trip', 'beach']
            },
            'RAK': {
                'name': 'Marrakech Menara Airport',
                'coastal': False,
                'sea': None,
                'themes': ['city_trip', 'couple', 'nature']
            },
            'AGA': {
                'name': 'Agadir–Al Massira Airport',
                'coastal': True,
                'sea': 'Atlantic',
                'themes': ['beach', 'couple']
            }
        }
    }
}

# Fonctions pour filtrer par thème
def get_airports_by_theme(theme):
    """Retourne tous les aéroports correspondant à un thème donné"""
    airports = []
    for country_data in airports_by_country.values():
        for code, airport_info in country_data['airports'].items():
            if theme in airport_info.get('themes', []):
                airports.append(code)
    return airports

def get_airports_by_themes(themes):
    """Retourne tous les aéroports correspondant à au moins un des thèmes donnés"""
    airports = []
    for country_data in airports_by_country.values():
        for code, airport_info in country_data['airports'].items():
            airport_themes = airport_info.get('themes', [])
            if any(theme in airport_themes for theme in themes):
                airports.append(code)
    return list(set(airports))  # Remove duplicates

# Mapping des thèmes
THEMES = {
    'couple': {
        'name': '💕 Couple',
        'description': 'Romantique mais abordable',
        'color': '#ff6b9d',
        'icon': 'bi-heart-fill'
    },
    'party': {
        'name': '🎉 Fête',
        'description': 'Nightlife, festivals, vie nocturne',
        'color': '#ff9f1c',
        'icon': 'bi-music-note-beamed'
    },
    'beach': {
        'name': '🏖️ Plage & Détente',
        'description': 'Soleil, mer, relaxation',
        'color': '#2ec4b6',
        'icon': 'bi-water'
    },
    'nature': {
        'name': '🌲 Nature',
        'description': 'Randos, parcs, outdoor',
        'color': '#8ac926',
        'icon': 'bi-tree-fill'
    },
    'mountain': {
        'name': '⛰️ Montagne',
        'description': 'Ski low-cost, chalets, air pur',
        'color': '#6f4a8e',
        'icon': 'bi-mountain'
    },
    'city_trip': {
        'name': '🏙️ City Trip',
        'description': 'Découverte urbaine, culture accessible',
        'color': '#1982c4',
        'icon': 'bi-building'
    }
}

# Backward compatibility functions
def get_airports_by_countries(countries):
    airports = []
    for country in countries:
        if country in airports_by_country:
            airports.extend(list(airports_by_country[country]['airports'].keys()))
    return airports

def get_airport_name(code):
    for country_data in airports_by_country.values():
        if code in country_data['airports']:
            return country_data['airports'][code]['name']
    return code

def get_airport_info(code):
    for country_data in airports_by_country.values():
        if code in country_data['airports']:
            return country_data['airports'][code]
    return {'name': code, 'coastal': None, 'sea': None, 'themes': []}

def get_coastal_airports_by_countries(countries, coastal_only=True):
    airports = []
    for country in countries:
        if country in airports_by_country:
            for code, info in airports_by_country[country]['airports'].items():
                if coastal_only and info.get('coastal', False):
                    airports.append(code)
                elif not coastal_only and not info.get('coastal', True):
                    airports.append(code)
    return airports