/**
 * Common components for multi-page site
 * Header, Footer, Breadcrumbs
 */

const Components = {
    /**
     * Generate navigation HTML
     * @param {string} currentPage - Current page identifier
     * @returns {string} Navigation HTML
     */
    getNavigation(currentPage = 'home') {
        const pages = {
            home: { href: 'index.html', i18n: 'nav.home' },
            discovery: { href: 'discovery.html', i18n: 'nav.dataDiscovery' },
            features: { href: 'features.html', i18n: 'nav.features' },
            useCases: { href: 'use-cases.html', i18n: 'nav.useCases' },
            download: { href: 'download.html', i18n: 'nav.download' }
        };

        const navItems = [
            { key: 'home', ...pages.home },
            { key: 'discovery', ...pages.discovery },
            { key: 'features', ...pages.features },
            { key: 'useCases', ...pages.useCases },
            { key: 'download', ...pages.download }
        ];

        let navHTML = '<div class="nav-menu" id="navMenu">';
        navItems.forEach(item => {
            const isActive = item.key === currentPage ? ' active' : '';
            navHTML += `<a href="${item.href}" class="nav-link${isActive}" data-i18n="${item.i18n}">${item.i18n}</a>`;
        });
        navHTML += `<a href="https://github.com/angryscan/angrydata-app" class="nav-link" target="_blank" data-i18n="nav.github">GitHub</a>`;
        navHTML += '</div>';

        return navHTML;
    },

    /**
     * Generate breadcrumbs HTML
     * @param {Array} items - Breadcrumb items [{text, href, i18n}]
     * @returns {string} Breadcrumbs HTML
     */
    getBreadcrumbs(items) {
        if (!items || items.length === 0) return '';

        let breadcrumbsHTML = '<nav class="breadcrumbs" aria-label="Breadcrumb">';
        breadcrumbsHTML += '<ol class="breadcrumbs-list">';

        items.forEach((item, index) => {
            const isLast = index === items.length - 1;
            const text = item.i18n ? `<span data-i18n="${item.i18n}">${item.text}</span>` : item.text;

            if (isLast) {
                breadcrumbsHTML += `<li class="breadcrumbs-item" aria-current="page">${text}</li>`;
            } else {
                breadcrumbsHTML += `<li class="breadcrumbs-item"><a href="${item.href}">${text}</a></li>`;
            }
        });

        breadcrumbsHTML += '</ol>';
        breadcrumbsHTML += '</nav>';

        return breadcrumbsHTML;
    },

    /**
     * Generate footer HTML
     * @returns {string} Footer HTML
     */
    getFooter() {
        return `
            <footer class="footer">
                <div class="container">
                    <div class="footer-content">
                        <p data-i18n="footer.copyright">&copy; 2025, by admin@angryscan.org</p>
                        <div class="footer-links">
                            <a href="https://github.com/angryscan/angrydata-app" target="_blank" data-i18n="nav.github">GitHub</a>
                            <a href="mailto:admin@angryscan.org" data-i18n="nav.contactUs">Contact us</a>
                        </div>
                        <div class="footer-pages">
                            <a href="index.html" data-i18n="nav.home">Home</a>
                            <a href="discovery.html" data-i18n="nav.dataDiscovery">Data Discovery</a>
                            <a href="features.html" data-i18n="nav.features">Features</a>
                            <a href="use-cases.html" data-i18n="nav.useCases">Use Cases</a>
                            <a href="download.html" data-i18n="nav.download">Download</a>
                        </div>
                    </div>
                </div>
            </footer>
        `;
    },

    /**
     * Generate SEO meta tags
     * @param {Object} meta - Meta data {title, description, url, image}
     * @returns {string} Meta tags HTML
     */
    getSEOMeta(meta) {
        const siteUrl = 'https://angryscan.org';
        const defaultImage = `${siteUrl}/assets/screenshot_light.png`;
        
        return `
            <!-- Primary Meta Tags -->
            <title>${meta.title}</title>
            <meta name="title" content="${meta.title}">
            <meta name="description" content="${meta.description}">
            <meta name="keywords" content="${meta.keywords || 'data scanner, PII discovery, sensitive data, PCI DSS, data protection'}">
            
            <!-- Open Graph / Facebook -->
            <meta property="og:type" content="website">
            <meta property="og:url" content="${meta.url || siteUrl}">
            <meta property="og:title" content="${meta.title}">
            <meta property="og:description" content="${meta.description}">
            <meta property="og:image" content="${meta.image || defaultImage}">
            
            <!-- Twitter -->
            <meta property="twitter:card" content="summary_large_image">
            <meta property="twitter:url" content="${meta.url || siteUrl}">
            <meta property="twitter:title" content="${meta.title}">
            <meta property="twitter:description" content="${meta.description}">
            <meta property="twitter:image" content="${meta.image || defaultImage}">
            
            <!-- Canonical URL -->
            <link rel="canonical" href="${meta.url || siteUrl}">
        `;
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Components;
}

