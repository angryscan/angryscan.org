// Table collapse functionality
// Automatically collapses tables with more than 5 data rows (excluding header)
// Adds a collapse/expand button as a table row with icon only

(function() {
    'use strict';
    
    const COLLAPSED_ICON = '▼'; // U+25BC Black Down-Pointing Triangle
    const EXPANDED_ICON = '▲';  // U+25B2 Black Up-Pointing Triangle
    const MAX_VISIBLE_ROWS = 5;
    
    /**
     * Counts data rows in table (excluding header)
     * @param {HTMLTableElement} table - The table element
     * @returns {number} Number of data rows
     */
    function countDataRows(table) {
        const tbody = table.querySelector('tbody');
        if (!tbody) {
            // If no tbody, count all tr elements except those in thead
            const thead = table.querySelector('thead');
            const allRows = table.querySelectorAll('tr');
            if (thead) {
                const headerRows = thead.querySelectorAll('tr');
                return allRows.length - headerRows.length;
            }
            return allRows.length;
        }
        
        const rows = tbody.querySelectorAll('tr');
        return rows.length;
    }
    
    /**
     * Counts visible data rows in table (excluding header, button rows, and filter-hidden rows)
     * Only counts rows that are visible (not hidden by filter)
     * @param {HTMLTableElement} table - The table element
     * @returns {number} Number of visible data rows (not hidden by filter)
     */
    function countVisibleDataRows(table) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return 0;
        
        const rows = tbody.querySelectorAll('tr');
        let count = 0;
        
        rows.forEach(row => {
            // Skip button rows
            if (row.classList.contains('table-collapse-button-row')) {
                return;
            }
            
            // Count only rows that are visible (not hidden by filter)
            // Rows hidden by collapse have class 'table-collapse-hidden-row' but we still count them
            // as they are part of the total visible rows (just collapsed)
            const computedStyle = window.getComputedStyle(row);
            // If row has display:none but doesn't have collapse class, it's hidden by filter
            const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
            
            if (!isFilterHidden) {
                count++;
            }
        });
        
        return count;
    }
    
    /**
     * Gets the number of columns in the table
     * @param {HTMLTableElement} table - The table element
     * @returns {number} Number of columns
     */
    function getColumnCount(table) {
        const thead = table.querySelector('thead');
        if (thead) {
            const headerRow = thead.querySelector('tr');
            if (headerRow) {
                const cells = headerRow.querySelectorAll('th, td');
                return cells.length;
            }
        }
        
        // Try to get from first data row
        const tbody = table.querySelector('tbody');
        if (tbody) {
            const firstRow = tbody.querySelector('tr');
            if (firstRow) {
                const cells = firstRow.querySelectorAll('td, th');
                return cells.length;
            }
        }
        
        // Fallback: try any row
        const firstRow = table.querySelector('tr');
        if (firstRow) {
            const cells = firstRow.querySelectorAll('td, th');
            return cells.length;
        }
        
        return 1; // Default to 1 column
    }
    
    /**
     * Creates a collapse/expand button row
     * @param {HTMLTableElement} table - The table element
     * @param {boolean} isCollapsed - Initial state
     * @returns {HTMLTableRowElement} The button row element
     */
    function createButtonRow(table, isCollapsed) {
        const row = document.createElement('tr');
        row.className = 'table-collapse-button-row';
        
        const cell = document.createElement('td');
        cell.className = 'table-collapse-button-cell';
        cell.setAttribute('colspan', getColumnCount(table));
        
        const button = document.createElement('button');
        button.className = 'table-collapse-button';
        button.setAttribute('type', 'button');
        button.setAttribute('aria-label', isCollapsed ? 'Expand table' : 'Collapse table');
        button.setAttribute('aria-expanded', !isCollapsed);
        button.textContent = isCollapsed ? COLLAPSED_ICON : EXPANDED_ICON;
        
        cell.appendChild(button);
        row.appendChild(cell);
        
        return row;
    }
    
    /**
     * Processes a single table
     * @param {HTMLTableElement} table - The table element
     */
    function processTable(table) {
        // Skip if already processed
        if (table.dataset.collapseProcessed === 'true') {
            return;
        }
        
        // Mark as processed
        table.dataset.collapseProcessed = 'true';
        
        const dataRowCount = countDataRows(table);
        
        // Only process tables with more than MAX_VISIBLE_ROWS rows
        if (dataRowCount <= MAX_VISIBLE_ROWS) {
            return;
        }
        
        // Get or create tbody
        let tbody = table.querySelector('tbody');
        if (!tbody) {
            // If no tbody exists, create one and move all non-header rows into it
            tbody = document.createElement('tbody');
            const thead = table.querySelector('thead');
            const allRows = Array.from(table.querySelectorAll('tr'));
            
            allRows.forEach(row => {
                // Skip rows that are already in thead
                if (thead && thead.contains(row)) {
                    return;
                }
                // Skip button rows
                if (row.classList.contains('table-collapse-button-row')) {
                    return;
                }
                tbody.appendChild(row);
            });
            
            // Insert tbody after thead or at the beginning
            if (thead) {
                thead.parentNode.insertBefore(tbody, thead.nextSibling);
            } else {
                table.insertBefore(tbody, table.firstChild);
            }
        }
        
        // Save column widths to prevent table width changes when collapsing/expanding
        const thead = table.querySelector('thead');
        const columnWidths = [];
        
        if (thead) {
            const headerRow = thead.querySelector('tr');
            if (headerRow) {
                const headerCells = headerRow.querySelectorAll('th, td');
                headerCells.forEach((cell, index) => {
                    // Get computed width and save it
                    const computedWidth = window.getComputedStyle(cell).width;
                    if (computedWidth) {
                        columnWidths[index] = computedWidth;
                        cell.dataset.originalWidth = computedWidth;
                        cell.style.width = computedWidth;
                        cell.style.minWidth = computedWidth;
                    }
                });
                
                // Apply saved widths to all cells in corresponding columns
                const allRows = tbody.querySelectorAll('tr');
                allRows.forEach(row => {
                    // Skip button rows
                    if (row.classList.contains('table-collapse-button-row')) {
                        return;
                    }
                    const cells = row.querySelectorAll('td, th');
                    cells.forEach((cell, index) => {
                        if (columnWidths[index]) {
                            cell.style.width = columnWidths[index];
                            cell.style.minWidth = columnWidths[index];
                        }
                    });
                });
            }
        }
        
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Hide rows beyond MAX_VISIBLE_ROWS
        let visibleRowCount = 0;
        const hiddenRows = [];
        
        rows.forEach((row, index) => {
            // Skip if this is a button row
            if (row.classList.contains('table-collapse-button-row')) {
                return;
            }
            
            if (visibleRowCount < MAX_VISIBLE_ROWS) {
                visibleRowCount++;
            } else {
                row.style.display = 'none';
                row.classList.add('table-collapse-hidden-row');
                row.dataset.collapseHidden = 'true';
                hiddenRows.push(row);
            }
        });
        
        // Only add button if there are hidden rows
        if (hiddenRows.length === 0) {
            return;
        }
        
        // Create and add button row
        const buttonRow = createButtonRow(table, true);
        tbody.appendChild(buttonRow);
        
        // Store references for later updates
        table._collapseData = {
            buttonRow: buttonRow,
            button: null, // Will be set below
            hiddenRows: hiddenRows,
            columnWidths: columnWidths,
            isCollapsed: true,
            clickHandler: null // Store handler reference
        };
        
        // Add click handler
        const button = buttonRow.querySelector('.table-collapse-button');
        table._collapseData.button = button;
        let isCollapsed = true; // Track state
        
        // Create click handler function
        const clickHandler = function() {
            const collapseData = table._collapseData;
            if (collapseData.isCollapsed) {
                // Expand: show all hidden rows (only if not hidden by filter)
                collapseData.hiddenRows.forEach(row => {
                    // Check if row is hidden by filter (has display:none but no collapse class)
                    const computedStyle = window.getComputedStyle(row);
                    const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
                    
                    // Only show if not hidden by filter
                    if (!isFilterHidden) {
                        // Apply saved column widths to cells in this row
                        const cells = row.querySelectorAll('td, th');
                        cells.forEach((cell, index) => {
                            if (collapseData.columnWidths[index]) {
                                cell.style.width = collapseData.columnWidths[index];
                                cell.style.minWidth = collapseData.columnWidths[index];
                            }
                        });
                        row.style.display = 'table-row';
                        row.classList.remove('table-collapse-hidden-row');
                    }
                });
                collapseData.button.textContent = EXPANDED_ICON;
                collapseData.button.setAttribute('aria-expanded', 'true');
                collapseData.button.setAttribute('aria-label', 'Collapse table');
                collapseData.isCollapsed = false;
            } else {
                // Collapse: hide rows beyond MAX_VISIBLE_ROWS
                collapseData.hiddenRows.forEach(row => {
                    // Check if row is currently visible (not hidden by filter)
                    const computedStyle = window.getComputedStyle(row);
                    const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
                    
                    // Only hide if currently visible (not hidden by filter)
                    if (!isFilterHidden) {
                        row.style.display = 'none';
                        row.classList.add('table-collapse-hidden-row');
                    }
                });
                collapseData.button.textContent = COLLAPSED_ICON;
                collapseData.button.setAttribute('aria-expanded', 'false');
                collapseData.button.setAttribute('aria-label', 'Expand table');
                collapseData.isCollapsed = true;
            }
        };
        
        // Store handler reference
        table._collapseData.clickHandler = clickHandler;
        
        // Attach handler
        button.addEventListener('click', clickHandler);
    }
    
    /**
     * Updates collapse state for a table based on visible rows
     * @param {HTMLTableElement} table - The table element
     */
    function updateCollapseState(table) {
        if (!table._collapseData) {
            return; // Table not processed by collapse script
        }
        
        // Prevent infinite loops - if already updating, skip
        if (table._collapseUpdating) {
            return;
        }
        
        // Set flag to prevent recursive updates
        table._collapseUpdating = true;
        
        const collapseData = table._collapseData;
        const tbody = table.querySelector('tbody');
        if (!tbody) {
            table._collapseUpdating = false;
            return;
        }
        
        // Save current collapse state before updating
        const wasExpanded = !collapseData.isCollapsed;
        
        // First, show all rows that were hidden by collapse
        // Filter has already set display for all rows before this function is called
        // So we need to remove collapse hiding while preserving filter's display settings
        collapseData.hiddenRows.forEach(row => {
            // If row has collapse markers, remove them
            if (row.classList.contains('table-collapse-hidden-row') || row.dataset.collapseHidden === 'true') {
                row.classList.remove('table-collapse-hidden-row');
                delete row.dataset.collapseHidden;
                // Remove collapse's display:none, but check if filter wants it hidden
                // Filter has already set display - check computed style to see final result
                const computedDisplay = window.getComputedStyle(row).display;
                // If computed display is 'none', filter wants it hidden, don't change
                // If computed display is not 'none', filter wants it shown, remove our 'none'
                if (computedDisplay !== 'none' && row.style.display === 'none') {
                    // Filter wants it shown, remove our collapse hiding
                    row.style.display = '';
                }
                // If computed display is 'none', filter wants it hidden, leave it as is
            }
        });
        
        // Count visible rows (not hidden by filter)
        const visibleRowCount = countVisibleDataRows(table);
        
        // If visible rows <= MAX_VISIBLE_ROWS, hide button but keep data for future use
        if (visibleRowCount <= MAX_VISIBLE_ROWS) {
            // All rows are already visible (collapse was removed above)
            // Remove button row but keep collapse data
            if (collapseData.buttonRow && collapseData.buttonRow.parentNode) {
                collapseData.buttonRow.remove();
            }
            // Mark that collapse is not needed right now, but keep data structure
            collapseData.hiddenRows = [];
            collapseData.isCollapsed = false;
            // Don't delete collapseData - we'll need it if rows become > 5 again
            table._collapseUpdating = false;
            return;
        }
        
        // Recalculate which rows should be hidden
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const newHiddenRows = [];
        let visibleCount = 0;
        
        rows.forEach(row => {
            // Skip button rows
            if (row.classList.contains('table-collapse-button-row')) {
                return;
            }
            
            // Check if row is visible (not hidden by filter)
            // Filter sets display:none directly, so we check computed style
            const computedStyle = window.getComputedStyle(row);
            const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
            
            if (isFilterHidden) {
                return; // Skip rows hidden by filter
            }
            
            // Row is visible by filter, now decide if it should be collapsed
            if (visibleCount < MAX_VISIBLE_ROWS) {
                // Show this row - remove collapse hiding
                // Don't touch display - let filter control it
                row.classList.remove('table-collapse-hidden-row');
                visibleCount++;
            } else {
                // Hide this row with collapse
                // Only hide if filter hasn't already hidden it
                // Check both inline style and computed style
                const inlineDisplay = row.style.display;
                const computedDisplay = window.getComputedStyle(row).display;
                
                // If filter has set display='none' in inline style, don't touch it
                // If filter has set display='' or display='table-row', we can hide it with collapse
                // If computed display is 'none', filter wants it hidden
                if (computedDisplay !== 'none') {
                    // Filter wants this row visible, but collapse should hide it
                    // Set display='none' but filter can override by setting display='' again
                    row.style.display = 'none';
                    row.classList.add('table-collapse-hidden-row');
                    row.dataset.collapseHidden = 'true';
                    newHiddenRows.push(row);
                }
            }
        });
        
        // Update hidden rows reference
        collapseData.hiddenRows = newHiddenRows;
        
        // Restore previous collapse state (expanded or collapsed)
        collapseData.isCollapsed = !wasExpanded;
        
        // If table was expanded, show all hidden rows
        if (wasExpanded) {
            collapseData.hiddenRows.forEach(row => {
                // Check if row is hidden by filter
                const computedStyle = window.getComputedStyle(row);
                const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
                
                // Only show if not hidden by filter
                if (!isFilterHidden) {
                    // Apply saved column widths to cells in this row
                    const cells = row.querySelectorAll('td, th');
                    cells.forEach((cell, index) => {
                        if (collapseData.columnWidths[index]) {
                            cell.style.width = collapseData.columnWidths[index];
                            cell.style.minWidth = collapseData.columnWidths[index];
                        }
                    });
                    row.style.display = 'table-row';
                    row.classList.remove('table-collapse-hidden-row');
                    delete row.dataset.collapseHidden;
                }
            });
        }
        
        // Ensure button exists - create if it was removed
        if (!collapseData.buttonRow || !collapseData.buttonRow.parentNode) {
            // Button was removed, create it again with correct initial state
            const buttonRow = createButtonRow(table, collapseData.isCollapsed);
            collapseData.buttonRow = buttonRow;
            collapseData.button = buttonRow.querySelector('.table-collapse-button');
            tbody.appendChild(buttonRow);
            
            // Re-attach click handler if it exists
            if (collapseData.clickHandler) {
                collapseData.button.addEventListener('click', collapseData.clickHandler);
            } else {
                // Create new handler if it doesn't exist
                const clickHandler = function() {
                    const collapseData = table._collapseData;
                    if (collapseData.isCollapsed) {
                        // Expand: show all hidden rows (only if not hidden by filter)
                        collapseData.hiddenRows.forEach(row => {
                            // Check if row is hidden by filter (has display:none but no collapse class)
                            const computedStyle = window.getComputedStyle(row);
                            const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
                            
                            // Only show if not hidden by filter
                            if (!isFilterHidden) {
                                // Apply saved column widths to cells in this row
                                const cells = row.querySelectorAll('td, th');
                                cells.forEach((cell, index) => {
                                    if (collapseData.columnWidths[index]) {
                                        cell.style.width = collapseData.columnWidths[index];
                                        cell.style.minWidth = collapseData.columnWidths[index];
                                    }
                                });
                                row.style.display = 'table-row';
                                row.classList.remove('table-collapse-hidden-row');
                            }
                        });
                        collapseData.button.textContent = EXPANDED_ICON;
                        collapseData.button.setAttribute('aria-expanded', 'true');
                        collapseData.button.setAttribute('aria-label', 'Collapse table');
                        collapseData.isCollapsed = false;
                    } else {
                        // Collapse: hide rows beyond MAX_VISIBLE_ROWS
                        collapseData.hiddenRows.forEach(row => {
                            // Check if row is currently visible (not hidden by filter)
                            const computedStyle = window.getComputedStyle(row);
                            const isFilterHidden = computedStyle.display === 'none' && !row.classList.contains('table-collapse-hidden-row');
                            
                            // Only hide if currently visible (not hidden by filter)
                            if (!isFilterHidden) {
                                row.style.display = 'none';
                                row.classList.add('table-collapse-hidden-row');
                            }
                        });
                        collapseData.button.textContent = COLLAPSED_ICON;
                        collapseData.button.setAttribute('aria-expanded', 'false');
                        collapseData.button.setAttribute('aria-label', 'Expand table');
                        collapseData.isCollapsed = true;
                    }
                };
                // Store handler reference
                collapseData.clickHandler = clickHandler;
                collapseData.button.addEventListener('click', clickHandler);
            }
        } else {
            // Button exists, update its state based on collapse state
            if (collapseData.isCollapsed) {
                collapseData.button.textContent = COLLAPSED_ICON;
                collapseData.button.setAttribute('aria-expanded', 'false');
                collapseData.button.setAttribute('aria-label', 'Expand table');
            } else {
                collapseData.button.textContent = EXPANDED_ICON;
                collapseData.button.setAttribute('aria-expanded', 'true');
                collapseData.button.setAttribute('aria-label', 'Collapse table');
            }
        }
        
        // Clear update flag
        table._collapseUpdating = false;
    }
    
    /**
     * Processes all tables on the page
     */
    function processAllTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            processTable(table);
        });
    }
    
    /**
     * Initialization function
     */
    function init() {
        // Process tables immediately if DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', processAllTables);
        } else {
            processAllTables();
        }
        
        // Watch for dynamically added tables
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.tagName === 'TABLE') {
                                processTable(node);
                            } else {
                                // Check for tables inside added element
                                const tables = node.querySelectorAll && node.querySelectorAll('table');
                                if (tables) {
                                    tables.forEach(table => {
                                        processTable(table);
                                    });
                                }
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Listen for filter change events from country filter script
        document.addEventListener('tableFilterChanged', function(event) {
            const table = event.detail.table;
            if (table && table._collapseData && !table._collapseUpdating) {
                // Update collapse state when filter changes
                clearTimeout(table._collapseUpdateTimeout);
                table._collapseUpdateTimeout = setTimeout(function() {
                    if (!table._collapseUpdating) {
                        updateCollapseState(table);
                    }
                }, 150);
            }
        });
    }
    
    // Start initialization
    init();
})();

