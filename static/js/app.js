// Flight Search App JavaScript

class FlightSearchApp {
    constructor() {
        this.currentResults = [];
        this.displayedResults = 0;
        this.resultsPerPage = 10;
        this.countries = {};
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCountryData();
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
                // Update active button
                document.querySelectorAll('[data-sort]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
        
        // Load more button
        document.getElementById('loadMoreBtn').addEventListener('click', () => {
            this.loadMoreResults();
        });
    }
    
    async loadCountryData() {
        try {
            // Countries data is already available in the template
            // This method is here for future API-based loading if needed
        } catch (error) {
            console.error('Error loading country data:', error);
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
                countryDiv.className = 'mb-2';
                countryDiv.innerHTML = `
                    <small class="text-muted fw-bold">${this.getCountryName(countryCode)}</small>
                    <div class="airport-checkboxes">
                        ${Object.entries(airports).map(([code, name]) => `
                            <div class="form-check form-check-inline">
                                <input class="form-check-input departure-airport" type="checkbox" 
                                       value="${code}" id="dep_${code}" checked>
                                <label class="form-check-label" for="dep_${code}">
                                    <small>${code}</small>
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
        
        const destinationCountries = Array.from(document.getElementById('destinationCountries').selectedOptions)
            .map(option => option.value);
        
        const coastalFilter = document.getElementById('coastalFilter').value;
        
        return {
            departure_airports: departureAirports,
            target_countries: destinationCountries,
            departure_date_from: document.getElementById('departureDateFrom').value,
            departure_date_to: document.getElementById('departureDateTo').value,
            min_stay_duration: parseInt(document.getElementById('minStayDuration').value),
            coastal_only: coastalFilter === '' ? null : coastalFilter === 'true',
            include_weather: document.getElementById('includeWeather').checked,
            include_accommodations: document.getElementById('includeAccommodations').checked
        };
    }
    
    validateForm(formData) {
        if (formData.departure_airports.length === 0) {
            alert('Veuillez sélectionner au moins un aéroport de départ.');
            return false;
        }
        
        if (formData.target_countries.length === 0) {
            alert('Veuillez sélectionner au moins un pays de destination.');
            return false;
        }
        
        if (!formData.departure_date_from || !formData.departure_date_to) {
            alert('Veuillez sélectionner les dates de départ.');
            return false;
        }
        
        if (new Date(formData.departure_date_from) > new Date(formData.departure_date_to)) {
            alert('La date de début doit être antérieure à la date de fin.');
            return false;
        }
        
        return true;
    }
    
    showLoading() {
        document.getElementById('welcomeMessage').classList.add('d-none');
        document.getElementById('resultsContainer').classList.add('d-none');
        document.getElementById('noResults').classList.add('d-none');
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
        
        document.getElementById('welcomeMessage').classList.add('d-none');
        document.getElementById('noResults').classList.add('d-none');
        document.getElementById('resultsContainer').classList.remove('d-none');
        
        document.getElementById('resultsTitle').textContent = 
            `${this.currentResults.length} vol${this.currentResults.length > 1 ? 's' : ''} trouvé${this.currentResults.length > 1 ? 's' : ''}`;
        
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
        card.className = 'col-12 fade-in';
        card.style.animationDelay = `${index * 0.1}s`;
        
        const destinationBadge = flight.destination_info.coastal 
            ? `<span class="coastal-badge"><i class="bi bi-water me-1"></i>${flight.destination_info.sea}</span>`
            : `<span class="inland-badge"><i class="bi bi-mountain me-1"></i>Intérieur</span>`;
        
        const weatherSection = flight.weather ? this.createWeatherSection(flight.weather) : '';
        const accommodationSection = flight.accommodations ? this.createAccommodationSection(flight.accommodations) : '';
        
        card.innerHTML = `
            <div class="flight-card">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <div class="flight-route">
                            <div class="text-center">
                                <div class="airport-code">${flight.origin}</div>
                                <small class="text-muted">${flight.origin_name}</small>
                            </div>
                            <div class="route-arrow">
                                <i class="bi bi-arrow-right"></i>
                            </div>
                            <div class="text-center">
                                <div class="airport-code">${flight.destination}</div>
                                <small class="text-muted">${flight.destination_info.name}</small>
                            </div>
                        </div>
                        
                        <div class="destination-info">
                            ${destinationBadge}
                        </div>
                        
                        <div class="flight-times">
                            <div class="departure-time">
                                <div class="time-label">Départ</div>
                                <div class="time-value">${this.formatDateTime(flight.departure_time)}</div>
                            </div>
                            <div class="route-arrow">
                                <i class="bi bi-arrow-left-right"></i>
                            </div>
                            <div class="return-time">
                                <div class="time-label">Retour</div>
                                <div class="time-value">${this.formatDateTime(flight.return_time)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4 text-center">
                        <div class="price-badge mb-3">
                            €${flight.total_price}
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-sm" onclick="app.showFlightDetails(${index})">
                                <i class="bi bi-info-circle me-1"></i>Détails
                            </button>
                            <a href="${flight.ryanair_link || 'https://www.ryanair.com'}" target="_blank" class="btn btn-success btn-sm">
                                <i class="bi bi-airplane me-1"></i>Réserver
                            </a>
                        </div>
                    </div>
                </div>
                
                ${weatherSection}
                ${accommodationSection}
            </div>
        `;
        
        return card;
    }
    
    createWeatherSection(weather) {
        console.log('Weather data:', weather); // Debug log
        if (!weather) {
            console.log('No weather data available');
            return '';
        }
        
        return `
            <div class="weather-info mt-3">
                <h6><i class="bi bi-cloud-sun me-2"></i>Météo sur place</h6>
                <div class="row">
                    <div class="col-md-6">
                        <div class="weather-temp">${Math.round(weather.main.temp)}°C</div>
                        <div class="text-muted">${weather.weather[0].description}</div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">
                            Ressenti: ${Math.round(weather.main.feels_like)}°C<br>
                            Humidité: ${weather.main.humidity}%<br>
                            Vent: ${weather.wind ? weather.wind.speed : 'N/A'} m/s
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
    
    createAccommodationSection(accommodations) {
        if (!accommodations || !accommodations.booking_links) return '';
        
        return `
            <div class="accommodation-info mt-3">
                <h6><i class="bi bi-house me-2"></i>Rechercher des hébergements</h6>
                <div class="d-flex gap-2 flex-wrap">
                    ${accommodations.booking_links.map(link => `
                        <a href="${link.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-${this.getIconForPlatform(link.type)} me-1"></i>${link.name}
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    getIconForPlatform(type) {
        const icons = {
            'booking_platform': 'building',
            'hostel_platform': 'house',
            'apartment_platform': 'house-door'
        };
        return icons[type] || 'house';
    }
    
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }) + ' ' + date.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    showFlightDetails(index) {
        const flight = this.currentResults[index];
        const modalContent = document.getElementById('flightDetailsContent');
        
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Vol Aller</h6>
                    <p><strong>De:</strong> ${flight.origin} (${flight.origin_name})</p>
                    <p><strong>Vers:</strong> ${flight.destination} (${flight.destination_info.name})</p>
                    <p><strong>Départ:</strong> ${this.formatDateTime(flight.departure_time)}</p>
                    <p><strong>Prix:</strong> €${flight.outbound_price}</p>
                </div>
                <div class="col-md-6">
                    <h6>Vol Retour</h6>
                    <p><strong>De:</strong> ${flight.destination} (${flight.destination_info.name})</p>
                    <p><strong>Vers:</strong> ${flight.origin} (${flight.origin_name})</p>
                    <p><strong>Départ:</strong> ${this.formatDateTime(flight.return_time)}</p>
                    <p><strong>Prix:</strong> €${flight.inbound_price}</p>
                </div>
            </div>
            <hr>
            <div class="text-center">
                <h5>Prix Total: €${flight.total_price}</h5>
                <a href="${flight.ryanair_link || 'https://www.ryanair.com'}" target="_blank" class="btn btn-success">
                    <i class="bi bi-airplane me-1"></i>Réserver sur Ryanair
                </a>
                <div class="mt-2">
                    <small class="text-muted">Le lien vous amènera directement sur la page de réservation avec vos dates pré-remplies</small>
                </div>
            </div>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('flightDetailsModal'));
        modal.show();
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
    
    showNoResults() {
        document.getElementById('welcomeMessage').classList.add('d-none');
        document.getElementById('resultsContainer').classList.add('d-none');
        document.getElementById('noResults').classList.remove('d-none');
    }
    
    showError(message) {
        alert(`Erreur: ${message}`);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FlightSearchApp();
});