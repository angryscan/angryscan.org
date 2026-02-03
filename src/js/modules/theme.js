/**
 * Theme Manager Module
 * Handles light/dark theme switching and related UI updates
 */

import { CONSTANTS } from '../core/constants.js';

export class ThemeManager {
    constructor() {
        // Can be extended with dependency injection
    }
    /**
     * Initialize theme system
     */
    init() {
        const themeToggle = document.querySelector(CONSTANTS.SELECTORS.THEME_TOGGLE);
        if (!themeToggle) return;

        const html = document.documentElement;
        // Check for saved theme first, then fall back to system preference
        const savedTheme = localStorage.getItem(CONSTANTS.THEME.STORAGE_KEY);
        const initialTheme = savedTheme || this.getSystemTheme();
        
        this.setTheme(initialTheme);
        this.updateIcon(initialTheme);
        this.updateScreenshot(initialTheme);
        this.updateFavicon(initialTheme);
        
        themeToggle.addEventListener('click', () => this.toggle());
    }

    /**
     * Get system theme preference
     * @returns {string} System theme ('light' or 'dark')
     */
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return CONSTANTS.THEME.DARK;
        }
        return CONSTANTS.THEME.LIGHT;
    }

    /**
     * Set theme
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    setTheme(theme) {
        const html = document.documentElement;
        html.setAttribute('data-theme', theme);
        localStorage.setItem(CONSTANTS.THEME.STORAGE_KEY, theme);
        this.updateScreenshot(theme);
        this.updateFavicon(theme);
    }

    /**
     * Update screenshot image based on theme
     * @param {string} theme - Current theme
     */
    updateScreenshot(theme) {
        const screenshot = document.getElementById('heroScreenshot');
        if (!screenshot) return;

        const lightSrc = screenshot.getAttribute('data-light');
        const darkSrc = screenshot.getAttribute('data-dark');

        // Set correct src immediately
        if (theme === CONSTANTS.THEME.DARK && darkSrc) {
            screenshot.src = darkSrc;
        } else if (lightSrc) {
            screenshot.src = lightSrc;
        }
        
        // Show image after src is set
        screenshot.style.opacity = '1';
    }

    /**
     * Get current theme
     * @returns {string} Current theme
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || CONSTANTS.THEME.LIGHT;
    }

    /**
     * Toggle between light and dark theme
     */
    toggle() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === CONSTANTS.THEME.DARK 
            ? CONSTANTS.THEME.LIGHT 
            : CONSTANTS.THEME.DARK;
        
        this.setTheme(newTheme);
        this.updateIcon(newTheme);
    }

    /**
     * Update theme icon based on current theme
     * @param {string} theme - Current theme
     */
    updateIcon(theme) {
        const themeToggle = document.querySelector(CONSTANTS.SELECTORS.THEME_TOGGLE);
        if (!themeToggle) return;

        const themeIcon = themeToggle.querySelector('.theme-icon');
        if (!themeIcon) return;

        if (theme === CONSTANTS.THEME.DARK) {
            // Moon icon for dark theme (to switch to light)
            themeIcon.innerHTML = `
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" 
                      stroke="currentColor" 
                      stroke-width="2" 
                      stroke-linecap="round" 
                      stroke-linejoin="round"/>
            `;
        } else {
            // Sun icon for light theme (to switch to dark)
            themeIcon.innerHTML = `
                <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="2"/>
                <path d="M12 2V4M12 20V22M4.93 4.93L6.34 6.34M17.66 17.66L19.07 19.07M2 12H4M20 12H22M4.93 19.07L6.34 17.66M17.66 6.34L19.07 4.93" 
                      stroke="currentColor" 
                      stroke-width="2" 
                      stroke-linecap="round"/>
            `;
        }
    }

    /**
     * Update logo icons in navigation based on theme
     * @param {string} theme - Current theme
     */
    updateFavicon(theme) {
        // Get the base path from existing logo icon to maintain correct relative/absolute path
        const existingLogoIcon = document.querySelector('.logo-icon');
        let assetsPath = '/assets/';
        
        // If we have an existing logo icon, extract the base path from its src attribute
        if (existingLogoIcon && existingLogoIcon.getAttribute('src')) {
            const logoSrc = existingLogoIcon.getAttribute('src');
            // Extract the directory path (everything before the filename)
            const pathMatch = logoSrc.match(/^(.+\/)favicon[^\/]*\.ico$/);
            if (pathMatch) {
                assetsPath = pathMatch[1];
            }
        }
        
        // Update logo icons in navigation based on theme
        const logoFaviconFile = theme === CONSTANTS.THEME.DARK 
            ? 'favicon_dark.ico' 
            : 'favicon_light.ico';
        const logoFaviconPath = assetsPath + logoFaviconFile;
        const logoIcons = document.querySelectorAll('.logo-icon');
        logoIcons.forEach(icon => {
            icon.src = logoFaviconPath;
        });
    }
}

