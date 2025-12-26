/**
 * Scroll Manager Module
 * Handles smooth scrolling, navbar effects, and mobile menu
 */

import { CONSTANTS } from '../core/constants.js';

export class ScrollManager {
    constructor() {
        // Can be extended with dependency injection
    }
    /**
     * Initialize scroll-related functionality
     */
    init() {
        this.initSmoothScroll();
        this.initNavbarScroll();
        this.initBurgerMenu();
    }

    /**
     * Initialize smooth scroll for anchor links
     */
    initSmoothScroll() {
        const anchorLinks = document.querySelectorAll(CONSTANTS.SELECTORS.ANCHOR_LINKS);
        
        anchorLinks.forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const href = anchor.getAttribute('href');
                if (href === '#' || !href) return;

                e.preventDefault();
                const target = document.querySelector(href);
                
                if (target) {
                    const offsetTop = target.offsetTop - CONSTANTS.SCROLL.NAVBAR_HEIGHT;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    /**
     * Initialize navbar scroll effects
     */
    initNavbarScroll() {
        const navbar = document.querySelector(CONSTANTS.SELECTORS.NAVBAR);
        if (!navbar) return;

        let ticking = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScroll = window.pageYOffset;
                    
                    if (currentScroll > CONSTANTS.SCROLL.SCROLL_THRESHOLD) {
                        navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
                    } else {
                        navbar.style.boxShadow = 'none';
                    }
                    
                    ticking = false;
                });
                
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    /**
     * Initialize burger menu for mobile devices
     */
    initBurgerMenu() {
        const burgerMenu = document.getElementById('burgerMenu');
        const navMenu = document.getElementById('navMenu');
        const navLinks = navMenu?.querySelectorAll('.nav-link');

        if (!burgerMenu || !navMenu) return;

        // Toggle menu on burger click
        burgerMenu.addEventListener('click', () => {
            const isExpanded = burgerMenu.getAttribute('aria-expanded') === 'true';
            burgerMenu.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (!isExpanded) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking on a link
        if (navLinks) {
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    burgerMenu.setAttribute('aria-expanded', 'false');
                    navMenu.classList.remove('active');
                    document.body.style.overflow = '';
                });
            });
        }

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu.classList.contains('active') && 
                !navMenu.contains(e.target) && 
                !burgerMenu.contains(e.target)) {
                burgerMenu.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu on window resize (if resizing to desktop)
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && navMenu.classList.contains('active')) {
                burgerMenu.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
}

