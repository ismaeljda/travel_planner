# Application Web de Recherche de Vols Ryanair

Une application web moderne pour rechercher des vols Ryanair pas chers avec des fonctionnalités avancées incluant la météo et les suggestions d'hébergement.

## 🌟 Fonctionnalités

- **Recherche Multi-Critères**: Recherchez des vols par pays, type de destination (côtière/intérieure), dates flexibles
- **Interface Utilisateur Moderne**: Interface responsive avec Bootstrap 5
- **Informations Météo**: Météo en temps réel pour les destinations
- **Suggestions d'Hébergement**: Intégration avec Hostelworld et Google Hotels
- **Filtrage Avancé**: Plus de 20 pays européens disponibles
- **Tri des Résultats**: Par prix, date de départ, ou durée

## 📋 Prérequis

- Python 3.7+
- pip (gestionnaire de packages Python)
- Clés API pour les services externes (optionnel)

## 🚀 Installation

1. **Cloner ou créer le projet**
   ```bash
   cd ryanair
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration des variables d'environnement (optionnel)**
   ```bash
   copy .env.example .env
   ```
   Éditez le fichier `.env` avec vos clés API.

4. **Lancer l'application**
   ```bash
   python app.py
   ```

5. **Accéder à l'application**
   Ouvrez votre navigateur sur `http://localhost:5000`

## 🔑 Configuration des API (Optionnel)

Pour activer toutes les fonctionnalités, obtenez les clés API suivantes :

### OpenWeatherMap (Météo)
1. Inscrivez-vous sur [OpenWeatherMap](https://openweathermap.org/api)
2. Obtenez votre clé API gratuite
3. Ajoutez `OPENWEATHER_API_KEY=votre_cle` dans `.env`

### Booking.com (Hébergements)
1. Inscrivez-vous sur [Booking.com Partner Hub](https://partner.booking.com/) pour l'API
2. Ajoutez `BOOKING_API_KEY=votre_cle` dans `.env`
   
**Note**: Hostelworld n'ayant pas d'API publique, l'application génère des liens directs vers les plateformes de réservation.

### Google Hotels (Hébergements)
1. Activez l'API Google Places sur [Google Cloud Console](https://console.cloud.google.com/)
2. Ajoutez `GOOGLE_HOTELS_API_KEY=votre_cle` dans `.env`

## 📁 Structure du Projet

```
ryanair/
├── app.py                 # Application Flask principale
├── main.py               # Script original (données des aéroports)
├── config.py             # Configuration
├── requirements.txt      # Dépendances Python
├── .env.example         # Exemple de variables d'environnement
├── templates/
│   └── index.html       # Template principal
└── static/
    ├── css/
    │   └── style.css    # Styles personnalisés
    └── js/
        └── app.js       # JavaScript de l'application
```

## 🖥️ Utilisation

1. **Sélectionner les aéroports de départ**
   - Choisissez un ou plusieurs pays
   - Les aéroports disponibles s'affichent automatiquement

2. **Choisir les destinations**
   - Sélectionnez les pays de destination
   - Optionnellement, filtrez par type (côtier/intérieur)

3. **Configurer les dates**
   - Période de départ flexible
   - Durée minimum de séjour

4. **Options avancées**
   - Inclure les informations météo
   - Inclure les suggestions d'hébergement

5. **Lancer la recherche**
   - Les résultats s'affichent triés par prix
   - Possibilité de trier par date ou durée

## 🌍 Pays et Destinations Supportés

L'application supporte plus de 20 pays européens incluant :
- France, Espagne, Italie, Portugal
- Allemagne, Pays-Bas, Belgique
- Royaume-Uni, Irlande
- Pays de l'Est, Scandinavie
- Grèce, Maroc

## 🎨 Personnalisation

### Modifier les Aéroports
Éditez `main.py` pour ajouter/modifier les aéroports dans `airports_by_country`.

### Personnaliser l'Interface
- CSS: `static/css/style.css`
- JavaScript: `static/js/app.js`
- HTML: `templates/index.html`

## 🐛 Résolution de Problèmes

### Erreur "No module named 'ryanair'"
```bash
pip install ryanair
```

### Erreur de connexion API
- Vérifiez votre connexion internet
- Vérifiez que les clés API sont correctes dans `.env`

### Aucun résultat trouvé
- Essayez d'élargir vos critères de recherche
- Vérifiez les dates (pas trop dans le futur)
- Certains aéroports peuvent avoir peu de connexions

## 🔧 Développement

Pour contribuer au projet :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Implémentez vos changements
4. Testez thoroughly
5. Soumettez une pull request

## 📊 API Endpoints

- `GET /` - Page principale
- `GET /api/airports/<country_code>` - Liste des aéroports par pays
- `POST /api/search` - Recherche de vols
- `GET /api/weather/<airport_code>` - Météo pour un aéroport
- `GET /api/accommodations/<destination>` - Hébergements

## ⚠️ Limitations

- Les données de vol proviennent de l'API Ryanair non officielle
- Les informations météo nécessitent une clé API
- Les hébergements nécessitent des clés API tierces
- Certaines destinations peuvent avoir une disponibilité limitée

## 📄 Licence

Ce projet est à des fins éducatives. Respectez les conditions d'utilisation des APIs tierces.

## 🆘 Support

Pour signaler des bugs ou demander de l'aide, créez une issue dans le repository.

---

**Bon voyage ! ✈️🌍**