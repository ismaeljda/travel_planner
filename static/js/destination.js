// Destination Page JavaScript

class DestinationManager {
    constructor() {
        this.allActivities = [];
        this.filteredActivities = [];
        this.filters = {
            category: '',
            price: '',
            rating: ''
        };
        
        this.init();
    }
    
    init() {
        this.collectActivities();
        this.bindFilterEvents();
        this.setupActivityInteractions();
    }
    
    collectActivities() {
        const activityCards = document.querySelectorAll('.activity-card');
        this.allActivities = Array.from(activityCards).map(card => ({
            element: card,
            category: card.dataset.category || '',
            price: card.dataset.price || '',
            rating: parseFloat(card.dataset.rating) || 0,
            name: card.querySelector('.activity-name')?.textContent || ''
        }));
        
        this.filteredActivities = [...this.allActivities];
        this.updateActivitiesCount();
    }
    
    bindFilterEvents() {
        // Category filter buttons
        const categoryButtons = document.querySelectorAll('.filter-buttons button[data-category]');
        categoryButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Remove active class from all buttons
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                const category = e.target.dataset.category;
                this.showCategoryActivities(category);
            });
        });
    }
    
    showCategoryActivities(category) {
        const categorySections = document.querySelectorAll('.activity-category-section');
        
        if (category === 'all') {
            // Show all category sections
            categorySections.forEach(section => {
                section.style.display = 'block';
            });
        } else {
            // Hide all sections
            categorySections.forEach(section => {
                section.style.display = 'none';
            });
            
            // Show only the selected category
            const targetSection = document.querySelector(`[data-category="${category}"]`);
            if (targetSection) {
                targetSection.style.display = 'block';
            }
        }
        
        // Update count
        this.updateActivitiesCount(category);
    }
    
    updateActivitiesCount(activeCategory = 'all') {
        const countElement = document.getElementById('activitiesCount');
        if (countElement) {
            let count = 0;
            
            if (activeCategory === 'all') {
                // Count all visible activities
                const categorySections = document.querySelectorAll('.activity-category-section[data-category]');
                categorySections.forEach(section => {
                    if (section.style.display !== 'none') {
                        count += section.querySelectorAll('.activity-card').length;
                    }
                });
            } else {
                // Count activities in active category
                const activeSection = document.querySelector(`[data-category="${activeCategory}"]`);
                if (activeSection) {
                    count = activeSection.querySelectorAll('.activity-card').length;
                }
            }
            
            countElement.textContent = count;
        }
    }
    
    applyFilters() {
        this.filteredActivities = this.allActivities.filter(activity => {
            // Category filter
            if (this.filters.category && activity.category !== this.filters.category) {
                return false;
            }
            
            // Price filter
            if (this.filters.price) {
                if (this.filters.price === 'free' && activity.price !== 'free') {
                    return false;
                }
                if (this.filters.price !== 'free' && activity.price !== this.filters.price) {
                    return false;
                }
            }
            
            // Rating filter
            if (this.filters.rating) {
                const minRating = parseFloat(this.filters.rating);
                if (activity.rating < minRating) {
                    return false;
                }
            }
            
            return true;
        });
        
        this.updateDisplay();
        this.updateActivitiesCount();
    }
    
    updateDisplay() {
        const activitiesGrid = document.getElementById('activitiesGrid');
        const noActivities = document.getElementById('noActivities');
        
        // Hide all activities first
        this.allActivities.forEach(activity => {
            activity.element.classList.add('filtered-out');
            activity.element.classList.remove('filtered-in');
        });
        
        // Show filtered activities with animation delay
        if (this.filteredActivities.length > 0) {
            this.filteredActivities.forEach((activity, index) => {
                setTimeout(() => {
                    activity.element.classList.remove('filtered-out');
                    activity.element.classList.add('filtered-in');
                }, index * 50); // Staggered animation
            });
            
            if (activitiesGrid) activitiesGrid.classList.remove('d-none');
            if (noActivities) noActivities.classList.add('d-none');
        } else {
            if (activitiesGrid) activitiesGrid.classList.add('d-none');
            if (noActivities) noActivities.classList.remove('d-none');
        }
    }
    
    
    resetFilters() {
        // Reset filter values
        this.filters = {
            category: '',
            price: '',
            rating: ''
        };
        
        // Reset form elements
        const categoryFilter = document.getElementById('categoryFilter');
        const priceFilter = document.getElementById('priceFilter');
        const ratingFilter = document.getElementById('ratingFilter');
        
        if (categoryFilter) categoryFilter.value = '';
        if (priceFilter) priceFilter.value = '';
        if (ratingFilter) ratingFilter.value = '';
        
        // Show all activities
        this.filteredActivities = [...this.allActivities];
        this.updateDisplay();
        this.updateActivitiesCount();
    }
    
    setupActivityInteractions() {
        // Add click interactions for activity cards
        this.allActivities.forEach(activity => {
            activity.element.addEventListener('click', () => {
                this.showActivityDetails(activity);
            });
        });
    }
    
    showActivityDetails(activity) {
        // Create modal or expand card with more details
        console.log('Showing details for:', activity.name);
        // This could open a modal, redirect to a detail page, or expand the card
    }
}

