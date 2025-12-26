/**
 * Data Renderer Module
 * Renders data tables and content from CONFIG
 * 
 * Note: CONFIG and I18N are loaded as regular scripts, available via window
 */

export class DataRenderer {
    /**
     * Initialize data rendering from config
     * @param {Object} languageManager - LanguageManager instance for translations
     * @param {Object} config - Configuration object (optional, uses imported CONFIG by default)
     */
    constructor() {
        this.languageManager = null;
        // CONFIG is loaded as regular script, available via window
        this.config = window.CONFIG;
    }

    /**
     * Initialize the renderer
     * @param {Object} languageManager - LanguageManager instance for translations
     * @param {Object} config - Optional config override
     */
    init(languageManager, config = null) {
        this.languageManager = languageManager;
        if (config) {
            this.config = config;
        }
        
        if (!this.config) {
            console.warn('CONFIG is not defined. Data will not be rendered.');
            return;
        }

        this.renderPersonalDataNumbers();
        this.renderPersonalDataText();
        this.renderPciDss();
        this.renderBankingSecrecy();
        this.renderCrypto();
        this.renderItAssets();
        this.renderCustomSignatures();
        this.renderFileTypes();
        this.renderDataSources();
        this.renderUseCases();
        this.renderDownloads();
    }

    /**
     * Get translation for a key
     * @param {string} key - Translation key
     * @returns {string} Translated text
     */
    getTranslation(key) {
        if (!this.languageManager) {
            return key;
        }
        
        // I18N is loaded as regular script, available via window
        const I18N = window.I18N || {};
        const lang = this.languageManager.getCurrentLanguage();
        const translations = I18N[lang] || I18N.en || {};
        
        const keys = key.split('.');
        let value = translations;
        for (const k of keys) {
            value = value && value[k];
        }
        return value !== undefined ? value : key;
    }

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
    }

    /**
     * Get current translations object
     * @returns {Object} Translations object
     */
    getTranslations() {
        // I18N is loaded as regular script, available via window
        const I18N = window.I18N || {};
        
        if (!this.languageManager) {
            return I18N.en || {};
        }
        
        const currentLang = this.languageManager.getCurrentLanguage();
        return I18N[currentLang] || I18N.en || {};
    }

    /**
     * Render Personal Data (numbers) table
     */
    renderPersonalDataNumbers() {
        const tbody = document.querySelector('[data-table="personal-data-numbers"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.config.personalDataNumbers.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                item.localName,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    }

    /**
     * Render Personal Data (text) table
     */
    renderPersonalDataText() {
        const tbody = document.querySelector('[data-table="personal-data-text"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.config.personalDataText.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                item.localName,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    }

    /**
     * Render PCI DSS table
     */
    renderPciDss() {
        const tbody = document.querySelector('[data-table="pci-dss"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.config.pciDss.forEach(item => {
            this.renderTableRow(tbody, [
                item.type,
                `<code>${item.example}</code>`
            ]);
        });
    }

    /**
     * Render Banking Secrecy table
     */
    renderBankingSecrecy() {
        const tbody = document.querySelector('[data-table="banking-secrecy"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.config.bankingSecrecy.forEach(item => {
            const countryDisplay = item.country === '-' ? '-' : item.country;
            this.renderTableRow(tbody, [
                item.type,
                countryDisplay,
                `<code>${item.example}</code>`
            ], item.country);
        });
    }

    /**
     * Render Crypto table
     */
    renderCrypto() {
        const tbody = document.querySelector('[data-table="crypto"] tbody');
        if (!tbody) return;

        const translations = this.getTranslations();
        
        // Use translated crypto data if available, otherwise fall back to CONFIG
        const crypto = translations.crypto && Array.isArray(translations.crypto)
            ? translations.crypto
            : this.config.crypto;

        tbody.innerHTML = '';
        crypto.forEach(item => {
            this.renderTableRow(tbody, [
                item.type,
                `<code>${item.example}</code>`
            ]);
        });
    }

    /**
     * Render IT Assets table
     */
    renderItAssets() {
        const tbody = document.querySelector('[data-table="it-assets"] tbody');
        if (!tbody) return;

        const translations = this.getTranslations();
        
        // Use translated IT assets if available, otherwise fall back to CONFIG
        const itAssets = translations.itAssets && Array.isArray(translations.itAssets)
            ? translations.itAssets
            : this.config.itAssets;

        tbody.innerHTML = '';
        itAssets.forEach(item => {
            // Check if example should be wrapped in code tags
            const shouldWrapInCode = !item.example.startsWith('Finds') && 
                                     !item.example.startsWith('Находит') &&
                                     !item.example.includes('SHA-256');
            const exampleCell = shouldWrapInCode 
                ? `<code>${item.example}</code>`
                : item.example;
            
            this.renderTableRow(tbody, [
                item.type,
                exampleCell
            ]);
        });
    }

    /**
     * Render Custom Signatures section
     */
    renderCustomSignatures() {
        const container = document.querySelector('[data-section="custom-signatures"]');
        if (!container) return;

        const translations = this.getTranslations();
        
        // Use translated examples if available, otherwise fall back to CONFIG
        const examples = translations.categories && translations.categories.customSignaturesExamples
            ? translations.categories.customSignaturesExamples
            : this.config.customSignatures.examples;
        
        const examplesHTML = examples
            .map(ex => `<code>${ex}</code>`)
            .join(', ');
        
        const description = container.querySelector('.category-description');
        if (description) {
            const descText = translations.categories && translations.categories.customSignaturesDesc
                ? translations.categories.customSignaturesDesc
                : this.config.customSignatures.description;
            const orText = translations.categories && translations.categories.customSignaturesOr
                ? translations.categories.customSignaturesOr
                : 'or any other.';
            description.innerHTML = `${descText} ${examplesHTML} ${orText}`;
        }
    }

    /**
     * Render File Types table
     */
    renderFileTypes() {
        const tbody = document.querySelector('[data-table="file-types"] tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        this.config.fileTypes.forEach(item => {
            this.renderTableRow(tbody, [
                item.category,
                `<code>${item.formats}</code>`
            ]);
        });
    }

    /**
     * Render Data Sources table
     */
    renderDataSources() {
        const tbody = document.querySelector('[data-table="data-sources"] tbody');
        if (!tbody) return;

        const translations = this.getTranslations();
        
        // Use translated data sources if available, otherwise fall back to CONFIG
        const dataSources = translations.sections && translations.sections.dataSources && translations.sections.dataSources.sources
            ? translations.sections.dataSources.sources
            : this.config.dataSources;

        tbody.innerHTML = '';
        dataSources.forEach(item => {
            this.renderTableRow(tbody, [
                item.connector,
                item.description
            ]);
        });
    }

    /**
     * Render Use Cases
     */
    renderUseCases() {
        const container = document.querySelector('[data-section="use-cases"]');
        if (!container) return;

        const useCasesContainer = container.querySelector('.use-cases');
        if (!useCasesContainer) return;

        const translations = this.getTranslations();
        
        // Use translated use cases if available, otherwise fall back to CONFIG
        const useCases = translations.sections && translations.sections.useCases && translations.sections.useCases.cases
            ? translations.sections.useCases.cases
            : this.config.useCases;

        // Icons for each use case - standard icons
        const useCaseIcons = [
            // Leak hunting - folder with search
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 7V19C3 19.5304 3.21071 20.0391 3.58579 20.4142C3.96086 20.7893 4.46957 21 5 21H19C19.5304 21 20.0391 20.7893 20.4142 20.4142C20.7893 20.0391 21 19.5304 21 19V9C21 8.46957 20.7893 7.96086 20.4142 7.58579C20.0391 7.21071 19.5304 7 19 7H12L10 5H5C4.46957 5 3.96086 5.21071 3.58579 5.58579C3.21071 5.96086 3 6.46957 3 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="15" cy="13" r="3" stroke="currentColor" stroke-width="2"/>
                <path d="M17 15L19 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>`,
            // PCI DSS - credit card
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="6" width="20" height="12" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 10H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>`,
            // Banking - shield
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L4 5V11C4 16.55 7.16 21.74 12 23C16.84 21.74 20 16.55 20 11V5L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>`,
            // Sales team - folder
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 7V19C3 19.5304 3.21071 20.0391 3.58579 20.4142C3.96086 20.7893 4.46957 21 5 21H19C19.5304 21 20.0391 20.7893 20.4142 20.4142C20.7893 20.0391 21 19.5304 21 19V9C21 8.46957 20.7893 7.96086 20.4142 7.58579C20.0391 7.21071 19.5304 7 19 7H12L10 5H5C4.46957 5 3.96086 5.21071 3.58579 5.58579C3.21071 5.96086 3 6.46957 3 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>`,
            // Cryptocurrency - laptop
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="4" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 18H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M6 22H18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>`,
            // Database - database
            `<svg class="use-case-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="12" cy="5" rx="9" ry="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M3 5V19C3 19.5304 6.13401 22 12 22C17.866 22 21 19.5304 21 19V5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M3 12C3 12.5304 6.13401 15 12 15C17.866 15 21 12.5304 21 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>`
        ];

        useCasesContainer.innerHTML = '';
        useCases.forEach((useCase, index) => {
            const item = document.createElement('div');
            item.className = 'use-case-item';
            item.innerHTML = `
                ${useCaseIcons[index] || useCaseIcons[0]}
                <p>${useCase}</p>
            `;
            useCasesContainer.appendChild(item);
        });
    }

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
            this.config.downloads[platform].forEach(link => {
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
            const systemRequirementsText = this.getTranslation('sections.download.systemRequirements');
            sysReq.textContent = systemRequirementsText || `System Requirements: ${this.config.systemRequirements}`;
        }
    }
}

