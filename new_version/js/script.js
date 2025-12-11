/**
 * Main JavaScript file for Angry Data Scanner website
 * Organized into modules for better maintainability
 */

// ============================================================================
// Constants
// ============================================================================

const CONSTANTS = {
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

// ============================================================================
// Theme Manager Module
// ============================================================================

const ThemeManager = {
    /**
     * Initialize theme system
     */
    init() {
        const themeToggle = document.querySelector(CONSTANTS.SELECTORS.THEME_TOGGLE);
        if (!themeToggle) return;

        const html = document.documentElement;
        const savedTheme = localStorage.getItem(CONSTANTS.THEME.STORAGE_KEY) || CONSTANTS.THEME.LIGHT;
        
        this.setTheme(savedTheme);
        this.updateIcon(savedTheme);
        this.updateScreenshot(savedTheme);
        
        themeToggle.addEventListener('click', () => this.toggle());
    },

    /**
     * Set theme
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    setTheme(theme) {
        const html = document.documentElement;
        html.setAttribute('data-theme', theme);
        localStorage.setItem(CONSTANTS.THEME.STORAGE_KEY, theme);
        this.updateScreenshot(theme);
    },

    /**
     * Update screenshot image based on theme
     * @param {string} theme - Current theme
     */
    updateScreenshot(theme) {
        const screenshot = document.getElementById('heroScreenshot');
        if (!screenshot) return;

        const lightSrc = screenshot.getAttribute('data-light');
        const darkSrc = screenshot.getAttribute('data-dark');

        // Fade out, change image, fade in
        screenshot.style.opacity = '0';
        
        setTimeout(() => {
            if (theme === CONSTANTS.THEME.DARK && darkSrc) {
                screenshot.src = darkSrc;
            } else if (lightSrc) {
                screenshot.src = lightSrc;
            }
            
            setTimeout(() => {
                screenshot.style.opacity = '1';
            }, 50);
        }, 150);
    },

    /**
     * Get current theme
     * @returns {string} Current theme
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || CONSTANTS.THEME.LIGHT;
    },

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
    },

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
};

// ============================================================================
// Scroll Manager Module
// ============================================================================

const ScrollManager = {
    /**
     * Initialize scroll-related functionality
     */
    init() {
        this.initSmoothScroll();
        this.initNavbarScroll();
    },

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
    },

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
};

// ============================================================================
// Animation Manager Module
// ============================================================================

const AnimationManager = {
    /**
     * Initialize intersection observer for animations
     */
    init() {
        if (!('IntersectionObserver' in window)) {
            // Fallback for browsers without IntersectionObserver
            this.fallbackAnimation();
            return;
        }

        const observerOptions = {
            threshold: CONSTANTS.ANIMATION.INTERSECTION_THRESHOLD,
            rootMargin: CONSTANTS.ANIMATION.ROOT_MARGIN
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateIn(entry.target);
                }
            });
        }, observerOptions);

        // Observe all animatable elements
        const elements = document.querySelectorAll(CONSTANTS.SELECTORS.ANIMATABLE_ELEMENTS);
        elements.forEach(el => {
            this.prepareElement(el);
            observer.observe(el);
        });
    },

    /**
     * Prepare element for animation
     * @param {HTMLElement} element - Element to prepare
     */
    prepareElement(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `opacity ${CONSTANTS.ANIMATION.DURATION}ms ease, transform ${CONSTANTS.ANIMATION.DURATION}ms ease`;
    },

    /**
     * Animate element in
     * @param {HTMLElement} element - Element to animate
     */
    animateIn(element) {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    },

    /**
     * Fallback animation for browsers without IntersectionObserver
     */
    fallbackAnimation() {
        const elements = document.querySelectorAll(CONSTANTS.SELECTORS.ANIMATABLE_ELEMENTS);
        elements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
    }
};

// ============================================================================
// Lightbox Module
// ============================================================================

const LightboxManager = {
    /**
     * Initialize lightbox functionality
     */
    init() {
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
    },

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
        const currentTheme = ThemeManager.getCurrentTheme();

        if (currentTheme === CONSTANTS.THEME.DARK && darkSrc) {
            lightboxImage.src = darkSrc;
        } else if (lightSrc) {
            lightboxImage.src = lightSrc;
        }

        // Show lightbox
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    /**
     * Close lightbox
     */
    close() {
        const lightbox = document.getElementById('lightbox');
        if (!lightbox) return;

        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    },

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
    },

    /**
     * Observe lightbox state and update image on theme change
     */
    observeLightbox() {
        // Store original updateScreenshot method
        const originalUpdateScreenshot = ThemeManager.updateScreenshot.bind(ThemeManager);
        
        // Wrap updateScreenshot to also update lightbox
        ThemeManager.updateScreenshot = function(theme) {
            originalUpdateScreenshot(theme);
            LightboxManager.updateLightboxImage(theme);
        };
    }
};

