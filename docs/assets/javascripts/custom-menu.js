// Добавление пунктов навигации в основную навигацию
document.addEventListener('DOMContentLoaded', function() {
    // Функция для добавления пунктов
    function addNavigationItems() {
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
        
        // Тексты для разных языков
        const texts = {
            en: {
                main: 'Main',
                library: 'Angry Data Core',
                download: 'Download'
            },
            ru: {
                main: 'Главная',
                library: 'Angry Data Core',
                download: 'Загрузки'
            },
            es: {
                main: 'Principal',
                library: 'Angry Data Core',
                download: 'Descargas'
            },
            de: {
                main: 'Hauptseite',
                library: 'Angry Data Core',
                download: 'Downloads'
            }
        };
        
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
