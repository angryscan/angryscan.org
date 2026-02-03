/**
 * Application constants
 * Centralized configuration values used across modules
 */

export const CONSTANTS = {
    THEME: {
        LIGHT: 'light',
        DARK: 'dark',
        STORAGE_KEY: 'theme'
    },
    SCROLL: {
        NAVBAR_HEIGHT: 64,
        SCROLL_THRESHOLD: 100
    },
    ANIMATION: {
        INTERSECTION_THRESHOLD: 0.1,
        ROOT_MARGIN: '0px 0px -50px 0px',
        DURATION: 600
    },
    BREAKPOINTS: {
        MOBILE: 768,
        TABLET: 968
    },
    SELECTORS: {
        THEME_TOGGLE: '#themeToggle',
        ANCHOR_LINKS: 'a[href^="#"]',
        NAVBAR: '.navbar',
        ANIMATABLE_ELEMENTS: '.section, .feature-card, .download-card, .use-case-item',
        TABLE_ROWS: '.data-table tbody tr'
    }
};

