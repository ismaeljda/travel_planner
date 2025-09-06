// Search Page JavaScript - Theme-based Flight Search

class SearchApp {
    constructor() {
        this.currentResults = [];
        this.displayedResults = 0;
        this.resultsPerPage = 10;
        this.selectedTheme = null;
        this.themes = {
            couple: { name: '💕 Couple', color: '#ff6b9d', description: 'Romantique mais abordable' },
            party: { name: '🎉 Fête', color: '#ff9f1c', description: 'Nightlife, festivals, vie nocturne' },
            beach: { name: '🏖️ Plage & Détente', color: '#2ec4b6', description: 'Soleil, mer, relaxation' },
            nature: { name: '🌲 Nature', color: '#8ac926', description: 'Randos, parcs, outdoor' },
            mountain: { name: '⛰️ Montagne', color: '#6f4a8e', description: 'Ski low-cost, chalets, air pur' },
            city_trip: { name: '🏙️ City Trip', color: '#1982c4', description: 'Découverte urbaine, culture accessible' }
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkThemeFromURL();
        this.updateDepartureAirports();
    }
    
    bindEvents() {
        // Form submission
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
        
        // Departure country change
        document.getElementById('departureCountry').addEventListener('change', () => {
            this.updateDepartureAirports();
        });
        
        // Sort buttons
        document.querySelectorAll('[data-sort]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.sortResults(e.target.dataset.sort);
                this.updateSortButtons(e.target);
            });
        });
        
        // Load more button
        document.getElementById('loadMoreBtn').addEventListener('click', () => {
            this.loadMoreResults();
        });
        
        // Activities checkbox toggle - show/hide activity filters
        document.getElementById('includeActivities').addEventListener('change', (e) => {
            const activitiesSection = document.getElementById('activitiesFiltersSection');
            if (e.target.checked) {
                activitiesSection.style.display = 'block';
            } else {
                activitiesSection.style.display = 'none';
                // Uncheck all activity filters when activities are disabled
                document.querySelectorAll('input[id^="category-"], input[id^="price-"]').forEach(cb => cb.checked = false);
                document.getElementById('minActivityRating').value = '';
            }
        });
        
        // Initialize activities filters visibility
        const includeActivitiesChecked = document.getElementById('includeActivities').checked;
        const activitiesSection = document.getElementById('activitiesFiltersSection');
        activitiesSection.style.display = includeActivitiesChecked ? 'block' : 'none';
        
        // Global functions
        window.changeTheme = () => {
            window.location.href = '/';
        };
        
        window.resetSearch = () => {
            document.getElementById('searchForm').reset();
            this.hideAllSections();
            document.getElementById('welcomeMessage').classList.remove('d-none');
        };
    }
    
    checkThemeFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const theme = urlParams.get('theme');
        
        if (theme && this.themes[theme]) {
            this.selectedTheme = theme;
            this.displaySelectedTheme();
            this.hideDestinationSection();
        }
    }
    
    displaySelectedTheme() {
        if (!this.selectedTheme) return;
        
        const themeData = this.themes[this.selectedTheme];
        const header = document.getElementById('themeHeader');
        
        document.getElementById('selectedThemeIcon').textContent = themeData.name.split(' ')[0];
        document.getElementById('selectedThemeName').textContent = themeData.name;
        document.getElementById('selectedThemeDesc').textContent = themeData.description;
        
        // Apply theme color
        header.style.borderLeft = `4px solid ${themeData.color}`;
        header.style.background = `linear-gradient(135deg, ${themeData.color}20, transparent)`;
        
        header.style.display = 'block';
    }
    
    hideDestinationSection() {
        const section = document.getElementById('destinationSection');
        if (section) {
            section.style.display = 'none';
        }
    }
    
    async updateDepartureAirports() {
        const selectedCountries = Array.from(document.getElementById('departureCountry').selectedOptions)
            .map(option => option.value);
        
        const container = document.getElementById('departureAirports');
        container.innerHTML = '';
        
        for (const countryCode of selectedCountries) {
            try {
                const response = await fetch(`/api/airports/${countryCode}`);
                const airports = await response.json();
                
                const countryDiv = document.createElement('div');
                countryDiv.className = 'airport-country mb-3';
                countryDiv.innerHTML = `
                    <label class="form-label fw-bold">${this.getCountryName(countryCode)}</label>
                    <div class="airport-grid">
                        ${Object.entries(airports).map(([code, info]) => `
                            <div class="form-check airport-item">
                                <input class="form-check-input departure-airport" type="checkbox" 
                                       value="${code}" id="dep_${code}" checked>
                                <label class="form-check-label" for="dep_${code}">
                                    <span class="airport-code">${code}</span>
                                    <small class="airport-name">${info.name || info}</small>
                                </label>
                            </div>
                        `).join('')}
                    </div>
                `;
                container.appendChild(countryDiv);
                
            } catch (error) {
                console.error(`Error loading airports for ${countryCode}:`, error);
            }
        }
    }
    
    getCountryName(countryCode) {
        const countryNames = {
            'belgium': 'Belgique',
            'netherlands': 'Pays-Bas', 
            'germany': 'Allemagne',
            'france': 'France',
            'spain': 'Espagne',
            'italy': 'Italie',
            'portugal': 'Portugal',
            'uk': 'Royaume-Uni',
            'ireland': 'Irlande'
        };
        return countryNames[countryCode] || countryCode;
    }
    
    async performSearch() {
        const formData = this.getFormData();
        
        if (!this.validateForm(formData)) {
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentResults = data.results;
                this.displayResults();
            } else {
                this.showError(data.error || 'Erreur lors de la recherche');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Erreur de connexion. Veuillez réessayer.');
        } finally {
            this.hideLoading();
        }
    }
    
    getFormData() {
        const departureAirports = Array.from(document.querySelectorAll('.departure-airport:checked'))
            .map(checkbox => checkbox.value);
        
        const formData = {
            departure_airports: departureAirports,
            departure_date_from: document.getElementById('departureDateFrom').value,
            departure_date_to: document.getElementById('departureDateTo').value,
            min_stay_duration: parseInt(document.getElementById('minStayDuration').value),
            include_weather: document.getElementById('includeWeather').checked,
            include_accommodations: document.getElementById('includeAccommodations').checked
        };
        
        // Add theme or country-based search
        if (this.selectedTheme) {
            formData.theme = this.selectedTheme;
        } else {
            const destinationCountries = Array.from(document.getElementById('destinationCountries').selectedOptions)
                .map(option => option.value);
            const coastalFilter = document.getElementById('coastalFilter').value;
            
            formData.target_countries = destinationCountries;
            formData.coastal_only = coastalFilter === '' ? null : coastalFilter === 'true';
        }
        
        // Add activities option
        formData.include_activities = document.getElementById('includeActivities').checked;
        
        // Add activity filters if activities are enabled
        if (formData.include_activities) {
            // Activity categories
            const activityCategories = Array.from(document.querySelectorAll('input[id^="category-"]:checked'))
                .map(checkbox => checkbox.value);
            if (activityCategories.length > 0) {
                formData.activity_categories = activityCategories;
            }
            
            // Activity price ranges
            const activityPriceRanges = Array.from(document.querySelectorAll('input[id^="price-"]:checked'))
                .map(checkbox => checkbox.value);
            if (activityPriceRanges.length > 0) {
                formData.activity_price_range = activityPriceRanges;
            }
            
            // Minimum rating
            const minRating = document.getElementById('minActivityRating').value;
            if (minRating) {
                formData.activity_min_rating = minRating;
            }
        }
        
        return formData;
    }
    
    validateForm(formData) {
        if (formData.departure_airports.length === 0) {
            this.showAlert('Veuillez sélectionner au moins un aéroport de départ.', 'warning');
            return false;
        }
        
        if (!this.selectedTheme && formData.target_countries.length === 0) {
            this.showAlert('Veuillez sélectionner au moins un pays de destination.', 'warning');
            return false;
        }
        
        if (!formData.departure_date_from || !formData.departure_date_to) {
            this.showAlert('Veuillez sélectionner les dates de départ.', 'warning');
            return false;
        }
        
        if (new Date(formData.departure_date_from) > new Date(formData.departure_date_to)) {
            this.showAlert('La date de début doit être antérieure à la date de fin.', 'warning');
            return false;
        }
        
        return true;
    }
    
    hideAllSections() {
        document.getElementById('welcomeMessage').classList.add('d-none');
        document.getElementById('resultsContainer').classList.add('d-none');
        document.getElementById('noResults').classList.add('d-none');
        document.getElementById('loadingSpinner').classList.add('d-none');
    }
    
    showLoading() {
        this.hideAllSections();
        document.getElementById('loadingSpinner').classList.remove('d-none');
    }
    
    hideLoading() {
        document.getElementById('loadingSpinner').classList.add('d-none');
    }
    
    displayResults() {
        if (this.currentResults.length === 0) {
            this.showNoResults();
            return;
        }
        
        this.hideAllSections();
        document.getElementById('resultsContainer').classList.remove('d-none');
        
        // Update results header
        const title = document.getElementById('resultsTitle');
        const subtitle = document.getElementById('resultsSubtitle');
        
        title.textContent = `${this.currentResults.length} vol${this.currentResults.length > 1 ? 's' : ''} trouvé${this.currentResults.length > 1 ? 's' : ''}`;
        
        if (this.selectedTheme) {
            const themeData = this.themes[this.selectedTheme];
            subtitle.textContent = `Thème: ${themeData.name} • Prix à partir de €${Math.min(...this.currentResults.map(r => r.total_price))}`;
        } else {
            subtitle.textContent = `Prix à partir de €${Math.min(...this.currentResults.map(r => r.total_price))}`;
        }
        
        this.displayedResults = 0;
        document.getElementById('resultsGrid').innerHTML = '';
        this.loadMoreResults();
    }
    
    loadMoreResults() {
        const container = document.getElementById('resultsGrid');
        const endIndex = Math.min(this.displayedResults + this.resultsPerPage, this.currentResults.length);
        
        for (let i = this.displayedResults; i < endIndex; i++) {
            const flight = this.currentResults[i];
            const flightCard = this.createFlightCard(flight, i);
            container.appendChild(flightCard);
        }
        
        this.displayedResults = endIndex;
        
        // Show/hide load more button
        const loadMoreContainer = document.getElementById('loadMoreContainer');
        if (this.displayedResults < this.currentResults.length) {
            loadMoreContainer.classList.remove('d-none');
        } else {
            loadMoreContainer.classList.add('d-none');
        }
    }
    
    createFlightCard(flight, index) {
        const card = document.createElement('div');
        card.className = 'flight-card fade-in';
        card.style.animationDelay = `${(index % this.resultsPerPage) * 0.1}s`;
        
        const destinationInfo = flight.destination_info;
        const destinationBadge = destinationInfo.coastal 
            ? `<span class="coastal-badge"><i class="bi bi-water me-1"></i>${destinationInfo.sea}</span>`
            : `<span class="inland-badge"><i class="bi bi-mountain me-1"></i>Intérieur</span>`;
        
        // Theme badges
        const themeBadges = destinationInfo.themes ? 
            destinationInfo.themes.map(theme => {
                const themeData = this.themes[theme];
                if (themeData) {
                    return `<span class="theme-badge" style="background-color: ${themeData.color}20; border-color: ${themeData.color}">
                        ${themeData.name.split(' ')[0]}
                    </span>`;
                }
                return '';
            }).join('') : '';
        
        const weatherSection = flight.weather ? this.createWeatherSection(flight.weather) : '';
        const accommodationSection = flight.accommodations ? this.createAccommodationSection(flight.accommodations) : '';
        const activitiesSection = flight.activities ? this.createActivitiesSection(flight.activities) : '';
        
        card.innerHTML = `
            <div class="flight-card-header">
                <div class="flight-route">
                    <div class="airport-info">
                        <div class="airport-code">${flight.origin}</div>
                        <small class="airport-name">${flight.origin_name}</small>
                    </div>
                    <div class="route-arrow">
                        <i class="bi bi-airplane"></i>
                    </div>
                    <div class="airport-info">
                        <div class="airport-code">${flight.destination}</div>
                        <small class="airport-name">${destinationInfo.name}</small>
                    </div>
                </div>
                
                <div class="price-section">
                    <div class="price-badge">€${flight.total_price}</div>
                    <small class="price-breakdown">Aller: €${flight.outbound_price} • Retour: €${flight.inbound_price}</small>
                </div>
            </div>
            
            <div class="flight-details">
                <div class="flight-times">
                    <div class="time-info">
                        <span class="time-label">Départ</span>
                        <span class="time-value">${this.formatDate(flight.departure_time)}</span>
                    </div>
                    <div class="time-info">
                        <span class="time-label">Retour</span>
                        <span class="time-value">${this.formatDate(flight.return_time)}</span>
                    </div>
                </div>
                
                <div class="destination-tags">
                    ${destinationBadge}
                    ${themeBadges}
                </div>
            </div>
            
            ${weatherSection}
            ${accommodationSection}
            ${activitiesSection}
            
            <div class="flight-actions">
                <button class="btn btn-outline-primary btn-sm" onclick="app.showFlightDetails(${index})">
                    <i class="bi bi-info-circle me-1"></i>Détails
                </button>
                <button class="btn btn-primary" onclick="app.goToDestination(${index})">
                    <i class="bi bi-geo-alt me-1"></i>Voir la destination
                </button>
            </div>
        `;
        
        return card;
    }
    
    createWeatherSection(weather) {
        if (!weather) return '';
        
        return `
            <div class="weather-section">
                <h6><i class="bi bi-cloud-sun me-2"></i>Météo sur place</h6>
                <div class="weather-details">
                    <div class="weather-main">
                        <span class="temperature">${Math.round(weather.main.temp)}°C</span>
                        <span class="description">${weather.weather[0].description}</span>
                    </div>
                    <div class="weather-extra">
                        <small>Ressenti: ${Math.round(weather.main.feels_like)}°C</small>
                        <small>Humidité: ${weather.main.humidity}%</small>
                        <small>Vent: ${weather.wind ? weather.wind.speed : 'N/A'} m/s</small>
                    </div>
                </div>
            </div>
        `;
    }
    
    createAccommodationSection(accommodations) {
        if (!accommodations || !accommodations.booking_links) return '';
        
        return `
            <div class="accommodation-section">
                <h6><i class="bi bi-house me-2"></i>Hébergements</h6>
                <div class="booking-links">
                    ${accommodations.booking_links.map(link => `
                        <a href="${link.url}" target="_blank" class="btn btn-outline-secondary btn-sm">
                            <i class="bi bi-${this.getIconForPlatform(link.type)} me-1"></i>${link.name}
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    createActivitiesSection(activities) {
        if (!activities) return '';
        
        // Handle both dict (organized by category) and list formats
        let activitiesHTML = '';
        
        if (typeof activities === 'object' && !Array.isArray(activities)) {
            // Activities organized by category
            const categoryIcons = {
                'gastronomie': '🍽️',
                'culture': '🏛️',
                'nature': '🌳',
                'loisirs': '🛍️',
                'detente': '🧘'
            };
            
            const categoryNames = {
                'gastronomie': 'Gastronomie',
                'culture': 'Culture & Histoire',
                'nature': 'Nature & Aventure',
                'loisirs': 'Loisirs & Vie locale',
                'detente': 'Bien-être & Détente'
            };
            
            let totalActivities = 0;
            for (const [category, categoryActivities] of Object.entries(activities)) {
                if (categoryActivities && categoryActivities.length > 0) {
                    totalActivities += categoryActivities.length;
                    const topActivities = categoryActivities.slice(0, 2); // Show max 2 per category
                    
                    activitiesHTML += `
                        <div class="activity-category">
                            <h6 class="activity-category-title">
                                <span class="category-icon">${categoryIcons[category] || '📍'}</span>
                                ${categoryNames[category] || category}
                            </h6>
                            <div class="activity-list">
                                ${topActivities.map(activity => `
                                    <div class="activity-item">
                                        <div class="activity-name">${activity.name}</div>
                                        <div class="activity-meta">
                                            ${activity.rating ? `<span class="rating"><i class="bi bi-star-fill"></i> ${activity.rating}</span>` : ''}
                                            ${activity.price_range ? `<span class="price">${activity.price_range}</span>` : ''}
                                        </div>
                                        ${activity.description ? `<div class="activity-description">${activity.description.substring(0, 80)}...</div>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
            }
            
            if (totalActivities === 0) return '';
            
            return `
                <div class="activities-section">
                    <h6><i class="bi bi-star me-2"></i>Activités populaires (${totalActivities})</h6>
                    <div class="activities-preview">
                        ${activitiesHTML}
                        <div class="activities-footer">
                            <small class="text-muted">Voir toutes les activités sur la page destination</small>
                        </div>
                    </div>
                </div>
            `;
        } else if (Array.isArray(activities) && activities.length > 0) {
            // Activities as simple list
            const topActivities = activities.slice(0, 4);
            
            activitiesHTML = topActivities.map(activity => `
                <div class="activity-item">
                    <div class="activity-name">${activity.name}</div>
                    <div class="activity-meta">
                        ${activity.rating ? `<span class="rating"><i class="bi bi-star-fill"></i> ${activity.rating}</span>` : ''}
                        ${activity.price_range ? `<span class="price">${activity.price_range}</span>` : ''}
                    </div>
                </div>
            `).join('');
            
            return `
                <div class="activities-section">
                    <h6><i class="bi bi-star me-2"></i>Activités populaires (${activities.length})</h6>
                    <div class="activities-preview">
                        ${activitiesHTML}
                    </div>
                </div>
            `;
        }
        
        return '';
    }
    
    getIconForPlatform(type) {
        const icons = {
            'booking_platform': 'building',
            'hostel_platform': 'house',
            'apartment_platform': 'house-door'
        };
        return icons[type] || 'house';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    sortResults(sortBy) {
        switch (sortBy) {
            case 'price':
                this.currentResults.sort((a, b) => a.total_price - b.total_price);
                break;
            case 'departure':
                this.currentResults.sort((a, b) => new Date(a.departure_time) - new Date(b.departure_time));
                break;
            case 'duration':
                this.currentResults.sort((a, b) => {
                    const durationA = new Date(a.return_time) - new Date(a.departure_time);
                    const durationB = new Date(b.return_time) - new Date(b.departure_time);
                    return durationA - durationB;
                });
                break;
        }
        
        this.displayResults();
    }
    
    updateSortButtons(activeBtn) {
        document.querySelectorAll('[data-sort]').forEach(btn => btn.classList.remove('active'));
        activeBtn.classList.add('active');
    }
    
    goToDestination(index) {
        const flight = this.currentResults[index];
        
        // Build query parameters for the destination page
        const params = new URLSearchParams({
            departure_airport: flight.origin,
            destination_airport: flight.destination,
            departure_date: flight.departure_time.split('T')[0],
            return_date: flight.return_time.split('T')[0],
            total_price: flight.total_price,
            outbound_price: flight.outbound_price,
            inbound_price: flight.inbound_price,
            ryanair_link: flight.ryanair_link || ''
        });
        
        // Redirect to destination page
        window.location.href = `/destination/${flight.destination}?${params.toString()}`;
    }
    
    showFlightDetails(index) {
        const flight = this.currentResults[index];
        const modalContent = document.getElementById('flightDetailsContent');
        
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="bi bi-airplane-engines me-2"></i>Vol Aller</h6>
                    <div class="flight-detail-item">
                        <strong>De:</strong> ${flight.origin} (${flight.origin_name})
                    </div>
                    <div class="flight-detail-item">
                        <strong>Vers:</strong> ${flight.destination} (${flight.destination_info.name})
                    </div>
                    <div class="flight-detail-item">
                        <strong>Départ:</strong> ${this.formatDate(flight.departure_time)}
                    </div>
                    <div class="flight-detail-item">
                        <strong>Prix:</strong> €${flight.outbound_price}
                    </div>
                </div>
                <div class="col-md-6">
                    <h6><i class="bi bi-airplane-engines-fill me-2"></i>Vol Retour</h6>
                    <div class="flight-detail-item">
                        <strong>De:</strong> ${flight.destination} (${flight.destination_info.name})
                    </div>
                    <div class="flight-detail-item">
                        <strong>Vers:</strong> ${flight.origin} (${flight.origin_name})
                    </div>
                    <div class="flight-detail-item">
                        <strong>Départ:</strong> ${this.formatDate(flight.return_time)}
                    </div>
                    <div class="flight-detail-item">
                        <strong>Prix:</strong> €${flight.inbound_price}
                    </div>
                </div>
            </div>
            <hr>
            <div class="text-center">
                <h4 class="text-success mb-3">Prix Total: €${flight.total_price}</h4>
                <a href="${flight.ryanair_link || 'https://www.ryanair.com'}" target="_blank" class="btn btn-success btn-lg">
                    <i class="bi bi-airplane me-2"></i>Réserver sur Ryanair
                </a>
                <div class="mt-2">
                    <small class="text-muted">Le lien vous amènera directement sur la page de réservation avec vos dates pré-remplies</small>
                </div>
            </div>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('flightDetailsModal'));
        modal.show();
    }
    
    showNoResults() {
        this.hideAllSections();
        document.getElementById('noResults').classList.remove('d-none');
    }
    
    showAlert(message, type = 'danger') {
        // Create bootstrap alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    showError(message) {
        this.showAlert(`Erreur: ${message}`, 'danger');
    }
}

// Initialize the search app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SearchApp();
});