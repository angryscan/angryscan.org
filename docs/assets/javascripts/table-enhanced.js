// Enhanced table functionality
// Combines country filtering and table collapse functionality
// Automatically collapses tables with more than 5 data rows and adds country filter for tables with Country column
// Compatible with MkDocs Material theme

(function() {
    'use strict';
    
    const COLLAPSED_ICON = '▼';
    const EXPANDED_ICON = '▲';
    const MAX_VISIBLE_ROWS = 5;
    const GLOBE_ICON = '🌐';
    
    // Language detection
    function getCurrentLanguage() {
        const path = window.location.pathname;
        const langMap = { '/ru/': 'ru', '/es/': 'es', '/de/': 'de', '/fr/': 'fr' };
        return Object.entries(langMap).find(([prefix]) => path.startsWith(prefix))?.[1] || 'en';
    }
    
    // Configuration
    const countryColumnNames = {
        'en': ['Country', 'country'],
        'ru': ['Страна', 'страна'],
        'es': ['País', 'país', 'Country', 'country'],
        'de': ['Land', 'land', 'Country', 'country'],
        'fr': ['Pays', 'pays', 'Country', 'country']
    };
    
    const countryFlagMapping = {
        'RU': 'ru', 'US': 'us', 'CN': 'cn', 'GB': 'gb', 'DE': 'de', 'FR': 'fr', 'ES': 'es',
        'IT': 'it', 'JP': 'jp', 'KR': 'kr', 'IN': 'in', 'BR': 'br', 'CA': 'ca', 'AU': 'au',
        'MX': 'mx', 'International': 'un'
    };
    
    const translations = {
        'en': { allCountries: 'All' },
        'ru': { allCountries: 'Все' },
        'es': { allCountries: 'Todos' },
        'de': { allCountries: 'Alle' },
        'fr': { allCountries: 'Tous' }
    };
    
    // Utility functions
    function getCountryFlagCode(country) {
        return countryFlagMapping[country] || countryFlagMapping[country?.toUpperCase()] || null;
    }
    
    function getFlagUrl(countryCode) {
        return countryCode ? `https://flagcdn.com/w40/${countryCode.toLowerCase()}.png` : null;
    }
    
    function getDataRows(table) {
        const tbody = table.querySelector('tbody') || table;
        return Array.from(tbody.querySelectorAll('tr')).filter(
            row => !row.classList.contains('table-collapse-button-row')
        );
    }
    
    function countDataRows(table) {
        return getDataRows(table).length;
    }
    
    function getColumnCount(table) {
        const headerRow = table.querySelector('thead tr') || table.querySelector('tbody tr') || table.querySelector('tr');
        return headerRow?.querySelectorAll('th, td').length || 1;
    }
    
    function findCountryColumnIndex(table) {
        const headerRow = table.querySelector('thead tr');
        if (!headerRow) return -1;
        
        const headers = headerRow.querySelectorAll('th, td');
        const countryNames = countryColumnNames[getCurrentLanguage()] || countryColumnNames['en'];
        
        for (let i = 0; i < headers.length; i++) {
            const headerText = headers[i].textContent.trim().toLowerCase();
            if (countryNames.some(name => headerText === name.toLowerCase())) {
                return i;
            }
        }
        return -1;
    }
    
    function getCountriesFromTable(table, countryColumnIndex) {
        const countries = new Set();
        getDataRows(table).forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const country = cells[countryColumnIndex]?.textContent.trim();
            if (country) countries.add(country);
        });
        return Array.from(countries).sort();
    }
    
    function findPreviousHeader(table) {
        // Ищем заголовок h2, h3 или h4 перед таблицей
        // Сначала проверяем прямых соседей таблицы
        let element = table.previousElementSibling;
        while (element) {
            if (/^H[2-4]$/.test(element.tagName)) {
                return element;
            }
            // Если встретили h1 - останавливаемся
            if (/^H[1]$/.test(element.tagName)) {
                break;
            }
            element = element.previousElementSibling;
        }
        
        // Если таблица внутри md-typeset__scrollwrap, ищем заголовок вне этого контейнера
        const scrollWrap = table.closest('.md-typeset__scrollwrap');
        if (scrollWrap) {
            // Ищем заголовок перед scrollWrap контейнером
            element = scrollWrap.previousElementSibling;
            while (element) {
                if (/^H[2-4]$/.test(element.tagName)) {
                    return element;
                }
                if (/^H[1]$/.test(element.tagName)) {
                    break;
                }
                element = element.previousElementSibling;
            }
            
            // Если не нашли среди соседей scrollWrap, ищем в родительском контейнере
            let parent = scrollWrap.parentElement;
            while (parent && parent.tagName !== 'BODY' && parent.tagName !== 'HTML') {
                const allChildren = Array.from(parent.children);
                const scrollWrapIndex = allChildren.indexOf(scrollWrap);
                
                if (scrollWrapIndex > 0) {
                    // Ищем заголовок перед scrollWrap в этом родителе
                    for (let i = scrollWrapIndex - 1; i >= 0; i--) {
                        const elem = allChildren[i];
                        if (/^H[2-4]$/.test(elem.tagName)) {
                            return elem;
                        }
                        if (/^H[1]$/.test(elem.tagName)) {
                            break;
                        }
                    }
                }
                
                parent = parent.parentElement;
            }
        } else {
            // Если таблица не в scrollWrap, ищем в родительском контейнере
            let parent = table.parentElement;
            while (parent && parent.tagName !== 'BODY' && parent.tagName !== 'HTML') {
                const allChildren = Array.from(parent.children);
                const tableIndex = allChildren.indexOf(table);
                
                if (tableIndex > 0) {
                    // Ищем заголовок перед таблицей в этом родителе
                    for (let i = tableIndex - 1; i >= 0; i--) {
                        const elem = allChildren[i];
                        if (/^H[2-4]$/.test(elem.tagName)) {
                            return elem;
                        }
                        if (/^H[1]$/.test(elem.tagName)) {
                            break;
                        }
                    }
                }
                
                parent = parent.parentElement;
            }
        }
        
        return null;
    }
    
    function rowPassesFilter(row, countryColumnIndex, selectedCountry) {
        if (countryColumnIndex === -1 || !selectedCountry) return true;
        const cells = row.querySelectorAll('td, th');
        return cells[countryColumnIndex]?.textContent.trim() === selectedCountry;
    }
    
    // UI creation
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
    
    function createCountryOption(value, flagUrlOrIcon, label, isAll) {
        const option = document.createElement('div');
        option.className = 'country-filter-option';
        option.dataset.country = value;
        
        const flagElement = document.createElement('div');
        flagElement.className = 'country-filter-flag';
        if (!isAll && flagUrlOrIcon && !flagUrlOrIcon.startsWith(GLOBE_ICON)) {
            flagElement.className += ' has-flag';
            flagElement.style.backgroundImage = `url('${flagUrlOrIcon}')`;
        } else {
            flagElement.textContent = GLOBE_ICON;
        }
        
        const labelElement = document.createElement('span');
        labelElement.className = 'country-filter-label';
        labelElement.textContent = label;
        
        option.appendChild(flagElement);
        option.appendChild(labelElement);
        return option;
    }
    
    function createCountrySelector(countries, currentLang) {
        const container = document.createElement('div');
        container.className = 'country-filter-container';
        
        const buttonWrapper = document.createElement('div');
        buttonWrapper.className = 'country-filter-button-wrapper';
        
        const button = document.createElement('button');
        button.className = 'country-filter-button';
        button.setAttribute('aria-label', 'Select country');
        
        const flagContainer = document.createElement('span');
        flagContainer.className = 'country-filter-button-flag';
        flagContainer.textContent = GLOBE_ICON;
        
        const selectedText = document.createElement('span');
        selectedText.className = 'country-filter-selected-text';
        selectedText.textContent = translations[currentLang]?.allCountries || 'All';
        
        button.appendChild(flagContainer);
        button.appendChild(selectedText);
        
        const dropdown = document.createElement('div');
        dropdown.className = 'country-filter-dropdown';
        dropdown.appendChild(createCountryOption('', GLOBE_ICON, selectedText.textContent, true));
        dropdown.appendChild(Object.assign(document.createElement('div'), { className: 'country-filter-divider' }));
        
        countries.forEach(country => {
            const flagUrl = getFlagUrl(getCountryFlagCode(country));
            dropdown.appendChild(createCountryOption(country, flagUrl, country, false));
        });
        
        buttonWrapper.appendChild(button);
        buttonWrapper.appendChild(dropdown);
        container.appendChild(buttonWrapper);
        
        let hoverTimeout, isClosing = false;
        
        button.addEventListener('click', e => {
            e.stopPropagation();
            clearTimeout(hoverTimeout);
            isClosing = false;
            dropdown.classList.toggle('show');
        });
        
        buttonWrapper.addEventListener('mouseenter', () => {
            if (!isClosing) {
                clearTimeout(hoverTimeout);
                dropdown.classList.add('show');
            }
        });
        
        buttonWrapper.addEventListener('mouseleave', () => {
            if (dropdown.classList.contains('show') && !isClosing) {
                hoverTimeout = setTimeout(() => dropdown.classList.remove('show'), 100);
            }
        });
        
        document.addEventListener('click', e => {
            if (!buttonWrapper.contains(e.target)) {
                clearTimeout(hoverTimeout);
                dropdown.classList.remove('show');
            }
        });
        
        return { container, button, dropdown, selectedText, flagContainer, setClosing: v => isClosing = v };
    }
    
    function hideCountryColumn(table, countryColumnIndex) {
        const hideCell = (cell) => cell && (cell.style.display = 'none');
        const headerRow = table.querySelector('thead tr');
        if (headerRow) hideCell(headerRow.querySelectorAll('th, td')[countryColumnIndex]);
        
        getDataRows(table).forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells[countryColumnIndex]) hideCell(cells[countryColumnIndex]);
        });
    }
    
    function applyColumnWidths(cells, columnWidths) {
        cells.forEach((cell, index) => {
            if (columnWidths[index]) {
                cell.style.width = cell.style.minWidth = columnWidths[index];
            }
        });
    }
    
    function saveColumnWidths(table) {
        const thead = table.querySelector('thead');
        if (!thead) return null;
        
        const headerRow = thead.querySelector('tr');
        if (!headerRow) return null;
        
        const headerCells = headerRow.querySelectorAll('th, td');
        const columnWidths = [];
        
        headerCells.forEach((cell, index) => {
            const width = window.getComputedStyle(cell).width;
            if (width) {
                columnWidths[index] = width;
                cell.dataset.originalWidth = width;
                cell.style.width = cell.style.minWidth = width;
            }
        });
        
        getDataRows(table).forEach(row => {
            applyColumnWidths(row.querySelectorAll('td, th'), columnWidths);
        });
        
        return columnWidths;
    }
    
    function updateTableVisibility(table) {
        const tableData = table._tableData;
        if (!tableData || tableData.updating) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        tableData.updating = true;
        
        const dataRows = getDataRows(table);
        const selectedCountry = tableData.selectedCountry || '';
        const isExpanded = !tableData.isCollapsed;
        
        // Filter rows
        const filteredRows = dataRows.filter(row => 
            rowPassesFilter(row, tableData.countryColumnIndex, selectedCountry)
        );
        
        // Apply collapse
        const visibleRows = [];
        const hiddenRows = [];
        let visibleCount = 0;
        
        filteredRows.forEach(row => {
            const shouldBeVisible = !tableData.needsCollapse || visibleCount < MAX_VISIBLE_ROWS || isExpanded;
            if (shouldBeVisible && visibleCount < MAX_VISIBLE_ROWS) visibleCount++;
            
            (shouldBeVisible ? visibleRows : hiddenRows).push(row);
        });
        
        // Hide rows that don't pass filter
        dataRows.forEach(row => {
            if (!filteredRows.includes(row)) hiddenRows.push(row);
        });
        
        // Apply visibility changes synchronously
        dataRows.forEach(row => {
            const shouldBeVisible = visibleRows.includes(row);
            row.style.display = shouldBeVisible ? '' : 'none';
            
            if (shouldBeVisible) {
                row.classList.remove('table-collapse-hidden-row');
                delete row.dataset.collapseHidden;
                if (tableData.columnWidths) {
                    applyColumnWidths(row.querySelectorAll('td, th'), tableData.columnWidths);
                }
            } else {
                row.classList.add('table-collapse-hidden-row');
                row.dataset.collapseHidden = 'true';
            }
        });
        
        tableData.hiddenRows = hiddenRows;
        updateCollapseButton(table);
        tableData.updating = false;
    }
    
    function updateCollapseButton(table) {
        const tableData = table._tableData;
        if (!tableData?.needsCollapse) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        const filteredRowCount = getDataRows(table).filter(row => 
            rowPassesFilter(row, tableData.countryColumnIndex, tableData.selectedCountry || '')
        ).length;
        
        if (filteredRowCount <= MAX_VISIBLE_ROWS) {
            tableData.buttonRow?.parentNode?.removeChild(tableData.buttonRow);
            return;
        }
        
        if (!tableData.buttonRow?.parentNode) {
            const buttonRow = createButtonRow(table, tableData.isCollapsed);
            tableData.buttonRow = buttonRow;
            tableData.button = buttonRow.querySelector('.table-collapse-button');
            tbody.appendChild(buttonRow);
            
            tableData.button?.addEventListener('click', () => {
                tableData.isCollapsed = !tableData.isCollapsed;
                updateTableVisibility(table);
            });
        }
        
        if (tableData.button) {
            const isCollapsed = tableData.isCollapsed;
            tableData.button.textContent = isCollapsed ? COLLAPSED_ICON : EXPANDED_ICON;
            tableData.button.setAttribute('aria-expanded', !isCollapsed);
            tableData.button.setAttribute('aria-label', isCollapsed ? 'Expand table' : 'Collapse table');
        }
    }
    
    function updateFilterButton(flagContainer, selectedText, selectedCountry, allCountriesText) {
        if (selectedCountry) {
            const flagUrl = getFlagUrl(getCountryFlagCode(selectedCountry));
            if (flagUrl) {
                flagContainer.style.backgroundImage = `url('${flagUrl}')`;
                flagContainer.textContent = '';
                flagContainer.classList.add('has-flag');
                selectedText.textContent = selectedCountry;
                return;
            }
        }
        flagContainer.style.backgroundImage = 'none';
        flagContainer.textContent = GLOBE_ICON;
        flagContainer.classList.remove('has-flag');
        selectedText.textContent = allCountriesText;
    }
    
    function processTable(table) {
        if (table.dataset.tableEnhancedProcessed === 'true') return;
        
        table.dataset.tableEnhancedProcessed = 'true';
        table.dataset.collapseProcessed = 'true';
        
        // Ensure tbody exists
        let tbody = table.querySelector('tbody');
        if (!tbody) {
            tbody = document.createElement('tbody');
            const thead = table.querySelector('thead');
            const allRows = Array.from(table.querySelectorAll('tr'));
            
            allRows.forEach(row => {
                if (!thead?.contains(row) && !row.classList.contains('table-collapse-button-row')) {
                    tbody.appendChild(row);
                }
            });
            
            (thead ? thead.parentNode : table).insertBefore(tbody, thead?.nextSibling || table.firstChild);
        }
        
        const tableData = {
            countryColumnIndex: -1,
            selectedCountry: '',
            needsCollapse: false,
            isCollapsed: true,
            hiddenRows: [],
            columnWidths: null,
            buttonRow: null,
            button: null,
            updating: false
        };
        
        table._tableData = tableData;
        
        // Setup country filter if needed
        const countryColumnIndex = findCountryColumnIndex(table);
        if (countryColumnIndex !== -1) {
            tableData.countryColumnIndex = countryColumnIndex;
            const countries = getCountriesFromTable(table, countryColumnIndex);
            
            if (countries.length > 0) {
                const currentLang = getCurrentLanguage();
                const { container, dropdown, selectedText, flagContainer, setClosing } = 
                    createCountrySelector(countries, currentLang);
                
                // Ищем заголовок h2, h3 или h4 перед таблицей
                const header = findPreviousHeader(table);
                if (header && header.parentNode) {
                    // Проверяем, есть ли уже обертка для заголовка
                    let headerWrapper = header.closest('.table-header-with-filter');
                    if (!headerWrapper) {
                        // Создаем обертку для заголовка и фильтра
                        headerWrapper = document.createElement('div');
                        headerWrapper.className = 'table-header-with-filter';
                        // Заменяем заголовок на обертку с заголовком внутри
                        header.parentNode.insertBefore(headerWrapper, header);
                        headerWrapper.appendChild(header);
                    }
                    // Добавляем фильтр в обертку после заголовка
                    headerWrapper.appendChild(container);
                } else {
                    // Если заголовок не найден, добавляем фильтр перед таблицей
                    table.parentNode?.insertBefore(container, table);
                }
                
                hideCountryColumn(table, countryColumnIndex);
                
                const allCountriesText = translations[currentLang]?.allCountries || 'All';
                dropdown.querySelectorAll('.country-filter-option').forEach(option => {
                    option.addEventListener('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        
                        tableData.selectedCountry = this.dataset.country || '';
                        
                        setClosing(true);
                        dropdown.classList.remove('show');
                        setTimeout(() => setClosing(false), 150);
                        
                        updateFilterButton(flagContainer, selectedText, tableData.selectedCountry, allCountriesText);
                        updateTableVisibility(table);
                    });
                });
            }
        }
        
        // Setup collapse if needed
        if (countDataRows(table) > MAX_VISIBLE_ROWS) {
            tableData.needsCollapse = true;
            tableData.columnWidths = saveColumnWidths(table);
        }
        
        updateTableVisibility(table);
    }
    
    function processAllTables() {
        document.querySelectorAll('table').forEach(processTable);
    }
    
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', processAllTables);
        } else {
            processAllTables();
        }
        
        new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) {
                            if (node.tagName === 'TABLE') {
                                processTable(node);
                            } else {
                                node.querySelectorAll?.('table').forEach(processTable);
                            }
                        }
                    });
                }
            });
        }).observe(document.body, { childList: true, subtree: true });
    }
    
    init();
})();
