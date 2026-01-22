// ==========================================
// LANDING PAGE JAVASCRIPT
// ==========================================

document.addEventListener('DOMContentLoaded', function () {

    // Initialize landing page components
    initParticles();
    initTestimonialsSlider();
    initFloatingAnimation();

});

// Hero section particles
function initParticles() {
    const container = document.getElementById('heroParticles');
    if (!container) return;

    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        createParticle(container);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    const size = Math.random() * 6 + 2;
    const left = Math.random() * 100;
    const delay = Math.random() * 5;
    const duration = Math.random() * 10 + 10;

    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(255, 107, 53, ${Math.random() * 0.5 + 0.2});
        border-radius: 50%;
        left: ${left}%;
        bottom: -20px;
        animation: particleFloat ${duration}s linear infinite;
        animation-delay: ${delay}s;
        box-shadow: 0 0 ${size * 2}px rgba(255, 107, 53, 0.3);
    `;

    container.appendChild(particle);
}

// Add particle animation keyframes
const particleStyle = document.createElement('style');
particleStyle.textContent = `
    @keyframes particleFloat {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(720deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(particleStyle);

// Infinite testimonials slider
function initTestimonialsSlider() {
    const slider = document.querySelector('.testimonials-slider');
    if (!slider) return;

    // Clone testimonial cards for infinite scroll
    const cards = slider.querySelectorAll('.testimonial-card');
    cards.forEach(card => {
        const clone = card.cloneNode(true);
        slider.appendChild(clone);
    });

    // Pause animation on hover
    slider.addEventListener('mouseenter', () => {
        slider.style.animationPlayState = 'paused';
    });

    slider.addEventListener('mouseleave', () => {
        slider.style.animationPlayState = 'running';
    });
}

// Floating badges animation enhancement
function initFloatingAnimation() {
    const badges = document.querySelectorAll('.float-badge');

    badges.forEach((badge, index) => {
        badge.addEventListener('mouseenter', () => {
            badge.style.transform = 'scale(1.1) translateY(-5px)';
            badge.style.boxShadow = '0 10px 30px rgba(255, 107, 53, 0.3)';
        });

        badge.addEventListener('mouseleave', () => {
            badge.style.transform = '';
            badge.style.boxShadow = '';
        });
    });
}

// Cylinder 3D mouse interaction
const cylinderContainer = document.querySelector('.cylinder-3d');
if (cylinderContainer) {
    document.addEventListener('mousemove', (e) => {
        const { clientX, clientY } = e;
        const { innerWidth, innerHeight } = window;

        const xRotation = ((clientY / innerHeight) - 0.5) * 10;
        const yRotation = ((clientX / innerWidth) - 0.5) * 15;

        cylinderContainer.style.transform = `
            translateY(${Math.sin(Date.now() / 500) * 10}px)
            rotateX(${xRotation}deg)
            rotateY(${yRotation}deg)
        `;
    });
}

// Navbar active section highlighting
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

function highlightNavLink() {
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');

        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}

window.addEventListener('scroll', highlightNavLink);

// Typing effect for hero text (optional enhancement)
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Intersection Observer for fade-in animations
const fadeElements = document.querySelectorAll('[data-fade]');

const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-visible');
            fadeObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

fadeElements.forEach(el => fadeObserver.observe(el));

// Add fade-in styles
const fadeStyle = document.createElement('style');
fadeStyle.textContent = `
    [data-fade] {
        opacity: 0;
        transform: translateY(30px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    
    [data-fade].fade-in-visible {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(fadeStyle);
