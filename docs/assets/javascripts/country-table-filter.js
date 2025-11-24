// Country table filter
// Analyzes tables on the page and adds country filter for tables with Country column
// Compatible with MkDocs Material theme

(function() {
    'use strict';
    
    // Определяем текущий язык по URL
    function getCurrentLanguage() {
        const path = window.location.pathname;
        if (path.startsWith('/ru/')) return 'ru';
        if (path.startsWith('/es/')) return 'es';
        if (path.startsWith('/de/')) return 'de';
        if (path.startsWith('/fr/')) return 'fr';
        return 'en'; // по умолчанию английский
    }
    
    // Переводы названия колонки "Country" на разные языки
    const countryColumnNames = {
        'en': ['Country', 'country'],
        'ru': ['Страна', 'страна'],
        'es': ['País', 'país', 'Country', 'country'],
        'de': ['Land', 'land', 'Country', 'country'],
        'fr': ['Pays', 'pays', 'Country', 'country']
    };
    
    // Маппинг кодов стран на ISO коды для флагов
    const countryFlagMapping = {
        'RU': 'ru',
        'US': 'us',
        'CN': 'cn',
        'GB': 'gb',
        'DE': 'de',
        'FR': 'fr',
        'ES': 'es',
        'IT': 'it',
        'JP': 'jp',
        'KR': 'kr',
        'IN': 'in',
        'BR': 'br',
        'CA': 'ca',
        'AU': 'au',
        'MX': 'mx',
        'International': 'un' // Используем флаг ООН для International
    };
    
    // Получает код флага для страны
    function getCountryFlagCode(country) {
        // Если страна уже является кодом (RU, US и т.д.)
        if (countryFlagMapping[country]) {
            return countryFlagMapping[country];
        }
        // Пробуем найти по ключу без учета регистра
        const upperCountry = country.toUpperCase();
        if (countryFlagMapping[upperCountry]) {
            return countryFlagMapping[upperCountry];
        }
        // Если не найдено, возвращаем null (без флага)
        return null;
    }
    
    // Получает URL флага
    function getFlagUrl(countryCode) {
        if (!countryCode) return null;
        return `https://flagcdn.com/w40/${countryCode.toLowerCase()}.png`;
    }
    
    // Переводы для селектора
    const translations = {
        'en': {
            countryLabel: 'Country:',
            allCountries: 'All'
        },
        'ru': {
            countryLabel: 'Страна:',
            allCountries: 'Все'
        },
        'es': {
            countryLabel: 'País:',
            allCountries: 'Todos'
        },
        'de': {
            countryLabel: 'Land:',
            allCountries: 'Alle'
        },
        'fr': {
            countryLabel: 'Pays:',
            allCountries: 'Tous'
        }
    };
    
    // Находит индекс колонки Country в заголовке таблицы
    function findCountryColumnIndex(table) {
        const thead = table.querySelector('thead');
        if (!thead) return -1;
        
        const headerRow = thead.querySelector('tr');
        if (!headerRow) return -1;
        
        const headers = headerRow.querySelectorAll('th, td');
        const currentLang = getCurrentLanguage();
        const countryNames = countryColumnNames[currentLang] || countryColumnNames['en'];
        
        for (let i = 0; i < headers.length; i++) {
            const headerText = headers[i].textContent.trim();
            if (countryNames.some(name => headerText.toLowerCase() === name.toLowerCase())) {
                return i;
            }
        }
        
        return -1;
    }
    
    // Получает список уникальных стран из таблицы
    function getCountriesFromTable(table, countryColumnIndex) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return [];
        
        const rows = tbody.querySelectorAll('tr');
        const countries = new Set();
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells[countryColumnIndex]) {
                const country = cells[countryColumnIndex].textContent.trim();
                if (country) {
                    countries.add(country);
                }
            }
        });
        
        return Array.from(countries).sort();
    }
    
    // Создает минималистичный селектор с флагами для выбора страны
    function createCountrySelector(countries, currentLang) {
        const container = document.createElement('div');
        container.className = 'country-filter-container';
        
        // Обертка для кнопки и выпадающего меню
        const buttonWrapper = document.createElement('div');
        buttonWrapper.className = 'country-filter-button-wrapper';
        
        // Кнопка с текущим выбранным флагом (или "Все")
        const button = document.createElement('button');
        button.className = 'country-filter-button';
        button.setAttribute('aria-label', 'Select country');
        
        // Контейнер для флага внутри кнопки
        const flagContainer = document.createElement('span');
        flagContainer.className = 'country-filter-button-flag';
        
        // Текст для отображения выбранной страны внутри кнопки
        const selectedText = document.createElement('span');
        selectedText.className = 'country-filter-selected-text';
        const allCountriesText = translations[currentLang]?.allCountries || 'All';
        
        // Иконка глобуса для "Все страны" (используем Unicode символ)
        const globeIcon = '🌐';
        flagContainer.textContent = globeIcon;
        selectedText.textContent = allCountriesText;
        
        button.appendChild(flagContainer);
        button.appendChild(selectedText);
        
        // Выпадающее меню
        const dropdown = document.createElement('div');
        dropdown.className = 'country-filter-dropdown';
        
        // Опция "Все страны"
        const allOption = createCountryOption('', globeIcon, allCountriesText, true);
        dropdown.appendChild(allOption);
        
        // Разделитель
        const divider = document.createElement('div');
        divider.className = 'country-filter-divider';
        dropdown.appendChild(divider);
        
        // Опции стран
        countries.forEach(country => {
            const flagCode = getCountryFlagCode(country);
            const flagUrl = getFlagUrl(flagCode);
            const option = createCountryOption(country, flagUrl, country, false);
            dropdown.appendChild(option);
        });
        
        buttonWrapper.appendChild(button);
        buttonWrapper.appendChild(dropdown);
        
        container.appendChild(buttonWrapper);
        
        // Переменная для хранения таймаута закрытия
        let hoverTimeout;
        let isClosing = false;
        
        // Обработчик клика на кнопку для переключения списка
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            clearTimeout(hoverTimeout);
            isClosing = false;
            dropdown.classList.toggle('show');
        });
        
        // Обработчик наведения на кнопку и меню (для удобства)
        buttonWrapper.addEventListener('mouseenter', function() {
            if (!isClosing) {
                clearTimeout(hoverTimeout);
                dropdown.classList.add('show');
            }
        });
        
        buttonWrapper.addEventListener('mouseleave', function() {
            // Закрываем список только если он открыт и не закрывается программно
            if (dropdown.classList.contains('show') && !isClosing) {
                hoverTimeout = setTimeout(function() {
                    dropdown.classList.remove('show');
                }, 100);
            }
        });
        
        // Закрываем список при клике вне области
        document.addEventListener('click', function(e) {
            if (!buttonWrapper.contains(e.target)) {
                clearTimeout(hoverTimeout);
                dropdown.classList.remove('show');
            }
        });
        
        return { container, button, dropdown, selectedText, flagContainer, hoverTimeout, setClosing: function(value) { isClosing = value; } };
    }
    
    // Создает опцию в выпадающем меню
    function createCountryOption(value, flagUrlOrIcon, label, isAll) {
        const option = document.createElement('div');
        option.className = 'country-filter-option';
        option.dataset.country = value;
        
        // Флаг или иконка
        const flagElement = document.createElement('div');
        flagElement.className = 'country-filter-flag';
        
        if (isAll || !flagUrlOrIcon || flagUrlOrIcon.startsWith('🌐')) {
            flagElement.textContent = '🌐';
        } else {
            flagElement.className += ' has-flag';
            flagElement.style.backgroundImage = `url('${flagUrlOrIcon}')`;
        }
        
        // Текст
        const labelElement = document.createElement('span');
        labelElement.className = 'country-filter-label';
        labelElement.textContent = label;
        
        option.appendChild(flagElement);
        option.appendChild(labelElement);
        
        return option;
    }
    
    // Скрывает колонку Country в таблице
    function hideCountryColumn(table, countryColumnIndex) {
        // Скрываем заголовок
        const thead = table.querySelector('thead');
        if (thead) {
            const headerRow = thead.querySelector('tr');
            if (headerRow) {
                const headerCell = headerRow.querySelectorAll('th, td')[countryColumnIndex];
                if (headerCell) {
                    headerCell.style.display = 'none';
                }
            }
        }
        
        // Скрываем ячейки в строках
        const tbody = table.querySelector('tbody');
        if (tbody) {
            const rows = tbody.querySelectorAll('tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td, th');
                if (cells[countryColumnIndex]) {
                    cells[countryColumnIndex].style.display = 'none';
                }
            });
        }
    }
    
    // Фильтрует строки таблицы по выбранной стране
    function filterTableRows(table, countryColumnIndex, selectedCountry) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        const rows = tbody.querySelectorAll('tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells[countryColumnIndex]) {
                const rowCountry = cells[countryColumnIndex].textContent.trim();
                if (selectedCountry === '' || rowCountry === selectedCountry) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }
    
    // Находит заголовок (h1-h6) перед таблицей
    function findPreviousHeader(table) {
        let element = table.previousElementSibling;
        while (element) {
            if (element.tagName && /^H[1-6]$/.test(element.tagName)) {
                return element;
            }
            element = element.previousElementSibling;
        }
        return null;
    }
    
    // Обрабатывает одну таблицу
    function processTable(table) {
        const countryColumnIndex = findCountryColumnIndex(table);
        if (countryColumnIndex === -1) {
            return; // Таблица не содержит колонку Country
        }
        
        // Получаем список стран
        const countries = getCountriesFromTable(table, countryColumnIndex);
        if (countries.length === 0) {
            return; // Нет стран для фильтрации
        }
        
        // Создаем селектор
        const currentLang = getCurrentLanguage();
        const { container, button, dropdown, selectedText, flagContainer, hoverTimeout, setClosing } = createCountrySelector(countries, currentLang);
        
        // Ищем заголовок перед таблицей
        const header = findPreviousHeader(table);
        if (header) {
            // Проверяем, находится ли заголовок уже внутри обертки
            let wrapper = header.closest('.table-header-with-filter');
            if (!wrapper) {
                // Если обертки нет, создаем ее
                wrapper = document.createElement('div');
                wrapper.className = 'table-header-with-filter';
                header.parentNode.insertBefore(wrapper, header);
                wrapper.appendChild(header);
            }
            // Добавляем селектор в обертку после заголовка
            wrapper.appendChild(container);
        } else {
            // Если заголовок не найден, добавляем селектор перед таблицей (как раньше)
            table.parentNode.insertBefore(container, table);
        }
        
        // Скрываем колонку Country
        hideCountryColumn(table, countryColumnIndex);
        
        // Обработчик выбора страны
        let selectedCountry = '';
        const allCountriesText = translations[currentLang]?.allCountries || 'All';
        dropdown.querySelectorAll('.country-filter-option').forEach(option => {
            option.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                
                selectedCountry = this.dataset.country || '';
                
                // Устанавливаем флаг закрытия и сразу закрываем список
                setClosing(true);
                clearTimeout(hoverTimeout);
                dropdown.classList.remove('show');
                
                // Сбрасываем флаг через небольшую задержку
                setTimeout(function() {
                    setClosing(false);
                }, 150);
                
                // Обновляем кнопку
                const flagCode = selectedCountry ? getCountryFlagCode(selectedCountry) : null;
                const flagUrl = getFlagUrl(flagCode);
                
                if (selectedCountry && flagUrl) {
                    flagContainer.style.backgroundImage = `url('${flagUrl}')`;
                    flagContainer.textContent = '';
                    flagContainer.classList.add('has-flag');
                    // Обновляем текст выбранной страны
                    selectedText.textContent = selectedCountry;
                } else {
                    flagContainer.style.backgroundImage = 'none';
                    flagContainer.textContent = '🌐';
                    flagContainer.classList.remove('has-flag');
                    // Обновляем текст на "Все"
                    selectedText.textContent = allCountriesText;
                }
                
                // Фильтруем таблицу
                filterTableRows(table, countryColumnIndex, selectedCountry);
            });
        });
        
        // Инициализируем фильтрацию (показываем все строки)
        filterTableRows(table, countryColumnIndex, '');
    }
    
    // Обрабатывает все таблицы на странице
    function processAllTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            // Проверяем, не обработана ли уже эта таблица
            if (!table.dataset.countryFilterProcessed) {
                table.dataset.countryFilterProcessed = 'true';
                processTable(table);
            }
        });
    }
    
    // Функция инициализации
    function init() {
        // Пробуем сразу
        processAllTables();
        
        // Если DOM еще не загружен, ждем
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', processAllTables);
        }
        
        // Также обрабатываем таблицы, которые могут появиться динамически
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.tagName === 'TABLE') {
                                if (!node.dataset.countryFilterProcessed) {
                                    node.dataset.countryFilterProcessed = 'true';
                                    processTable(node);
                                }
                            } else {
                                // Проверяем таблицы внутри добавленного элемента
                                const tables = node.querySelectorAll && node.querySelectorAll('table');
                                if (tables) {
                                    tables.forEach(table => {
                                        if (!table.dataset.countryFilterProcessed) {
                                            table.dataset.countryFilterProcessed = 'true';
                                            processTable(table);
                                        }
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
    }
    
    // Запускаем инициализацию
    init();
})();

