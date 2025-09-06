from ryanair import Ryanair
from datetime import datetime, timedelta

# Aéroports organisés par pays
airports_by_country = {
    'belgium': {
        'name': 'Belgique',
        'airports': {
            'CRL': 'Brussels South Charleroi Airport',
            'BRU': 'Brussels Airport',
            'LGG': 'Liège Airport',
            'OST': 'Ostend-Bruges International Airport',
            'ANR': 'Antwerp International Airport'
        }
    },
    'netherlands': {
        'name': 'Pays-Bas', 
        'airports': {
            'EIN': 'Eindhoven Airport',
            'MST': 'Maastricht Aachen Airport',
            'AMS': 'Amsterdam Schiphol Airport',
            'RTM': 'Rotterdam The Hague Airport',
            'GRQ': 'Groningen Airport Eelde',
            'LEY': 'Lelystad Airport',
            'DHR': 'De Kooy Airport'
        }
    },
    'germany': {
        'name': 'Allemagne',
        'airports': {
            'CGN': 'Cologne Bonn Airport',
            'DUS': 'Düsseldorf Airport',
            'FRA': 'Frankfurt Airport',
            'HAM': 'Hamburg Airport',
            'BER': 'Berlin Brandenburg Airport',
            'MUC': 'Munich Airport',
            'STR': 'Stuttgart Airport',
            'NUE': 'Nuremberg Airport',
            'HAJ': 'Hannover Airport',
            'DTM': 'Dortmund Airport',
            'FDH': 'Friedrichshafen Airport',
            'KSF': 'Kassel Airport',
            'PAD': 'Paderborn Lippstadt Airport',
            'FKB': 'Karlsruhe/Baden-Baden Airport',
            'SXF': 'Berlin Schönefeld Airport',
            'DRS': 'Dresden Airport',
            'LEJ': 'Leipzig/Halle Airport',
            'ERF': 'Erfurt Airport',
            'FMM': 'Memmingen Airport',
            'HHN': 'Frankfurt-Hahn Airport',
            'NRN': 'Weeze Airport',
            'LBC': 'Lübeck Airport'
        }
    },
    'france': {
        'name': 'France',
        'airports': {
            'CDG': {'name': 'Charles de Gaulle Airport', 'coastal': False, 'sea': None},
            'ORY': {'name': 'Paris Orly Airport', 'coastal': False, 'sea': None},
            'LYS': {'name': 'Lyon-Saint Exupéry Airport', 'coastal': False, 'sea': None},
            'MRS': {'name': 'Marseille Provence Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'NCE': {'name': 'Nice Côte d\'Azur Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'TLS': {'name': 'Toulouse-Blagnac Airport', 'coastal': False, 'sea': None},
            'BOD': {'name': 'Bordeaux Airport', 'coastal': True, 'sea': 'Atlantic'},
            'NTE': {'name': 'Nantes Atlantique Airport', 'coastal': True, 'sea': 'Atlantic'},
            'LIL': {'name': 'Lille Airport', 'coastal': False, 'sea': None},
            'MLH': {'name': 'EuroAirport Basel Mulhouse Freiburg', 'coastal': False, 'sea': None},
            'SXB': {'name': 'Strasbourg Airport', 'coastal': False, 'sea': None},
            'RNS': {'name': 'Rennes Airport', 'coastal': False, 'sea': None},
            'BVA': {'name': 'Paris Beauvais Airport', 'coastal': False, 'sea': None},
            'MPL': {'name': 'Montpellier Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'BIQ': {'name': 'Biarritz Airport', 'coastal': True, 'sea': 'Atlantic'},
            'CCF': {'name': 'Carcassonne Airport', 'coastal': False, 'sea': None},
            'PGF': {'name': 'Perpignan Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'LIG': {'name': 'Limoges Airport', 'coastal': False, 'sea': None},
            'PUF': {'name': 'Pau Airport', 'coastal': False, 'sea': None},
            'BES': {'name': 'Brest Airport', 'coastal': True, 'sea': 'Atlantic'},
            'LRT': {'name': 'Lorient Airport', 'coastal': True, 'sea': 'Atlantic'},
            'QPX': {'name': 'Quimper Airport', 'coastal': True, 'sea': 'Atlantic'},
            'CFE': {'name': 'Clermont-Ferrand Airport', 'coastal': False, 'sea': None},
            'RDZ': {'name': 'Rodez Airport', 'coastal': False, 'sea': None},
            'AUR': {'name': 'Aurillac Airport', 'coastal': False, 'sea': None},
            'ETC': {'name': 'Le Touquet Airport', 'coastal': True, 'sea': 'Atlantic'},
            'CNG': {'name': 'Cognac Airport', 'coastal': False, 'sea': None}
        }
    },
    'spain': {
        'name': 'Espagne',
        'airports': {
            'BCN': {'name': 'Barcelona-El Prat Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'MAD': {'name': 'Madrid-Barajas Airport', 'coastal': False, 'sea': None},
            'PMI': {'name': 'Palma Mallorca Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'AGP': {'name': 'Málaga Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'SVQ': {'name': 'Seville Airport', 'coastal': False, 'sea': None},
            'VLC': {'name': 'Valencia Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'BIO': {'name': 'Bilbao Airport', 'coastal': True, 'sea': 'Atlantic'},
            'LPA': {'name': 'Las Palmas Airport', 'coastal': True, 'sea': 'Atlantic'},
            'TFS': {'name': 'Tenerife South Airport', 'coastal': True, 'sea': 'Atlantic'},
            'ACE': {'name': 'Lanzarote Airport', 'coastal': True, 'sea': 'Atlantic'},
            'ALC': {'name': 'Alicante Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'GRO': {'name': 'Girona Airport', 'coastal': False, 'sea': None},
            'IBZ': {'name': 'Ibiza Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'JER': {'name': 'Jerez Airport', 'coastal': False, 'sea': None},
            'LEI': {'name': 'Almería Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'LCG': {'name': 'La Coruña Airport', 'coastal': True, 'sea': 'Atlantic'},
            'MAH': {'name': 'Menorca Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'OVD': {'name': 'Oviedo Airport', 'coastal': True, 'sea': 'Atlantic'},
            'REU': {'name': 'Reus Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'SLM': {'name': 'Salamanca Airport', 'coastal': False, 'sea': None},
            'SCQ': {'name': 'Santiago de Compostela Airport', 'coastal': False, 'sea': None},
            'SDR': {'name': 'Santander Airport', 'coastal': True, 'sea': 'Atlantic'},
            'VGO': {'name': 'Vigo Airport', 'coastal': True, 'sea': 'Atlantic'},
            'VIT': {'name': 'Vitoria Airport', 'coastal': False, 'sea': None},
            'ZAZ': {'name': 'Zaragoza Airport', 'coastal': False, 'sea': None},
            'XRY': {'name': 'Jerez de la Frontera Airport', 'coastal': False, 'sea': None},
            'FUE': {'name': 'Fuerteventura Airport', 'coastal': True, 'sea': 'Atlantic'},
            'GMZ': {'name': 'La Gomera Airport', 'coastal': True, 'sea': 'Atlantic'}
        }
    },
    'italy': {
        'name': 'Italie',
        'airports': {
            'FCO': {'name': 'Rome Fiumicino Airport', 'coastal': True, 'sea': 'Tyrrhenian'},
            'CIA': {'name': 'Rome Ciampino Airport', 'coastal': False, 'sea': None},
            'MXP': {'name': 'Milan Malpensa Airport', 'coastal': False, 'sea': None},
            'BGY': {'name': 'Milan Bergamo Airport', 'coastal': False, 'sea': None},
            'VCE': {'name': 'Venice Marco Polo Airport', 'coastal': True, 'sea': 'Adriatic'},
            'NAP': {'name': 'Naples International Airport', 'coastal': True, 'sea': 'Tyrrhenian'},
            'BLQ': {'name': 'Bologna Airport', 'coastal': False, 'sea': None},
            'FLR': {'name': 'Florence Airport', 'coastal': False, 'sea': None},
            'CTA': {'name': 'Catania Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'PMO': {'name': 'Palermo Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'LIN': {'name': 'Milan Linate Airport', 'coastal': False, 'sea': None},
            'TSF': {'name': 'Treviso Airport', 'coastal': False, 'sea': None},
            'VRN': {'name': 'Verona Villafranca Airport', 'coastal': False, 'sea': None},
            'GOA': {'name': 'Genoa Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'TRN': {'name': 'Turin Airport', 'coastal': False, 'sea': None},
            'AOI': {'name': 'Ancona Airport', 'coastal': True, 'sea': 'Adriatic'},
            'BRI': {'name': 'Bari Airport', 'coastal': True, 'sea': 'Adriatic'},
            'PSR': {'name': 'Pescara Airport', 'coastal': True, 'sea': 'Adriatic'},
            'REG': {'name': 'Reggio Calabria Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'CRV': {'name': 'Crotone Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'LMP': {'name': 'Lampedusa Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'PNL': {'name': 'Pantelleria Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'TPS': {'name': 'Trapani Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'CUF': {'name': 'Cuneo Airport', 'coastal': False, 'sea': None},
            'BZO': {'name': 'Bolzano Airport', 'coastal': False, 'sea': None},
            'RMI': {'name': 'Rimini Airport', 'coastal': True, 'sea': 'Adriatic'},
            'PSA': {'name': 'Pisa Airport', 'coastal': True, 'sea': 'Tyrrhenian'},
            'SUF': {'name': 'Lamezia Terme Airport', 'coastal': True, 'sea': 'Tyrrhenian'},
            'BDS': {'name': 'Brindisi Airport', 'coastal': True, 'sea': 'Adriatic'},
            'TAR': {'name': 'Taranto Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'FOG': {'name': 'Foggia Airport', 'coastal': False, 'sea': None},
            'CAG': {'name': 'Cagliari Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'AHO': {'name': 'Alghero Airport', 'coastal': True, 'sea': 'Mediterranean'},
            'OLB': {'name': 'Olbia Airport', 'coastal': True, 'sea': 'Mediterranean'}
        }
    },
    'portugal': {
        'name': 'Portugal',
        'airports': {
            'LIS': {'name': 'Lisbon Airport', 'coastal': True, 'sea': 'Atlantic'},
            'OPO': {'name': 'Porto Airport', 'coastal': True, 'sea': 'Atlantic'},
            'FAO': {'name': 'Faro Airport', 'coastal': True, 'sea': 'Atlantic'},
            'FNC': {'name': 'Funchal Airport (Madeira)', 'coastal': True, 'sea': 'Atlantic'},
            'TER': {'name': 'Terceira Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'PDL': {'name': 'João Paulo II Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'HOR': {'name': 'Horta Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'PIX': {'name': 'Pico Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'PXO': {'name': 'Porto Santo Airport', 'coastal': True, 'sea': 'Atlantic'},
            'SMA': {'name': 'Santa Maria Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'GRW': {'name': 'Graciosa Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'FLW': {'name': 'Flores Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'CVU': {'name': 'Corvo Airport (Azores)', 'coastal': True, 'sea': 'Atlantic'},
            'BGC': {'name': 'Bragança Airport', 'coastal': False, 'sea': None},
            'VRL': {'name': 'Vila Real Airport', 'coastal': False, 'sea': None},
            'CHV': {'name': 'Chaves Airport', 'coastal': False, 'sea': None}
        }
    },
    'uk': {
        'name': 'Royaume-Uni',
        'airports': {
            'STN': 'London Stansted Airport',
            'LTN': 'London Luton Airport',
            'LGW': 'London Gatwick Airport',
            'LHR': 'London Heathrow Airport',
            'LCY': 'London City Airport',
            'SEN': 'London Southend Airport',
            'MAN': 'Manchester Airport',
            'EDI': 'Edinburgh Airport',
            'LPL': 'Liverpool John Lennon Airport',
            'BHX': 'Birmingham Airport',
            'GLA': 'Glasgow Airport',
            'ABZ': 'Aberdeen Airport',
            'PIK': 'Glasgow Prestwick Airport',
            'NCL': 'Newcastle Airport',
            'LBA': 'Leeds Bradford Airport',
            'DSA': 'Robin Hood Doncaster Sheffield Airport',
            'EMA': 'East Midlands Airport',
            'NWI': 'Norwich Airport',
            'BOH': 'Bournemouth Airport',
            'BRS': 'Bristol Airport',
            'CWL': 'Cardiff Airport',
            'SWS': 'Swansea Airport',
            'INV': 'Inverness Airport',
            'DND': 'Dundee Airport',
            'SYY': 'Stornoway Airport',
            'IOM': 'Isle of Man Airport',
            'JER': 'Jersey Airport',
            'GCI': 'Guernsey Airport',
            'ACI': 'Alderney Airport',
            'BEB': 'Benbecula Airport',
            'UNT': 'Unst Airport',
            'PSL': 'Perth Airport',
            'ILY': 'Islay Airport',
            'COL': 'Coll Airport',
            'OBN': 'Oban Airport',
            'CAL': 'Campbeltown Airport'
        }
    },
    'ireland': {
        'name': 'Irlande',
        'airports': {
            'DUB': 'Dublin Airport',
            'ORK': 'Cork Airport',
            'SNN': 'Shannon Airport',
            'KIR': 'Kerry Airport',
            'WAT': 'Waterford Airport',
            'NOC': 'Ireland West Airport Knock',
            'CFN': 'Donegal Airport',
            'GWY': 'Galway Airport',
            'SLG': 'Sligo Airport',
            'BLY': 'Belmullet Airport',
            'IOR': 'Inishmore Airport',
            'IIA': 'Inisheer Airport',
            'IIN': 'Inishmaan Airport'
        }
    },
    'poland': {
        'name': 'Pologne',
        'airports': {
            'WAW': 'Warsaw Chopin Airport',
            'KRK': 'Kraków Airport',
            'GDN': 'Gdańsk Airport',
            'WRO': 'Wrocław Airport',
            'POZ': 'Poznań Airport',
            'KTW': 'Katowice Airport',
            'RZE': 'Rzeszów Airport',
            'LUZ': 'Lublin Airport',
            'SZZ': 'Szczecin Airport',
            'BZG': 'Bydgoszcz Airport',
            'LCJ': 'Łódź Airport',
            'OSZ': 'Koszalin Airport',
            'EPO': 'Olsztyn Airport',
            'RDO': 'Radom Airport',
            'IEG': 'Zielona Góra Airport',
            'WMI': 'Warsaw Modlin Airport'
        }
    },
    'greece': {
        'name': 'Grèce',
        'airports': {
            'ATH': 'Athens International Airport',
            'SKG': 'Thessaloniki Airport',
            'HER': 'Heraklion Airport',
            'RHO': 'Rhodes Airport',
            'CFU': 'Corfu Airport',
            'CHQ': 'Chania Airport',
            'KGS': 'Kos Airport',
            'ZTH': 'Zakynthos Airport',
            'SMI': 'Samos Airport',
            'MJT': 'Mytilene Airport',
            'JTR': 'Santorini Airport',
            'MYK': 'Mykonos Airport',
            'PAS': 'Paros Airport',
            'JSI': 'Skiathos Airport',
            'VOL': 'Volos Airport',
            'KVA': 'Kavala Airport',
            'AOK': 'Karpathos Airport',
            'JKH': 'Chios Airport',
            'LRS': 'Leros Airport',
            'KIT': 'Kithira Airport',
            'JNX': 'Naxos Airport',
            'JSY': 'Syros Airport',
            'MLO': 'Milos Airport',
            'IKA': 'Ikaria Airport',
            'JIK': 'Ikaria Island Airport'
        }
    },
    'czech_republic': {
        'name': 'République Tchèque',
        'airports': {
            'PRG': 'Prague Václav Havel Airport',
            'BRQ': 'Brno-Tuřany Airport',
            'OSR': 'Ostrava Airport',
            'PED': 'Pardubice Airport',
            'KLV': 'Karlovy Vary Airport'
        }
    },
    'hungary': {
        'name': 'Hongrie',
        'airports': {
            'BUD': 'Budapest Ferenc Liszt International Airport',
            'DEB': 'Debrecen International Airport',
            'PEV': 'Pécs-Pogány Airport',
            'SOB': 'Sármellék International Airport'
        }
    },
    'croatia': {
        'name': 'Croatie',
        'airports': {
            'ZAG': 'Zagreb Airport',
            'SPU': 'Split Airport',
            'DBV': 'Dubrovnik Airport',
            'ZAD': 'Zadar Airport',
            'RJK': 'Rijeka Airport',
            'PUY': 'Pula Airport',
            'OSI': 'Osijek Airport',
            'LSZ': 'Lošinj Airport',
            'BWK': 'Brač Airport'
        }
    },
    'romania': {
        'name': 'Roumanie',
        'airports': {
            'OTP': 'Henri Coandă International Airport (Bucharest)',
            'CLJ': 'Cluj-Napoca International Airport',
            'TSR': 'Timișoara Airport',
            'IAS': 'Iași Airport',
            'CND': 'Mihail Kogălniceanu International Airport',
            'SBZ': 'Sibiu Airport',
            'BCM': 'Bacău Airport',
            'CRA': 'Craiova Airport',
            'SCV': 'Suceava Airport',
            'OMR': 'Oradea Airport'
        }
    },
    'bulgaria': {
        'name': 'Bulgarie',
        'airports': {
            'SOF': 'Sofia Airport',
            'VAR': 'Varna Airport',
            'BOJ': 'Burgas Airport',
            'PDV': 'Plovdiv Airport',
            'ROU': 'Ruse Airport'
        }
    },
    'austria': {
        'name': 'Autriche',
        'airports': {
            'VIE': 'Vienna International Airport',
            'SZG': 'Salzburg Airport',
            'INN': 'Innsbruck Airport',
            'GRZ': 'Graz Airport',
            'LNZ': 'Linz Airport',
            'KLU': 'Klagenfurt Airport'
        }
    },
    'switzerland': {
        'name': 'Suisse',
        'airports': {
            'ZUR': 'Zurich Airport',
            'GVA': 'Geneva Airport',
            'BSL': 'EuroAirport Basel Mulhouse Freiburg',
            'BRN': 'Bern Airport',
            'LUG': 'Lugano Airport',
            'SMV': 'Samedan Airport',
            'SIR': 'Sion Airport'
        }
    },
    'sweden': {
        'name': 'Suède',
        'airports': {
            'ARN': 'Stockholm Arlanda Airport',
            'BMA': 'Stockholm Bromma Airport',
            'NYO': 'Stockholm Skavsta Airport',
            'GOT': 'Gothenburg Landvetter Airport',
            'GSE': 'Gothenburg City Airport',
            'MMX': 'Malmö Airport',
            'RNB': 'Ronneby Airport',
            'KID': 'Kristianstad Airport',
            'VXO': 'Växjö Airport',
            'JKG': 'Jönköping Airport'
        }
    },
    'norway': {
        'name': 'Norvège',
        'airports': {
            'OSL': 'Oslo Gardermoen Airport',
            'TRF': 'Oslo Sandefjord Airport',
            'BGO': 'Bergen Airport',
            'TRD': 'Trondheim Airport',
            'SVG': 'Stavanger Airport',
            'KRS': 'Kristiansand Airport',
            'AES': 'Alesund Airport',
            'BOO': 'Bodø Airport',
            'TOS': 'Tromsø Airport',
            'EVE': 'Harstad/Narvik Airport'
        }
    },
    'denmark': {
        'name': 'Danemark',
        'airports': {
            'CPH': 'Copenhagen Airport',
            'BLL': 'Billund Airport',
            'AAL': 'Aalborg Airport',
            'EBJ': 'Esbjerg Airport',
            'KRP': 'Karup Airport',
            'RKE': 'Roskilde Airport',
            'ODE': 'Odense Airport'
        }
    },
    'finland': {
        'name': 'Finlande',
        'airports': {
            'HEL': 'Helsinki-Vantaa Airport',
            'TMP': 'Tampere-Pirkkala Airport',
            'TKU': 'Turku Airport',
            'OUL': 'Oulu Airport',
            'RVN': 'Rovaniemi Airport',
            'KUO': 'Kuopio Airport',
            'JOE': 'Joensuu Airport',
            'VAA': 'Vaasa Airport'
        }
    },
    'lithuania': {
        'name': 'Lituanie',
        'airports': {
            'VNO': 'Vilnius Airport',
            'KUN': 'Kaunas Airport',
            'PLQ': 'Palanga Airport'
        }
    },
    'latvia': {
        'name': 'Lettonie',
        'airports': {
            'RIX': 'Riga International Airport',
            'LPX': 'Liepāja International Airport',
            'DGR': 'Daugavpils Airport'
        }
    },
    'estonia': {
        'name': 'Estonie',
        'airports': {
            'TLL': 'Tallinn Airport',
            'TAY': 'Tartu Airport',
            'EPU': 'Pärnu Airport',
            'KDL': 'Kärdla Airport'
        }
    },
    'morocco': {
        'name': 'Maroc',
        'airports': {
            'CMN': 'Mohammed V International Airport (Casablanca)',
            'RAK': 'Marrakech Menara Airport',
            'FEZ': 'Fez–Saïs Airport',
            'AGA': 'Agadir–Al Massira Airport',
            'TNG': 'Tangier Ibn Battouta Airport',
            'OUD': 'Oujda Angads Airport',
            'NDR': 'Nador International Airport',
            'RBA': 'Rabat–Salé Airport',
            'TTU': 'Tetouan Sania Ramel Airport'
        }
    }
}

# Fonction pour obtenir tous les aéroports d'un ou plusieurs pays
def get_airports_by_countries(countries):
    airports = []
    for country in countries:
        if country in airports_by_country:
            airports.extend(list(airports_by_country[country]['airports'].keys()))
    return airports

# Fonction pour obtenir le nom d'un aéroport
def get_airport_name(code):
    for country_data in airports_by_country.values():
        if code in country_data['airports']:
            airport_info = country_data['airports'][code]
            if isinstance(airport_info, dict):
                return airport_info['name']
            else:
                return airport_info
    return code

# Fonction pour obtenir les informations côtières d'un aéroport
def get_airport_info(code):
    for country_data in airports_by_country.values():
        if code in country_data['airports']:
            airport_info = country_data['airports'][code]
            if isinstance(airport_info, dict):
                return airport_info
            else:
                return {'name': airport_info, 'coastal': None, 'sea': None}
    return {'name': code, 'coastal': None, 'sea': None}

# Fonction pour filtrer les aéroports côtiers
def get_coastal_airports_by_countries(countries, coastal_only=True):
    airports = []
    for country in countries:
        if country in airports_by_country:
            for code, info in airports_by_country[country]['airports'].items():
                if isinstance(info, dict):
                    if coastal_only and info.get('coastal', False):
                        airports.append(code)
                    elif not coastal_only and not info.get('coastal', True):
                        airports.append(code)
                else:
                    # Format ancien, on inclut tout
                    airports.append(code)
    return airports


# This script now serves as a data provider for the web application
# The flight search logic has been moved to app.py

# Example usage (commented out - use the web interface instead):
"""
# Configuration de recherche
departure_airports = ['CRL']
target_countries = ['italy', 'spain', 'france']
departure_date_from = '2025-10-09'
departure_date_to = '2025-10-12'
min_stay_duration = 4

# Use the web application at http://localhost:5000 instead
print("Please use the web application: python app.py")
print("Then open http://localhost:5000 in your browser")
"""