// Global functions for button clicks
function applyFilters() {
    if (window.destinationManager) {
        window.destinationManager.applyFilters();
    }
}

function resetFilters() {
    if (window.destinationManager) {
        window.destinationManager.resetFilters();
    }
}

// Utility functions for enhanced interactions
function shareDestination() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            text: 'Découvre cette destination avec FlightFinder!',
            url: window.location.href
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            showNotification('Lien copié dans le presse-papiers!', 'success');
        });
    }
}

function bookFlight() {
    const ryanairLink = document.querySelector('a[href*="ryanair"]');
    if (ryanairLink) {
        window.open(ryanairLink.href, '_blank');
    }
}

function showNotification(message, type = 'info') {
    // Create and show a notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Enhanced search functionality
function searchActivities(query) {
    if (!window.destinationManager) return;
    
    const searchQuery = query.toLowerCase();
    const manager = window.destinationManager;
    
    manager.filteredActivities = manager.allActivities.filter(activity => {
        const nameMatch = activity.name.toLowerCase().includes(searchQuery);
        const categoryMatch = activity.category.toLowerCase().includes(searchQuery);
        
        return nameMatch || categoryMatch;
    });
    
    manager.updateDisplay();
    manager.updateActivitiesCount();
}

// Smooth scroll to activities section
function scrollToActivities() {
    const activitiesGrid = document.getElementById('activitiesGrid');
    if (activitiesGrid) {
        activitiesGrid.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Add CSS animations dynamically
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
        
        .notification-toast {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    `;
    document.head.appendChild(style);
}

// Hotel Search Manager
class HotelManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupDateDefaults();
        this.bindHotelEvents();
    }
    
    setupDateDefaults() {
        // Set default dates
        const checkinInput = document.getElementById('hotelCheckin');
        const checkoutInput = document.getElementById('hotelCheckout');
        
        if (checkinInput && checkoutInput) {
            // Try to get flight dates from URL params if coming from search results
            const urlParams = new URLSearchParams(window.location.search);
            const flightDeparture = urlParams.get('departure_time');
            const flightReturn = urlParams.get('return_time');
            
            let checkin, checkout;
            
            if (flightDeparture && flightReturn) {
                // Use flight dates if available
                checkin = new Date(flightDeparture.split('T')[0]);
                checkout = new Date(flightReturn.split('T')[0]);
            } else {
                // Default dates: 7 days from now for 3 nights
                const today = new Date();
                checkin = new Date(today);
                checkin.setDate(today.getDate() + 7);
                checkout = new Date(checkin);
                checkout.setDate(checkin.getDate() + 3);
            }
            
            checkinInput.value = checkin.toISOString().split('T')[0];
            checkoutInput.value = checkout.toISOString().split('T')[0];
        }
    }
    
    bindHotelEvents() {
        const hotelForm = document.getElementById('hotelSearchForm');
        const resetButton = document.getElementById('resetHotelFilters');
        
        if (hotelForm) {
            hotelForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.searchHotels();
            });
        }
        
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                this.resetHotelFilters();
            });
        }
    }
    
    async searchHotels() {
        const loadingDiv = document.getElementById('hotelsLoading');
        const resultsDiv = document.getElementById('hotelsResults');
        const noHotelsDiv = document.getElementById('noHotels');
        
        // Show loading state
        loadingDiv.classList.remove('d-none');
        resultsDiv.innerHTML = '';
        noHotelsDiv.classList.add('d-none');
        
        try {
            // Get search parameters
            const params = this.getSearchParams();
            
            // Build query string
            const queryString = new URLSearchParams(params).toString();
            
            // Make API request
            const response = await fetch(`/api/hotels/search?${queryString}`);
            const data = await response.json();
            
            loadingDiv.classList.add('d-none');
            
            if (data.success && data.data.hotels && data.data.hotels.length > 0) {
                this.displayHotels(data.data.hotels);
            } else {
                this.showNoHotelsMessage();
            }
            
        } catch (error) {
            console.error('Hotel search error:', error);
            loadingDiv.classList.add('d-none');
            this.showNoHotelsMessage();
        }
    }
    
    getSearchParams() {
        const params = {};
        
        params.destination = document.getElementById('hotelDestination').value;
        params.checkin = document.getElementById('hotelCheckin').value;
        params.checkout = document.getElementById('hotelCheckout').value;
        params.adults = document.getElementById('hotelAdults').value;
        
        // Optional filters
        const priceRange = document.getElementById('hotelPriceRange').value;
        if (priceRange) {
            const [min, max] = priceRange.split('-');
            if (min) params.price_min = min;
            if (max) params.price_max = max;
        }
        
        const hotelClass = document.getElementById('hotelClass').value;
        if (hotelClass) params.hotel_class = hotelClass;
        
        const hotelType = document.getElementById('hotelType').value;
        if (hotelType) params.hotel_type = hotelType;
        
        const freeCancellation = document.getElementById('hotelFreeCancellation').checked;
        if (freeCancellation) params.free_cancellation = 'true';
        
        const sort = document.getElementById('hotelSort').value;
        if (sort) params.sort = sort;
        
        return params;
    }
    
    displayHotels(hotels) {
        const resultsDiv = document.getElementById('hotelsResults');
        
        let hotelsHtml = '<div class="hotels-grid">';
        
        hotels.forEach(hotel => {
            hotelsHtml += `
                <div class="hotel-card">
                    ${hotel.image ? `<div class="hotel-image">
                        <img src="${hotel.image}" alt="${hotel.name}">
                    </div>` : ''}
                    <div class="hotel-content">
                        <div class="hotel-header">
                            <div class="hotel-title-section">
                                <h5 class="hotel-name">${hotel.name}</h5>
                                <div class="hotel-type-badge">
                                    <span class="badge bg-secondary">${hotel.type || 'Hotel'}</span>
                                </div>
                            </div>
                            <div class="hotel-meta">
                                ${hotel.stars && hotel.stars > 0 ? `<div class="hotel-stars">
                                    ${'⭐'.repeat(hotel.stars)} (${hotel.stars} étoiles)
                                </div>` : hotel.stars_display ? `<div class="hotel-stars-text">
                                    ${hotel.stars_display}
                                </div>` : ''}
                                ${hotel.rating ? `<div class="hotel-rating">
                                    <i class="bi bi-star-fill text-warning"></i>
                                    <span>${hotel.rating}</span>
                                    ${hotel.reviews ? `<small class="text-muted">(${hotel.reviews} avis)</small>` : ''}
                                </div>` : ''}
                            </div>
                        </div>
                        
                        ${hotel.description ? `<p class="hotel-description">${hotel.description.substring(0, 200)}...</p>` : ''}
                        
                        ${hotel.amenities && hotel.amenities.length > 0 ? `
                        <div class="hotel-amenities mb-3">
                            ${hotel.amenities.slice(0, 5).map(amenity => 
                                `<span class="badge bg-light text-dark me-1 mb-1">${amenity}</span>`
                            ).join('')}
                        </div>` : ''}
                        
                        <div class="hotel-footer">
                            <div class="hotel-price">
                                ${hotel.price ? `<span class="price-tag">${hotel.price}/nuit</span>` : '<span class="price-tag">Prix sur demande</span>'}
                                ${hotel.free_cancellation ? '<div class="free-cancellation"><small class="text-success"><i class="bi bi-check-circle me-1"></i>Annulation gratuite</small></div>' : ''}
                            </div>
                            <div class="hotel-actions">
                                <button class="btn btn-outline-primary btn-sm me-2" onclick="addHotelToTrip('${hotel.name}', '${hotel.price || '0'}', '${hotel.image || ''}', '${hotel.rating || '0'}')">
                                    <i class="bi bi-plus-circle me-1"></i>Ajouter au séjour
                                </button>
                                ${hotel.details_url ? `
                                <a href="${hotel.details_url}" target="_blank" class="btn btn-outline-info btn-sm me-2">
                                    <i class="bi bi-info-circle me-1"></i>Plus d'infos
                                </a>` : ''}
                                ${hotel.booking_url ? `
                                <a href="${hotel.booking_url}" target="_blank" class="btn btn-primary btn-sm">
                                    <i class="bi bi-box-arrow-up-right me-1"></i>Réserver maintenant
                                </a>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        hotelsHtml += '</div>';
        resultsDiv.innerHTML = hotelsHtml;
    }
    
    showNoHotelsMessage() {
        const noHotelsDiv = document.getElementById('noHotels');
        noHotelsDiv.classList.remove('d-none');
    }
    
    resetHotelFilters() {
        document.getElementById('hotelPriceRange').value = '';
        document.getElementById('hotelClass').value = '';
        document.getElementById('hotelType').value = '';
        document.getElementById('hotelFreeCancellation').checked = false;
        document.getElementById('hotelSort').value = '';
        
        // Reset results
        document.getElementById('hotelsResults').innerHTML = '';
        document.getElementById('noHotels').classList.add('d-none');
        
        this.setupDateDefaults(); // Reset dates to defaults
    }
}

// Trip Manager for panier/séjour functionality
class TripManager {
    constructor() {
        this.trip = {
            flight: null,
            hotel: null,
            activities: [],
            totalPrice: 0
        };
        this.loadTrip();
        this.updateTripDisplay();
    }
    
    addHotelToTrip(name, price, image, rating) {
        this.trip.hotel = {
            name,
            price: this.extractPriceNumber(price),
            image,
            rating: parseFloat(rating) || 0,
            priceDisplay: price
        };
        this.saveTrip();
        this.updateTripDisplay();
        this.showNotification('Hôtel ajouté au séjour !', 'success');
    }
    
    addFlightToTrip(origin, destination, price, departureTime, returnTime, ryanairLink) {
        this.trip.flight = {
            origin,
            destination,
            price: parseFloat(price) || 0,
            departureTime,
            returnTime,
            ryanairLink
        };
        this.saveTrip();
        this.updateTripDisplay();
        this.showNotification('Vol ajouté au séjour !', 'success');
    }
    
    extractPriceNumber(priceString) {
        if (!priceString) return 0;
        const match = priceString.match(/(\d+)/);
        return match ? parseFloat(match[1]) : 0;
    }
    
    calculateTotalPrice() {
        let total = 0;
        if (this.trip.flight) total += this.trip.flight.price;
        if (this.trip.hotel) total += this.trip.hotel.price;
        // Add activities prices when implemented
        this.trip.totalPrice = total;
        return total;
    }
    
    saveTrip() {
        localStorage.setItem('currentTrip', JSON.stringify(this.trip));
    }
    
    loadTrip() {
        const saved = localStorage.getItem('currentTrip');
        if (saved) {
            this.trip = JSON.parse(saved);
        }
    }
    
    updateTripDisplay() {
        // This will create a floating trip summary
        this.createTripSummary();
    }
    
    createTripSummary() {
        let existingSummary = document.getElementById('tripSummary');
        if (existingSummary) {
            existingSummary.remove();
        }
        
        if (!this.trip.flight && !this.trip.hotel && this.trip.activities.length === 0) {
            return; // Don't show if trip is empty
        }
        
        const total = this.calculateTotalPrice();
        
        const summaryHtml = `
            <div id="tripSummary" class="trip-summary-float">
                <div class="trip-summary-header">
                    <h6><i class="bi bi-suitcase me-2"></i>Mon Séjour</h6>
                    <button class="btn btn-sm btn-outline-light" onclick="window.tripManager.toggleSummary()">
                        <i class="bi bi-chevron-down"></i>
                    </button>
                </div>
                <div class="trip-summary-content" id="tripSummaryContent">
                    ${this.trip.flight ? `
                    <div class="trip-item">
                        <i class="bi bi-airplane"></i>
                        <span>${this.trip.flight.origin} → ${this.trip.flight.destination}</span>
                        <span class="trip-price">${this.trip.flight.price}€</span>
                    </div>` : ''}
                    ${this.trip.hotel ? `
                    <div class="trip-item">
                        <i class="bi bi-building"></i>
                        <span>${this.trip.hotel.name}</span>
                        <span class="trip-price">${this.trip.hotel.priceDisplay}</span>
                    </div>` : ''}
                    <div class="trip-total">
                        <strong>Total: ${total}€</strong>
                    </div>
                    <button class="btn btn-primary btn-sm w-100 mt-2" onclick="window.location.href='/recap'">
                        <i class="bi bi-eye me-1"></i>Voir le récapitulatif
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', summaryHtml);
    }
    
    toggleSummary() {
        const content = document.getElementById('tripSummaryContent');
        const icon = document.querySelector('#tripSummary .bi-chevron-down, #tripSummary .bi-chevron-up');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            icon.className = 'bi bi-chevron-down';
        } else {
            content.style.display = 'none';
            icon.className = 'bi bi-chevron-up';
        }
    }
    
    showNotification(message, type = 'info') {
        // Reuse the existing notification function
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            alert(message);
        }
    }
}

// Global functions for adding items to trip
function addHotelToTrip(name, price, image, rating) {
    if (window.tripManager) {
        window.tripManager.addHotelToTrip(name, price, image, rating);
    }
}

function addFlightToTrip(origin, destination, price, departureTime, returnTime, ryanairLink) {
    if (window.tripManager) {
        window.tripManager.addFlightToTrip(origin, destination, price, departureTime, returnTime, ryanairLink);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the destination manager
    window.destinationManager = new DestinationManager();
    
    // Initialize the hotel manager
    window.hotelManager = new HotelManager();
    
    // Initialize the trip manager
    window.tripManager = new TripManager();
    
    // Add animation styles
    addAnimationStyles();
    
    // Add loading states for any async operations
    const loadingElements = document.querySelectorAll('.loading-placeholder');
    loadingElements.forEach(element => {
        setTimeout(() => {
            element.classList.add('loaded');
        }, Math.random() * 1000 + 500);
    });
    
    console.log('Destination page initialized with hotel search and trip manager');
});