/**
 * Screenshots Gallery Lightbox
 * Handles opening/closing lightbox and navigation between images
 */

(function() {
    'use strict';

    let currentImageIndex = 0;
    let images = [];
    let lightbox = null;
    let lightboxImage = null;
    let lightboxClose = null;
    let lightboxPrev = null;
    let lightboxNext = null;

    /**
     * Initialize the lightbox functionality
     */
    function initLightbox() {
        // Get all screenshot links
        const screenshotLinks = document.querySelectorAll('.screenshot-link');
        
        if (screenshotLinks.length === 0) {
            return;
        }

        // Collect all image URLs
        images = Array.from(screenshotLinks).map(link => {
            const fullImage = link.getAttribute('data-full') || link.getAttribute('href');
            return fullImage;
        });

        // Get lightbox elements
        lightbox = document.getElementById('screenshot-lightbox');
        lightboxImage = document.getElementById('lightbox-image');
        lightboxClose = document.querySelector('.lightbox-close');
        lightboxPrev = document.querySelector('.lightbox-prev');
        lightboxNext = document.querySelector('.lightbox-next');

        if (!lightbox || !lightboxImage) {
            return;
        }

        // Add click handlers to screenshot links
        screenshotLinks.forEach((link, index) => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                openLightbox(index);
            });
        });

        // Close lightbox handlers
        if (lightboxClose) {
            lightboxClose.addEventListener('click', closeLightbox);
        }

        // Navigation handlers
        if (lightboxPrev) {
            lightboxPrev.addEventListener('click', function(e) {
                e.stopPropagation();
                showPreviousImage();
            });
        }

        if (lightboxNext) {
            lightboxNext.addEventListener('click', function(e) {
                e.stopPropagation();
                showNextImage();
            });
        }

        // Close on overlay click
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', handleKeyPress);
    }

    /**
     * Open lightbox with specified image
     */
    function openLightbox(index) {
        if (index < 0 || index >= images.length) {
            return;
        }

        currentImageIndex = index;
        updateLightboxImage();
        
        if (lightbox) {
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    }

    /**
     * Close lightbox
     */
    function closeLightbox() {
        if (lightbox) {
            lightbox.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }

    /**
     * Show previous image
     */
    function showPreviousImage() {
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        updateLightboxImage();
    }

    /**
     * Show next image
     */
    function showNextImage() {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        updateLightboxImage();
    }

    /**
     * Update lightbox image source
     */
    function updateLightboxImage() {
        if (lightboxImage && images[currentImageIndex]) {
            lightboxImage.src = images[currentImageIndex];
            lightboxImage.alt = `Screenshot ${currentImageIndex + 1}`;
        }

        // Update navigation button visibility
        if (lightboxPrev && lightboxNext) {
            if (images.length <= 1) {
                lightboxPrev.style.display = 'none';
                lightboxNext.style.display = 'none';
            } else {
                lightboxPrev.style.display = 'block';
                lightboxNext.style.display = 'block';
            }
        }
    }

    /**
     * Handle keyboard events
     */
    function handleKeyPress(e) {
        if (!lightbox || !lightbox.classList.contains('active')) {
            return;
        }

        switch(e.key) {
            case 'Escape':
                closeLightbox();
                break;
            case 'ArrowLeft':
                showPreviousImage();
                break;
            case 'ArrowRight':
                showNextImage();
                break;
        }
    }

    /**
     * Handle touch events for mobile navigation
     */
    function initTouchSupport() {
        if (!lightbox) {
            return;
        }

        let touchStartX = 0;
        let touchEndX = 0;

        lightbox.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        lightbox.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next image
                    showNextImage();
                } else {
                    // Swipe right - previous image
                    showPreviousImage();
                }
            }
        }
    }

    /**
     * Update scroll indicators for gallery
     */
    function updateScrollIndicators() {
        const gallery = document.querySelector('.screenshots-gallery');
        if (!gallery) {
            return;
        }

        const scrollLeft = gallery.scrollLeft;
        const scrollWidth = gallery.scrollWidth;
        const clientWidth = gallery.clientWidth;
        const isAtStart = scrollLeft <= 1;
        const isAtEnd = scrollLeft + clientWidth >= scrollWidth - 1;

        gallery.classList.toggle('scrolled-start', isAtStart);
        gallery.classList.toggle('scrolled-end', isAtEnd);
    }

    /**
     * Initialize scroll indicators for gallery
     */
    function initScrollIndicators() {
        const gallery = document.querySelector('.screenshots-gallery');
        if (!gallery) {
            return;
        }

        // Update on scroll
        gallery.addEventListener('scroll', updateScrollIndicators, { passive: true });

        // Update on resize
        window.addEventListener('resize', updateScrollIndicators, { passive: true });

        // Initial update
        updateScrollIndicators();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initLightbox();
            initTouchSupport();
            initScrollIndicators();
        });
    } else {
        initLightbox();
        initTouchSupport();
        initScrollIndicators();
    }
})();

