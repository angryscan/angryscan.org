// Language selector with flag display
// Version: 1.1 - Replace language button with current language flag
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
    
    // Маппинг языков на флаги (используем более высокое разрешение для лучшего качества)
    const languageFlags = {
        'en': {
            flag: 'https://flagcdn.com/w40/us.png',
            name: 'English'
        },
        'ru': {
            flag: 'https://flagcdn.com/w40/ru.png',
            name: 'Русский'
        },
        'es': {
            flag: 'https://flagcdn.com/w40/es.png',
            name: 'Español'
        },
        'de': {
            flag: 'https://flagcdn.com/w40/de.png',
            name: 'Deutsch'
        },
        'fr': {
            flag: 'https://flagcdn.com/w40/fr.png',
            name: 'Français'
        }
    };
    
    let isReplaced = false;
    
    // Функция для замены кнопки языка на флаг
    function replaceLanguageButton() {
        if (isReplaced) return;
        
        const languageButton = document.querySelector('.md-header__option .md-select button');
        if (!languageButton) {
            console.log('Language button not found, trying again...');
            return;
        }
        
        console.log('Found language button, replacing with flag...');
        
        const currentLang = getCurrentLanguage();
        const currentLangData = languageFlags[currentLang];
        
        if (!currentLangData) {
            console.warn('Language data not found for:', currentLang);
            return;
        }
        
        // Создаем новый элемент с флагом
        const flagElement = document.createElement('div');
        flagElement.className = 'md-header__button md-icon language-flag-button';
        flagElement.setAttribute('aria-label', `Select language - Current: ${currentLangData.name}`);
        flagElement.setAttribute('title', `Current language: ${currentLangData.name}`);
        
        // Применяем стили через CSS классы
        flagElement.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 4px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-image: url('${currentLangData.flag}');
            border: none;
            box-shadow: none;
            transition: all 0.2s ease;
            cursor: pointer;
        `;
        
        // Добавляем hover эффект
        flagElement.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.filter = 'brightness(1.1)';
        });
        
        flagElement.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.filter = 'brightness(1)';
        });
        
        // Сохраняем функциональность выпадающего меню
        const selectInner = languageButton.parentNode.querySelector('.md-select__inner');
        if (selectInner) {
            // Показываем/скрываем меню при клике на флаг
            flagElement.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                const isVisible = selectInner.style.display !== 'none' && selectInner.style.display !== '';
                if (isVisible) {
                    selectInner.style.display = 'none';
                } else {
                    selectInner.style.display = 'block';
                }
            });
            
            // Скрываем меню при клике вне его
            document.addEventListener('click', function(e) {
                if (!languageButton.parentNode.contains(e.target)) {
                    selectInner.style.display = 'none';
                }
            });
        }
        
        // Заменяем кнопку
        languageButton.parentNode.replaceChild(flagElement, languageButton);
        isReplaced = true;
        
        console.log('Language button replaced with flag for:', currentLang);
    }
    
    // Функция инициализации
    function init() {
        // Пробуем сразу
        replaceLanguageButton();
        
        // Если не получилось, ждем загрузки DOM
        if (!isReplaced) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', replaceLanguageButton);
            } else {
                // DOM уже загружен
                setTimeout(replaceLanguageButton, 100);
            }
        }
    }
    
    // Запускаем инициализацию
    init();
    
    // Также пробуем при изменении DOM (на случай динамической загрузки)
    const observer = new MutationObserver(function(mutations) {
        if (isReplaced) return;
        
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                setTimeout(replaceLanguageButton, 50);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Очищаем observer через 10 секунд
    setTimeout(function() {
        observer.disconnect();
    }, 10000);
})();