// ============================================================================
// Table Enhancement Module
// ============================================================================

const TableEnhancement = {
    /**
     * Initialize table enhancements
     */
    init() {
        const tableRows = document.querySelectorAll(CONSTANTS.SELECTORS.TABLE_ROWS);
        
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.transition = 'background-color 0.2s ease';
            });
        });
    }
};

// ============================================================================
// Country Filter Module
// ============================================================================

const CountryFilter = {
    /**
     * Initialize country filter functionality
     */
    init() {
        const countryButtons = document.querySelectorAll('.country-button');
        if (countryButtons.length === 0) return;

        // Wait for tables to be rendered first
        setTimeout(() => {
            // Mark all table rows with data attributes for filtering
            this.markTableRows();

            // Add event listeners to buttons
            countryButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const selectedCountry = button.getAttribute('data-country');
                    
                    // Update active state
                    countryButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    
                    // Filter tables
                    this.filterTables(selectedCountry);
                });
            });
        }, 100);
    },

    /**
     * Mark table rows with country data attributes for filtering
     * Note: Rows are already marked during rendering, but this ensures compatibility
     */
    markTableRows() {
        // Rows are already marked with data-country attribute during rendering
        // This method is kept for backward compatibility
    },

    /**
     * Filter tables based on selected country
     * @param {string} selectedCountry - Selected country code or 'all' or 'international'
     */
    filterTables(selectedCountry) {
        // Get all filterable tables
        const tables = [
            '[data-table="personal-data-numbers"]',
            '[data-table="personal-data-text"]',
            '[data-table="banking-secrecy"]'
        ];

        tables.forEach(tableSelector => {
            const table = document.querySelector(tableSelector);
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            let visibleCount = 0;
            
            rows.forEach((row, index) => {
                const rowCountry = row.getAttribute('data-country');
                let shouldShow = false;
                
                if (selectedCountry === 'all') {
                    // Show all rows
                    shouldShow = true;
                } else if (selectedCountry === 'international') {
                    // Show only international rows
                    shouldShow = rowCountry === 'international';
                } else {
                    // Show rows for selected country AND international rows
                    shouldShow = rowCountry === selectedCountry || rowCountry === 'international';
                }
                
                // Add smooth transition
                if (shouldShow) {
                    row.style.opacity = '0';
                    row.style.transform = 'translateY(-10px)';
                    row.style.display = '';
                    visibleCount++;
                    
                    // Animate in
                    setTimeout(() => {
                        row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                        row.style.opacity = '1';
                        row.style.transform = 'translateY(0)';
                    }, index * 20);
                } else {
                    // Animate out
                    row.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                    row.style.opacity = '0';
                    row.style.transform = 'translateY(-10px)';
                    
                    setTimeout(() => {
                        row.style.display = 'none';
                    }, 200);
                }
            });
            
            // Show message if no rows visible
            this.showEmptyMessage(table, visibleCount === 0);
        });
    },

    /**
     * Show or hide empty message for table
     * @param {HTMLElement} table - Table element
     * @param {boolean} show - Whether to show message
     */
    showEmptyMessage(table, show) {
        let message = table.parentElement.querySelector('.table-empty-message');
        
        if (show && !message) {
            message = document.createElement('div');
            message.className = 'table-empty-message';
            message.textContent = 'No data available for selected country';
            table.parentElement.appendChild(message);
        } else if (!show && message) {
            message.remove();
        }
    }
};

// ============================================================================
// Data Renderer Module
// ============================================================================

