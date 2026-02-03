/**
 * Table Enhancement Module
 * Adds interactive enhancements to data tables
 */

import { CONSTANTS } from '../core/constants.js';

export class TableEnhancement {
    constructor() {
        // Can be extended with dependency injection
    }
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
}

