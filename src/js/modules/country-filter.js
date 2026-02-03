/**
 * Country Filter Module
 * Handles filtering of data tables by country
 * 
 * Note: I18N is loaded as regular script, available via window
 */

export class CountryFilter {
    constructor() {
        this.languageManager = null;
    }
    /**
     * Initialize country filter functionality
     * @param {Object} languageManager - LanguageManager instance for translations
     */
    init(languageManager) {
        this.languageManager = languageManager;
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
    }

    /**
     * Mark table rows with country data attributes for filtering
     * Note: Rows are already marked during rendering, but this ensures compatibility
     */
    markTableRows() {
        // Rows are already marked with data-country attribute during rendering
        // This method is kept for backward compatibility
    }

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
    }

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
            
            // I18N is loaded as regular script, available via window
            const I18N = window.I18N || {};
            
            if (this.languageManager) {
                const currentLang = this.languageManager.getCurrentLanguage();
                const translations = I18N[currentLang] || I18N.en || {};
                message.textContent = translations.emptyMessage || 'No data available for selected country';
            } else {
                message.textContent = 'No data available for selected country';
            }
            
            message.setAttribute('data-i18n', 'emptyMessage');
            table.parentElement.appendChild(message);
        } else if (!show && message) {
            message.remove();
        }
    }
}

