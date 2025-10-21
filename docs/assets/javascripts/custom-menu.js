// Добавление пунктов навигации в основную навигацию
document.addEventListener('DOMContentLoaded', function() {
    let translations = null;
    
    // Загружаем переводы из внешнего файла
    async function loadTranslations() {
        if (translations) return translations;
        
        try {
            const response = await fetch('/assets/data/menu-translations.json');
            translations = await response.json();
            return translations;
        } catch (error) {
            console.warn('Failed to load menu translations, using fallback:', error);
            // Fallback переводы
            translations = {
                en: {
                    main: 'Main',
                    library: 'Angry Data Core',
                    download: 'Download'
                }
            };
            return translations;
        }
    }
    
    // Функция для добавления пунктов
    async function addNavigationItems() {
        // Ищем основную навигацию
        const primaryNav = document.querySelector('.md-nav--primary');
        if (!primaryNav) {
            return;
        }
        
        // Проверяем, не добавлены ли уже наши пункты
        const hasCustomItems = primaryNav.querySelector('a[href="/angrydata-app/"]');
        if (hasCustomItems) {
            return;
        }
        
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
                <a href="/angrydata-app/downloads/" class="md-nav__link">
                    <span class="md-nav__text">${t.download}</span>
                </a>
            </li>
        `;
        
        // Добавляем пункты непосредственно в nav элемент
        primaryNav.insertAdjacentHTML('beforeend', newItems);
    }
    
    // Пробуем несколько раз с разными задержками
    setTimeout(addNavigationItems, 500);
    setTimeout(addNavigationItems, 1000);
    setTimeout(addNavigationItems, 2000);
    
    // Также пробуем при изменении DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setTimeout(addNavigationItems, 100);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});