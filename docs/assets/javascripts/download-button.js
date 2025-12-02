/**
 * Download Button Functionality
 * Creates download button after screenshots gallery and scrolls to Download section on click
 * Supports multiple languages: Download, Скачать, Descargar, Herunterladen, etc.
 */

(function() {
    'use strict';

    /**
     * Create and insert download button after screenshots gallery
     */
    function createDownloadButton() {
        // Check if button already exists
        if (document.getElementById('download-button')) {
            return;
        }

        // Find screenshots gallery or lightbox overlay
        const gallery = document.querySelector('.screenshots-gallery');
        const lightbox = document.getElementById('screenshot-lightbox');
        
        // Determine insertion point: after lightbox if exists, otherwise after gallery
        let insertAfter = null;
        if (lightbox && lightbox.parentNode) {
            insertAfter = lightbox;
        } else if (gallery && gallery.parentNode) {
            insertAfter = gallery;
        }

        if (!insertAfter) {
            return; // No gallery found, skip button creation
        }

        // Create button container
        const container = document.createElement('div');
        container.className = 'download-button-container';

        // Create button
        const button = document.createElement('button');
        button.id = 'download-button';
        button.className = 'download-button';
        button.onclick = scrollToDownload;

        // Create button text span
        const textSpan = document.createElement('span');
        textSpan.className = 'download-button-text';
        textSpan.textContent = 'Download';

        // Create button icon span
        const iconSpan = document.createElement('span');
        iconSpan.className = 'download-button-icon';
        iconSpan.textContent = '↓';

        // Assemble button
        button.appendChild(textSpan);
        button.appendChild(iconSpan);
        container.appendChild(button);

        // Insert after gallery/lightbox
        if (insertAfter.nextSibling) {
            insertAfter.parentNode.insertBefore(container, insertAfter.nextSibling);
        } else {
            insertAfter.parentNode.appendChild(container);
        }
    }

    /**
     * Scroll to Download section
     * Supports multiple languages: Download, Скачать, Descargar, Herunterladen, etc.
     */
    function scrollToDownload() {
        // Possible download section headings in different languages
        const downloadHeadings = [
            'Download',
            'Скачать',
            'Descargar',
            'Herunterladen',
            'Télécharger',
            'Scarica',
            'ダウンロード',
            '下载',
            '다운로드'
        ];
        
        // Find all h2 headings
        const headings = document.querySelectorAll('h2');
        
        let targetHeading = null;
        
        // Search for download section heading
        for (const heading of headings) {
            const headingText = heading.textContent.trim();
            // Check if heading contains any of the download keywords
            for (const keyword of downloadHeadings) {
                if (headingText.toLowerCase().includes(keyword.toLowerCase())) {
                    targetHeading = heading;
                    break;
                }
            }
            if (targetHeading) {
                break;
            }
        }
        
        if (targetHeading) {
            // Scroll to the heading with smooth behavior
            targetHeading.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            
            // Add a highlight effect
            targetHeading.style.transition = 'background-color 0.3s ease';
            const originalBg = targetHeading.style.backgroundColor;
            targetHeading.style.backgroundColor = 'var(--md-primary-fg-color--lightest, rgba(64, 81, 181, 0.1))';
            
            setTimeout(() => {
                targetHeading.style.backgroundColor = originalBg;
                setTimeout(() => {
                    targetHeading.style.transition = '';
                }, 300);
            }, 2000);
        } else {
            // Fallback: try to find by ID or anchor
            const downloadAnchor = document.querySelector('#download, [id*="download"], [id*="скачать"]');
            if (downloadAnchor) {
                downloadAnchor.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    }

    // Make function available globally
    window.scrollToDownload = scrollToDownload;

    /**
     * Initialize download button when DOM is ready
     * Tries multiple times to find gallery in case it's added dynamically
     */
    function initDownloadButton() {
        let attempts = 0;
        const maxAttempts = 10; // Try for up to 1 second (10 * 100ms)
        
        function tryCreateButton() {
            attempts++;
            
            // Check if gallery exists
            const gallery = document.querySelector('.screenshots-gallery');
            const lightbox = document.getElementById('screenshot-lightbox');
            
            if (gallery || lightbox) {
                // Gallery found, create button
                createDownloadButton();
            } else if (attempts < maxAttempts) {
                // Gallery not found yet, try again
                setTimeout(tryCreateButton, 100);
            }
            // If max attempts reached and no gallery found, give up silently
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                tryCreateButton();
            });
        } else {
            // DOM already loaded
            tryCreateButton();
        }
    }

    // Initialize
    initDownloadButton();
})();