const DataRenderer = {
    /**
     * Initialize data rendering from config
     */
    init() {
        if (typeof CONFIG === 'undefined') {
            console.warn('CONFIG is not defined. Data will not be rendered.');
            return;
        }

        this.renderPersonalDataNumbers();
        this.renderPersonalDataText();
        this.renderPciDss();
        this.renderBankingSecrecy();
        this.renderItAssets();
        this.renderCustomSignatures();
        this.renderFileTypes();
        this.renderDataSources();
        this.renderUseCases();
        this.renderDownloads();
    },

    /**
     * Render table row
     * @param {HTMLElement} tbody - Table body element
     * @param {Array} cells - Array of cell content (strings or HTML strings)
     * @param {string} country - Optional country code for filtering
     */
    renderTableRow(tbody, cells, country = null) {
        const row = document.createElement('tr');
        if (country !== null) {
            // Normalize country: '-' becomes 'international'
            const normalizedCountry = country === '-' ? 'international' : country;
            row.setAttribute('data-country', normalizedCountry);
        }
        cells.forEach(cellContent => {
            const cell = document.createElement('td');
            if (typeof cellContent === 'string') {
                // Check if it's HTML (contains tags)
                if (cellContent.includes('<')) {
                    cell.innerHTML = cellContent;
                } else {
                    cell.textContent = cellContent;
                }
            } else {
                cell.appendChild(cellContent);
            }
            row.appendChild(cell);
        });
        tbody.appendChild(row);
    },

    /**
     * Render Personal Data (numbers) table
     */
    renderPersonalDataNumbers() {
        const tbody = document.querySelector('[data-table="personal-data-numbers"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.personalDataNumbers.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                item.localName,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    },

    /**
     * Render Personal Data (text) table
     */
    renderPersonalDataText() {
        const tbody = document.querySelector('[data-table="personal-data-text"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.personalDataText.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                item.localName,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    },

    /**
     * Render PCI DSS table
     */
    renderPciDss() {
        const tbody = document.querySelector('[data-table="pci-dss"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.pciDss.forEach(item => {
            this.renderTableRow(tbody, [
                item.type,
                `<code>${item.example}</code>`
            ]);
        });
    },

    /**
     * Render Banking Secrecy table
     */
    renderBankingSecrecy() {
        const tbody = document.querySelector('[data-table="banking-secrecy"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.bankingSecrecy.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    },

    /**
     * Render IT Assets table
     */
    renderItAssets() {
        const tbody = document.querySelector('[data-table="it-assets"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.itAssets.forEach(item => {
            // Check if example should be wrapped in code tags
            const shouldWrapInCode = !item.example.startsWith('Finds') && 
                                     !item.example.includes('SHA-256');
            const exampleCell = shouldWrapInCode 
                ? `<code>${item.example}</code>`
                : item.example;
            
            this.renderTableRow(tbody, [
                item.type,
                exampleCell
            ]);
        });
    },

    /**
     * Render Custom Signatures section
     */
    renderCustomSignatures() {
        const container = document.querySelector('[data-section="custom-signatures"]');
        if (!container) return;

        const examples = CONFIG.customSignatures.examples
            .map(ex => `<code>${ex}</code>`)
            .join(', ');
        
        const description = container.querySelector('.category-description');
        if (description) {
            description.innerHTML = `${CONFIG.customSignatures.description} ${examples} or any other.`;
        }
    },

    /**
     * Render File Types table
     */
    renderFileTypes() {
        const tbody = document.querySelector('[data-table="file-types"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.fileTypes.forEach(item => {
            this.renderTableRow(tbody, [
                item.category,
                `<code>${item.formats}</code>`
            ]);
        });
    },

    /**
     * Render Data Sources table
     */
    renderDataSources() {
        const tbody = document.querySelector('[data-table="data-sources"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        CONFIG.dataSources.forEach(item => {
            this.renderTableRow(tbody, [
                item.connector,
                item.description
            ]);
        });
    },

    /**
     * Render Use Cases
     */
    renderUseCases() {
        const container = document.querySelector('[data-section="use-cases"]');
        if (!container) return;

        const useCasesContainer = container.querySelector('.use-cases');
        if (!useCasesContainer) return;

        useCasesContainer.innerHTML = '';
        CONFIG.useCases.forEach(useCase => {
            const item = document.createElement('div');
            item.className = 'use-case-item';
            item.innerHTML = `
                <svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <p>${useCase}</p>
            `;
            useCasesContainer.appendChild(item);
        });
    },

    /**
     * Render Download links
     */
    renderDownloads() {
        const platforms = {
            windows: document.querySelector('[data-platform="windows"]'),
            linux: document.querySelector('[data-platform="linux"]'),
            macos: document.querySelector('[data-platform="macos"]')
        };

        Object.keys(platforms).forEach(platform => {
            const container = platforms[platform];
            if (!container) return;

            const linksContainer = container.querySelector('.download-links');
            if (!linksContainer) return;

            linksContainer.innerHTML = '';
            CONFIG.downloads[platform].forEach(link => {
                const linkEl = document.createElement('a');
                linkEl.href = link.href;
                linkEl.className = 'download-link';
                linkEl.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M12 3V15M12 15L8 11M12 15L16 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    ${link.text}
                `;
                linksContainer.appendChild(linkEl);
            });
        });

        // Update system requirements
        const sysReq = document.querySelector('[data-info="system-requirements"]');
        if (sysReq) {
            sysReq.textContent = `System Requirements: ${CONFIG.systemRequirements}`;
        }
    }
};

// ============================================================================
// Utility Functions
// ============================================================================

const Utils = {
    /**
     * Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Check if element is in viewport
     * @param {HTMLElement} element - Element to check
     * @returns {boolean} True if element is in viewport
     */
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// ============================================================================
// Main Initialization
// ============================================================================

/**
 * Initialize all modules when DOM is ready
 */
function init() {
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
        return;
    }

    try {
        // Initialize all modules
        DataRenderer.init(); // Must be first to populate data
        ThemeManager.init();
        ScrollManager.init();
        AnimationManager.init();
        CountryFilter.init(); // Initialize country filter (will re-render tables)
        TableEnhancement.init();
        LightboxManager.init();

        console.log('Angry Data Scanner website initialized successfully');
    } catch (error) {
        console.error('Error initializing website:', error);
    }
}

// Start initialization
init();
