/**
 * Language Manager Module
 * Handles internationalization, language detection, and translation management
 * 
 * Note: I18N is loaded as regular script, available via window
 */

export class LanguageManager {
    constructor() {
        this.currentLanguage = 'en';
        this.dataRenderer = null;
    }

    /**
     * Set DataRenderer reference for re-rendering on language change
     * @param {Object} dataRenderer - DataRenderer instance
     */
    setDataRenderer(dataRenderer) {
        this.dataRenderer = dataRenderer;
    }

    /**
     * Initialize language system
     */
    init() {
        // Check if we need to redirect to language-specific URL
        const path = window.location.pathname;
        const pathMatch = path.match(/^\/(ru|de|fr|es)\//);
        
        // If we're on root page (no language prefix) and have saved non-English language, redirect
        if (!pathMatch) {
            const savedLanguage = localStorage.getItem('language');
            if (savedLanguage && savedLanguage !== 'en' && 
                (savedLanguage === 'ru' || savedLanguage === 'es' || savedLanguage === 'de' || savedLanguage === 'fr')) {
                // Determine current page name
                let currentPage = path.split('/').filter(p => p).pop() || '';
                if (currentPage.endsWith('.html')) {
                    currentPage = currentPage.replace(/\.html$/, '');
                }
                if (!currentPage || currentPage === '' || currentPage === 'index') {
                    currentPage = '';
                }
                
                // Build redirect URL
                const redirectUrl = currentPage ? `/${savedLanguage}/${currentPage}` : `/${savedLanguage}/`;
                window.location.href = redirectUrl;
                return; // Exit early, page will reload
            }
        }
        
        // Detect language from URL first (has priority)
        const detectedLang = this.detectLanguage();
        
        // Use detected language (which already checks saved language for root pages)
        const languageToUse = detectedLang || 'en';
        
        // Set language (but don't redirect if we're already on the right page)
        this.currentLanguage = languageToUse;
        localStorage.setItem('language', languageToUse);
        
        // Initialize language selector (hidden select for form compatibility)
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.value = this.currentLanguage;
        }
        
        // Initialize custom dropdown
        this.initCustomLanguageDropdown();
        
        // Update all internal links to preserve language
        this.updateInternalLinks(languageToUse);
        
        // For de/fr/es: pages are pre-translated, just ensure page is visible
        if (languageToUse === 'de' || languageToUse === 'fr' || languageToUse === 'es') {
            // Don't call applyLanguage for pre-translated pages - it might try to update translations
            // Just ensure page is visible and language attributes are set
            document.documentElement.setAttribute('lang', languageToUse);
            document.documentElement.style.visibility = '';
            if (document.documentElement.hasAttribute('data-lang-loading')) {
                document.documentElement.removeAttribute('data-lang-loading');
            }
        } else {
            // For en/ru: apply translations
            this.applyLanguage(languageToUse, false);
            
            // Show page after translations are applied (if it was hidden)
            if (document.documentElement.hasAttribute('data-lang-loading')) {
                document.documentElement.style.visibility = '';
                document.documentElement.removeAttribute('data-lang-loading');
            }
        }
    }

