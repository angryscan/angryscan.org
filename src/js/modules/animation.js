/**
 * Animation Manager Module
 * Handles scroll-triggered animations using Intersection Observer
 */

import { CONSTANTS } from '../core/constants.js';

export class AnimationManager {
    constructor() {
        // Can be extended with dependency injection
    }
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
    }

    /**
     * Prepare element for animation
     * @param {HTMLElement} element - Element to prepare
     */
    prepareElement(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `opacity ${CONSTANTS.ANIMATION.DURATION}ms ease, transform ${CONSTANTS.ANIMATION.DURATION}ms ease`;
    }

    /**
     * Animate element in
     * @param {HTMLElement} element - Element to animate
     */
    animateIn(element) {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }

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
}

