// Добавление пунктов навигации в основную навигацию
// Version: 2.4 - Optimized translation loading without hiding

// Предзагружаем переводы сразу при загрузке скрипта
const preloadTranslations = fetch('/assets/menu-translations.json')
    .then(response => response.json())
    .catch(error => {
        console.warn('Failed to load menu translations, using fallback:', error);
        return {
            en: {
                main: 'Main',
                library: 'Angry Data Core',
                download: 'Download'
            }
        };
    });

document.addEventListener('DOMContentLoaded', function() {
    let translations = null;
    let tabsTranslated = false;
    let navigationAdded = false;
    
    // Загружаем переводы из внешнего файла
    async function loadTranslations() {
        if (translations) return translations;
        
        translations = await preloadTranslations;
        return translations;
    }
    
    // Функция для перевода навигационных табов
    async function translateNavigationTabs() {
        // Проверяем, не переведены ли уже табы
        if (tabsTranslated) {
            return;
        }
        tabsTranslated = true;
        
        // Ищем навигационные табы
        const tabsList = document.querySelector('.md-tabs__list');
        if (!tabsList) {
            return;
        }
        
        // Определяем текущий язык
        const path = window.location.pathname;
        let lang = 'en';
        
        if (path.startsWith('/ru/')) lang = 'ru';
        else if (path.startsWith('/es/')) lang = 'es';
        else if (path.startsWith('/de/')) lang = 'de';
        else if (path.startsWith('/fr/')) lang = 'fr';
        
        // Загружаем переводы
        const texts = await loadTranslations();
        const t = texts[lang] || texts.en;
        
        // Переводим табы
        const tabLinks = tabsList.querySelectorAll('.md-tabs__link');
        
        tabLinks.forEach((link) => {
            const href = link.href;
            const currentText = link.textContent.trim();
            
            // Переводим по href в первую очередь, затем по тексту
            if (href && href.includes('download')) {
                link.textContent = t.download;
            } else if (href && href.includes('angrydata-core')) {
                link.textContent = t.library;
            } else if (href && href.includes('angrydata-app') && !href.includes('download')) {
                link.textContent = t.main;
            }
        });
        
        // Отмечаем, что табы переведены
        tabsTranslated = true;
        
        // Добавляем класс для плавного появления
        tabsList.classList.add('loaded');
    }
    
    // Функция для добавления пунктов
    async function addNavigationItems() {
        // Проверяем, не добавлена ли уже навигация
        if (navigationAdded) {
            return;
        }
        
        // Ищем основную навигацию
        const primaryNav = document.querySelector('.md-nav--primary');
        if (!primaryNav) {
            return;
        }
        
        // Проверяем, не добавлены ли уже наши пункты
        const hasCustomItems = primaryNav.querySelector('a[href="/angrydata-app/"]');
        if (hasCustomItems) {
            navigationAdded = true;
            return;
        }
        navigationAdded = true;
        
        // Определяем текущий язык
        const currentLang = document.documentElement.lang || 'en';
        const path = window.location.pathname;
        let lang = 'en';
        
        if (path.startsWith('/ru/')) lang = 'ru';
        else if (path.startsWith('/es/')) lang = 'es';
        else if (path.startsWith('/de/')) lang = 'de';
        else if (path.startsWith('/fr/')) lang = 'fr';
        
        // Загружаем переводы
        const texts = await loadTranslations();
        
        // Используем переводы с fallback на английский
        const t = texts[lang] || texts.en;
        
        // Создаем новые пункты навигации
        const newItems = `
            <li class="md-nav__item">
                <a href="/angrydata-app/" class="md-nav__link">
                    <span class="md-nav__text">${t.main}</span>
                </a>
            </li>
            <li class="md-nav__item">
                <a href="/angrydata-core/" class="md-nav__link">
                    <span class="md-nav__text">${t.library}</span>
                </a>
            </li>
            <li class="md-nav__item">
                <a href="/download/" class="md-nav__link">
                    <span class="md-nav__text">${t.download}</span>
                </a>
            </li>
        `;
        
        // Добавляем пункты непосредственно в nav элемент
        primaryNav.insertAdjacentHTML('beforeend', newItems);
        
        // Добавляем класс loaded для плавного появления новых пунктов
        const newNavItems = primaryNav.querySelectorAll('.md-nav__item:not([data-original])');
        newNavItems.forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('loaded');
            }, index * 100); // Задержка для каждого пункта
        });
        
        // Отмечаем, что навигация добавлена
        navigationAdded = true;
    }
    
    // Выполняем сразу при загрузке
    addNavigationItems();
    translateNavigationTabs();
    
    // Также пробуем при изменении DOM (только если еще не выполнено)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Переводим табы только если еще не переведены
                if (!tabsTranslated) {
                    translateNavigationTabs();
                }
                // Добавляем навигацию только если еще не добавлена
                if (!navigationAdded) {
                    addNavigationItems();
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});