    /**
     * Initialize custom language dropdown
     */
    initCustomLanguageDropdown() {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        const hiddenSelect = document.getElementById('languageSelector');
        
        if (!button || !dropdown || !hiddenSelect) return;
        
        // Update button text based on current language
        this.updateLanguageButton();
        
        // Toggle dropdown on button click
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = dropdown.classList.contains('active');
            this.toggleLanguageDropdown(!isOpen);
        });
        
        // Handle option clicks
        const options = dropdown.querySelectorAll('.language-option');
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const value = option.getAttribute('data-value');
                if (value) {
                    this.setLanguage(value);
                    this.toggleLanguageDropdown(false);
                }
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!button.contains(e.target) && !dropdown.contains(e.target)) {
                this.toggleLanguageDropdown(false);
            }
        });
        
        // Close dropdown on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && dropdown.classList.contains('active')) {
                this.toggleLanguageDropdown(false);
                button.focus();
            }
        });
    }

    /**
     * Toggle language dropdown
     */
    toggleLanguageDropdown(open) {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        
        if (!button || !dropdown) return;
        
        if (open) {
            dropdown.classList.add('active');
            button.setAttribute('aria-expanded', 'true');
        } else {
            dropdown.classList.remove('active');
            button.setAttribute('aria-expanded', 'false');
        }
    }

    /**
     * Update language button text
     */
    updateLanguageButton() {
        const buttonText = document.getElementById('languageSelectorText');
        const hiddenSelect = document.getElementById('languageSelector');
        const options = document.querySelectorAll('.language-option');
        
        if (!buttonText || !hiddenSelect) return;
        
        const currentValue = hiddenSelect.value;
        const currentOption = hiddenSelect.querySelector(`option[value="${currentValue}"]`);
        
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
        
        // Language to flag mapping
        const flagMap = {
            'en': { file: 'flag-us.svg', alt: 'US', name: 'English' },
            'ru': { file: 'flag-ru.svg', alt: 'RU', name: 'Русский' },
            'es': { file: 'flag-es.svg', alt: 'ES', name: 'Español' },
            'de': { file: 'flag-de.svg', alt: 'DE', name: 'Deutsch' },
            'fr': { file: 'flag-fr.svg', alt: 'FR', name: 'Français' }
        };
        
        if (currentOption && flagMap[currentValue]) {
            const flagInfo = flagMap[currentValue];
            buttonText.innerHTML = `<img src="${assetsPath}${flagInfo.file}" alt="${flagInfo.alt}" class="language-flag-icon"> ${flagInfo.name}`;
        }
        
        // Update selected state in dropdown (don't update flag paths - they're already correct in HTML)
        options.forEach(option => {
            if (option.getAttribute('data-value') === currentValue) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }

    /**
     * Detect language from URL, localStorage, or URL parameter
     */
    detectLanguage() {
        // Check URL path for language prefix (/ru/, /de/, /fr/, /es/)
        const path = window.location.pathname;
        const pathMatch = path.match(/^\/(ru|de|fr|es)\//);
        if (pathMatch && pathMatch[1]) {
            return pathMatch[1];
        }

        // If we're on root pages (/, /index.html, etc.), check saved language first
        // This ensures that when switching from /ru/ to English, we use English
        const savedLanguage = localStorage.getItem('language');
        if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'ru' || savedLanguage === 'es' || savedLanguage === 'de' || savedLanguage === 'fr')) {
            // If we're on root page (no language prefix in URL), return saved language
            if (!pathMatch) {
                return savedLanguage;
            }
        }

        // Check URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const langParam = urlParams.get('lang');
        if (langParam && (langParam === 'en' || langParam === 'ru' || langParam === 'es' || langParam === 'de' || langParam === 'fr')) {
            return langParam;
        }
        
        return 'en'; // Default to English
    }

    /**
     * Update all internal links to include language prefix
     * @param {string} lang - Language code
     */
    updateInternalLinks(lang) {
        // List of internal HTML pages
        const internalPages = ['index.html', 'discovery.html', 'features.html', 'use-cases.html', 'download.html'];
        
        // Get all links on the page
        const links = document.querySelectorAll('a[href]');
        
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            
            // Skip external links, anchors, and mailto links
            if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('#')) {
                return;
            }
            
            // Check if it's an internal page (exact match or ends with page name)
            const isInternalPage = internalPages.some(page => {
                return href === page || 
                       href === '/' + page || 
                       href.endsWith('/' + page) ||
                       href === '/' + lang + '/' + page;
            });
            
            if (isInternalPage) {
                // Extract page name (remove any existing language prefix and leading slashes)
                let pageName = href;
                
                // Remove language prefix if present
                pageName = pageName.replace(/^\/(ru|de|fr|es)\//, '');
                
                // Remove leading slash
                pageName = pageName.replace(/^\//, '');
                
                // Ensure we have a valid page name
                if (!pageName || !internalPages.includes(pageName)) {
                    // Try to extract from full path
                    const match = href.match(/\/([^\/]+\.html)$/);
                    if (match && internalPages.includes(match[1])) {
                        pageName = match[1];
                    } else {
                        return; // Skip if we can't determine the page
                    }
                }
                
                // Update href based on language
                if (lang === 'ru' || lang === 'de' || lang === 'fr' || lang === 'es') {
                    // Add language prefix
                    link.setAttribute('href', `/${lang}/${pageName}`);
                } else {
                    // For English, use root path
                    link.setAttribute('href', pageName);
                }
            }
        });
    }

    /**
     * Apply language without redirecting
     * @param {string} lang - Language code
     * @param {boolean} updateStorage - Whether to update localStorage
     */
    applyLanguage(lang, updateStorage = true) {
        this.currentLanguage = lang;
        if (updateStorage) {
            localStorage.setItem('language', lang);
        }
        
        // Update language selector (hidden select)
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.value = lang;
        }
        
        // Update custom dropdown button
        this.updateLanguageButton();
        
        // Update all internal links to preserve language
        this.updateInternalLinks(lang);
        
        // Update HTML lang attribute
        if (lang === 'ru') {
            document.documentElement.setAttribute('lang', 'ru');
        } else if (lang === 'de') {
            document.documentElement.setAttribute('lang', 'de');
        } else if (lang === 'fr') {
            document.documentElement.setAttribute('lang', 'fr');
        } else if (lang === 'es') {
            document.documentElement.setAttribute('lang', 'es');
        } else {
            document.documentElement.setAttribute('lang', 'en');
        }
        
        // Handle different languages
        if (lang === 'en' || lang === 'ru') {
            // Use custom translations
            // Apply translations immediately without delay to avoid showing English first
            this.updateTranslations(lang);
            // Note: Page title is already set correctly in HTML template, so we don't override it here
            // Re-render use cases, data sources, custom signatures, IT assets, crypto and downloads with new translations
            if (this.dataRenderer) {
                this.dataRenderer.renderUseCases();
                this.dataRenderer.renderDataSources();
                this.dataRenderer.renderCustomSignatures();
                this.dataRenderer.renderItAssets();
                this.dataRenderer.renderCrypto();
                this.dataRenderer.renderDownloads();
            }
            // Show page after translations are applied (if it was hidden)
            if (document.documentElement.hasAttribute('data-lang-loading')) {
                document.documentElement.style.visibility = '';
                document.documentElement.removeAttribute('data-lang-loading');
            }
        } else {
            // For es, de, fr: pages are pre-translated via Python API
            // No need to update translations - pages are already translated
            // Don't update title - it's already translated in HTML
            // Show page immediately (it was never hidden for pre-translated pages)
            // But ensure it's visible in case something went wrong
            document.documentElement.style.visibility = '';
            if (document.documentElement.hasAttribute('data-lang-loading')) {
                document.documentElement.removeAttribute('data-lang-loading');
            }
        }
    }

    /**
     * Set language (with redirect if needed)
     * @param {string} lang - Language code
     */
    setLanguage(lang) {
        // Check if we need to redirect to language-specific URL
        const currentPath = window.location.pathname;
        const currentLangMatch = currentPath.match(/^\/(ru|de|fr|es)\//);
        
        // Determine current page name (remove .html extension for clean URLs)
        let currentPage = currentPath.split('/').filter(p => p).pop() || '';
        
        // If we're on a language page, extract the page name
        if (currentLangMatch) {
            const parts = currentPath.split('/').filter(p => p);
            if (parts.length > 1) {
                currentPage = parts[parts.length - 1];
            } else {
                currentPage = '';
            }
        }
        
        // Remove .html extension if present
        if (currentPage.endsWith('.html')) {
            currentPage = currentPage.replace(/\.html$/, '');
        }
        
        // Handle root/index page - use clean URL (empty string or '/')
        if (!currentPage || currentPage === '' || currentPage === 'index') {
            currentPage = '';
        }
        
        // If switching to a language that has a dedicated page (ru, de, fr, es)
        if (lang === 'ru' || lang === 'de' || lang === 'fr' || lang === 'es') {
            // If we're not already on that language's page, redirect
            if (!currentLangMatch || currentLangMatch[1] !== lang) {
                // Save language to localStorage before redirect
                localStorage.setItem('language', lang);
                // Build clean URL (without .html)
                const newUrl = currentPage ? `/${lang}/${currentPage}` : `/${lang}/`;
                window.location.href = newUrl;
                return; // Exit early, page will reload
            }
        } else if (lang === 'en') {
            // If switching to English and we're on a language page, redirect to root
            if (currentLangMatch) {
                // Save language to localStorage before redirect
                localStorage.setItem('language', lang);
                // Build clean URL (without .html)
                const rootPage = currentPage ? `/${currentPage}` : '/';
                window.location.href = rootPage;
                return; // Exit early, page will reload
            }
        }
        
        // If we're already on the correct page, apply language without redirect
        this.applyLanguage(lang, true);
    }

    /**
     * Update translations for custom languages (en, ru)
     * @param {string} lang - Language code
     */
    updateTranslations(lang) {
        // Only update translations for en and ru
        // de, fr, es pages are pre-translated via Python API
        if (lang !== 'en' && lang !== 'ru') {
            return;
        }
        
        // I18N is loaded as regular script, available via window
        const I18N = window.I18N || {};
        
        if (!I18N[lang]) {
            console.warn(`Translations for language ${lang} not found`);
            return;
        }

        const translations = I18N[lang];
        const elements = document.querySelectorAll('[data-i18n]');

        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (!key) return;
            
            // Skip if element has child elements with data-i18n (they will be processed separately)
            if (element.querySelector('[data-i18n]')) {
                return;
            }
            
            const value = this.getNestedValue(translations, key);
            
            if (value !== undefined && value !== null) {
                try {
                    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                        element.value = value;
                    } else if (element.hasAttribute('placeholder')) {
                        element.setAttribute('placeholder', value);
                    } else {
                        // Simple text replacement - innerHTML will be handled by child elements
                        element.textContent = value;
                    }
                } catch (error) {
                    console.warn(`Error updating translation for key "${key}":`, error);
                }
            }
        });
    }

    /**
     * Convert snake_case to camelCase
     * @param {string} str - String to convert
     * @returns {string} Converted string
     */
    _snakeToCamel(str) {
        return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
    }

    /**
     * Convert camelCase to snake_case
     * @param {string} str - String to convert
     * @returns {string} Converted string
     */
    _camelToSnake(str) {
        return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
    }

    /**
     * Get nested value from object using dot notation
     * Supports both snake_case and camelCase keys for compatibility
     * @param {Object} obj - Object to search
     * @param {string} path - Dot notation path (can be snake_case or camelCase)
     * @returns {*} Value or undefined
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            if (!current) return undefined;
            
            // First try exact key match
            if (current[key] !== undefined) {
                return current[key];
            }
            
            // Try converting snake_case to camelCase
            const camelKey = this._snakeToCamel(key);
            if (current[camelKey] !== undefined) {
                return current[camelKey];
            }
            
            // Try converting camelCase to snake_case
            const snakeKey = this._camelToSnake(key);
            if (current[snakeKey] !== undefined) {
                return current[snakeKey];
            }
            
            return undefined;
        }, obj);
    }

    /**
     * Get current language
     * @returns {string} Current language code
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

