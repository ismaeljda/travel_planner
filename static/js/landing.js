// Landing Page JavaScript - Theme Selection & Navigation

class LandingPage {
    constructor() {
        this.selectedTheme = null;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.animateOnScroll();
    }
    
    bindEvents() {
        // Theme card selection
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const theme = card.dataset.theme;
                this.selectTheme(theme);
            });
        });
        
        // Smooth scroll to themes
        window.scrollToThemes = () => {
            document.getElementById('themes').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        };
        
        // Advanced search toggle
        window.toggleAdvancedSearch = () => {
            // Redirect to advanced search page
            window.location.href = '/search';
        };
    }
    
    selectTheme(theme) {
        this.selectedTheme = theme;
        
        // Add selection effect
        document.querySelectorAll('.theme-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = document.querySelector(`[data-theme="${theme}"]`);
        selectedCard.classList.add('selected');
        
        // Redirect to search with theme
        setTimeout(() => {
            window.location.href = `/search?theme=${theme}`;
        }, 800);
    }
    
    animateOnScroll() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        });
        
        // Observe elements for animation
        document.querySelectorAll('.theme-card, .feature-card, .stat-number').forEach(el => {
            observer.observe(el);
        });
    }
}

// Initialize landing page
document.addEventListener('DOMContentLoaded', () => {
    new LandingPage();
    
    // Add some interactive effects
    addParticleEffect();
    addTypingEffect();
});

// Add particle effect to hero section
function addParticleEffect() {
    const hero = document.querySelector('.hero-section');
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            pointer-events: none;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float-particle ${3 + Math.random() * 4}s ease-in-out infinite;
        `;
        hero.appendChild(particle);
    }
    
    // Add CSS animation for particles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float-particle {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.6; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

// Add typing effect to hero title
function addTypingEffect() {
    const title = document.querySelector('.hero-title');
    const text = title.textContent;
    title.innerHTML = '';
    
    let i = 0;
    const typeWriter = () => {
        if (i < text.length) {
            title.innerHTML += text.charAt(i);
            i++;
            setTimeout(typeWriter, 50);
        }
    };
    
    // Start typing effect after a short delay
    setTimeout(typeWriter, 500);
}

// Add hover sound effects (optional - commented out for now)
/*
function addSoundEffects() {
    const hoverSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmIcBSl+2vLfgycGKWq+8Ni/ZicFP5DS8tiXaswFJAzBqI4CQCcFJOHU5AqJRAwTSLHj3ZhgHws8k9LH0OqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLHj3ZhcGws8k9LL1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLHjxZhEIwU8k9LH0OqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsIGXfJ5P6Laz8KGWqJ5QGKKAkTSLPj3ZhEIwU8k9LH1eqRLgEJCAmRqpWLJAUNLGHH6+mjWRsI');
    
    document.querySelectorAll('.theme-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            hoverSound.currentTime = 0;
            hoverSound.play().catch(() => {}); // Ignore autoplay policy errors
        });
    });
}
*/

// Add some CSS for selected theme state
const selectedStyle = document.createElement('style');
selectedStyle.textContent = `
    .theme-card.selected {
        transform: scale(0.95);
        opacity: 0.8;
        transition: all 0.3s ease;
    }
    
    .theme-card.selected::after {
        content: '✓';
        position: absolute;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .animate-in {
        animation: slideInUp 0.6s ease-out;
    }
`;
document.head.appendChild(selectedStyle);