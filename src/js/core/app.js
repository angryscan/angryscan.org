/**
 * Main Application Initializer
 * Coordinates initialization of all modules using Dependency Injection
 * 
 * Architecture:
 * - Event Bus: Modules communicate through events (loose coupling)
 * - Dependency Container: Manages module dependencies
 * - Module Registry: Tracks all initialized modules
 */

import { eventBus } from './event-bus.js';
import { container } from './dependency-container.js';

// CONFIG and I18N are embedded as inline scripts in HTML from config.json
// They should be loaded before this script runs
if (typeof window === 'undefined' || !window.CONFIG || !window.I18N) {
    console.error('CONFIG or I18N not found. Make sure translations and config are embedded in HTML before script.js');
}

const CONFIG = window.CONFIG;
const I18N = window.I18N;

// Import modules
import { ThemeManager } from '../modules/theme.js';
import { ScrollManager } from '../modules/scroll.js';
import { AnimationManager } from '../modules/animation.js';
import { LightboxManager } from '../modules/lightbox.js';
import { TableEnhancement } from '../modules/table.js';
import { CountryFilter } from '../modules/country-filter.js';
import { DataRenderer } from '../modules/data-renderer.js';
import { LanguageManager } from '../modules/language.js';

/**
 * Application class - manages module lifecycle
 */
class App {
    constructor() {
        this.modules = new Map();
        this.initialized = false;
    }

    /**
     * Register dependencies in the container
     */
    registerDependencies() {
        // Register CONFIG and I18N as singletons
        container.register('config', () => CONFIG, true);
        container.register('i18n', () => I18N, true);
        container.register('eventBus', () => eventBus, true);
    }

    /**
     * Initialize all modules
     */
    async init() {
        if (this.initialized) {
            console.warn('App already initialized');
            return;
        }

        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
            return;
        }

        try {
            // Register dependencies first
            this.registerDependencies();

            // Initialize language first (before rendering content)
            // Language manager needs to be initialized early
            const languageManager = new LanguageManager();
            languageManager.init();
            this.modules.set('language', languageManager);
            container.register('languageManager', () => languageManager, true);

            // Initialize data renderer (needs language manager and config)
            const dataRenderer = new DataRenderer();
            dataRenderer.init(languageManager, CONFIG);
            this.modules.set('dataRenderer', dataRenderer);
            languageManager.setDataRenderer(dataRenderer);

            // Initialize theme manager
            const themeManager = new ThemeManager();
            themeManager.init();
            this.modules.set('theme', themeManager);

            // Initialize scroll manager
            const scrollManager = new ScrollManager();
            scrollManager.init();
            this.modules.set('scroll', scrollManager);

            // Initialize animation manager
            const animationManager = new AnimationManager();
            animationManager.init();
            this.modules.set('animation', animationManager);

            // Initialize country filter (needs language manager)
            const countryFilter = new CountryFilter();
            countryFilter.init(languageManager);
            this.modules.set('countryFilter', countryFilter);

            // Initialize table enhancement
            const tableEnhancement = new TableEnhancement();
            tableEnhancement.init();
            this.modules.set('table', tableEnhancement);

            // Initialize lightbox (needs theme manager)
            const lightboxManager = new LightboxManager();
            lightboxManager.init(themeManager);
            this.modules.set('lightbox', lightboxManager);

            // Emit initialization complete event
            eventBus.emit('app:initialized', {
                modules: Array.from(this.modules.keys())
            });

            // Update translations after all content is rendered
            requestAnimationFrame(() => {
                this.finalizeInitialization(languageManager, dataRenderer);
            });

            this.initialized = true;
            console.log('Angry Data Scanner website initialized successfully');
        } catch (error) {
            console.error('Error initializing website:', error);
            eventBus.emit('app:error', { error });
        }
    }

    /**
     * Finalize initialization - render translated content
     */
    finalizeInitialization(languageManager, dataRenderer) {
        const currentLang = languageManager.getCurrentLanguage();
        
        // Only re-render for en/ru - de/fr/es pages are pre-translated
        if (currentLang === 'en' || currentLang === 'ru') {
            dataRenderer.renderUseCases();
            dataRenderer.renderDataSources();
            dataRenderer.renderCustomSignatures();
            dataRenderer.renderItAssets();
            dataRenderer.renderCrypto();
            dataRenderer.renderDownloads();
        } else if (currentLang === 'de' || currentLang === 'fr' || currentLang === 'es') {
            // Ensure page is visible for pre-translated pages
            document.documentElement.style.visibility = '';
            if (document.documentElement.hasAttribute('data-lang-loading')) {
                document.documentElement.removeAttribute('data-lang-loading');
            }
        }
    }

    /**
     * Get a module by name
     * @param {string} name - Module name
     * @returns {*} Module instance
     */
    getModule(name) {
        return this.modules.get(name);
    }

    /**
     * Destroy all modules (useful for testing)
     */
    destroy() {
        this.modules.clear();
        container.clear();
        eventBus.clear();
        this.initialized = false;
    }
}

// Create and export singleton instance
const app = new App();

// Initialize on load
app.init();

// Export for programmatic access
export { app, App };

// Export init function for backward compatibility
export function init() {
    app.init();
}
