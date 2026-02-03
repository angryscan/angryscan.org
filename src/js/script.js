/**
 * Main JavaScript file for Angry Data Scanner website
 * 
 * This file now uses ES6 modules for better organization.
 * All functionality has been split into separate modules in:
 * - js/core/ - Core functionality (constants, app initialization)
 * - js/modules/ - Feature modules (theme, scroll, language, etc.)
 * 
 * For backward compatibility, this file imports and initializes the app.
 */

/**
 * Main entry point for the application
 * 
 * This file imports and initializes the app.
 * The app initialization happens automatically in app.js
 * 
 * For backward compatibility, modules are also exported to global scope
 */

// Import and initialize the application
// Note: CONFIG and I18N are loaded as regular scripts in HTML, available via window
import { app, init } from './core/app.js';

// Export modules to global scope for backward compatibility
// (in case any inline scripts or other code references them)
import { ThemeManager } from './modules/theme.js';
import { ScrollManager } from './modules/scroll.js';
import { AnimationManager } from './modules/animation.js';
import { LightboxManager } from './modules/lightbox.js';
import { TableEnhancement } from './modules/table.js';
import { CountryFilter } from './modules/country-filter.js';
import { DataRenderer } from './modules/data-renderer.js';
import { LanguageManager } from './modules/language.js';
import { Utils } from './modules/utils.js';
import { CONSTANTS } from './core/constants.js';
import { eventBus } from './core/event-bus.js';
import { container } from './core/dependency-container.js';

// Make modules available globally for backward compatibility
if (typeof window !== 'undefined') {
    // Export classes
    window.ThemeManager = ThemeManager;
    window.ScrollManager = ScrollManager;
    window.AnimationManager = AnimationManager;
    window.LightboxManager = LightboxManager;
    window.TableEnhancement = TableEnhancement;
    window.CountryFilter = CountryFilter;
    window.DataRenderer = DataRenderer;
    window.LanguageManager = LanguageManager;
    window.Utils = Utils;
    window.CONSTANTS = CONSTANTS;
    
    // Export app instance and utilities
    window.app = app;
    window.eventBus = eventBus;
    window.container = container;
}
