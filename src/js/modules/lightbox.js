/**
 * Lightbox Manager Module
 * Handles image lightbox functionality
 */

import { CONSTANTS } from '../core/constants.js';

export class LightboxManager {
    constructor() {
        this.themeManager = null;
    }

    /**
     * Set theme manager reference
     * @param {Object} themeManager - ThemeManager instance
     */
    setThemeManager(themeManager) {
        this.themeManager = themeManager;
    }
    /**
     * Initialize lightbox functionality
     * @param {Object} themeManager - ThemeManager instance (optional)
     */
    init(themeManager = null) {
        if (themeManager) {
            this.setThemeManager(themeManager);
        }
        const screenshotContainer = document.getElementById('screenshotContainer');
        const lightbox = document.getElementById('lightbox');
        const lightboxClose = document.getElementById('lightboxClose');
        const lightboxImage = document.getElementById('lightboxScreenshot');
        const heroScreenshot = document.getElementById('heroScreenshot');

        if (!screenshotContainer || !lightbox || !lightboxClose || !lightboxImage) return;

        // Open lightbox on screenshot click
        screenshotContainer.addEventListener('click', () => {
            this.open(heroScreenshot);
        });

        // Close lightbox
        lightboxClose.addEventListener('click', (e) => {
            e.stopPropagation();
            this.close();
        });

        // Close on background click
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                this.close();
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && lightbox.classList.contains('active')) {
                this.close();
            }
        });

        // Prevent body scroll when lightbox is open
        this.observeLightbox();
    }

    /**
     * Open lightbox with image
     * @param {HTMLElement} sourceImage - Source image element
     */
    open(sourceImage) {
        const lightbox = document.getElementById('lightbox');
        const lightboxImage = document.getElementById('lightboxScreenshot');
        
        if (!lightbox || !lightboxImage) return;

        // Set image source from source image
        const lightSrc = sourceImage.getAttribute('data-light');
        const darkSrc = sourceImage.getAttribute('data-dark');
        const currentTheme = this.themeManager?.getCurrentTheme() || 'light';

        if (currentTheme === CONSTANTS.THEME.DARK && darkSrc) {
            lightboxImage.src = darkSrc;
        } else if (lightSrc) {
            lightboxImage.src = lightSrc;
        }

        // Show lightbox
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close lightbox
     */
    close() {
        const lightbox = document.getElementById('lightbox');
        if (!lightbox) return;

        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * Update lightbox image when theme changes
     * @param {string} theme - Current theme
     */
    updateLightboxImage(theme) {
        const lightbox = document.getElementById('lightbox');
        const lightboxImage = document.getElementById('lightboxScreenshot');
        
        if (!lightbox || !lightboxImage || !lightbox.classList.contains('active')) return;

        const lightSrc = lightboxImage.getAttribute('data-light');
        const darkSrc = lightboxImage.getAttribute('data-dark');

        if (theme === CONSTANTS.THEME.DARK && darkSrc) {
            lightboxImage.src = darkSrc;
        } else if (lightSrc) {
            lightboxImage.src = lightSrc;
        }
    }

    /**
     * Observe lightbox state and update image on theme change
     */
    observeLightbox() {
        if (!this.themeManager) return;
        
        // Store original updateScreenshot method
        const originalUpdateScreenshot = this.themeManager.updateScreenshot.bind(this.themeManager);
        const self = this;
        
        // Wrap updateScreenshot to also update lightbox
        this.themeManager.updateScreenshot = function(theme) {
            originalUpdateScreenshot(theme);
            self.updateLightboxImage(theme);
        };
    }
}

