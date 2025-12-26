"""
Единый конфиг со всеми данными и переводами для сайта Angry Data Scanner
Загружается из config.json
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

# Путь к JSON конфигу
CONFIG_FILE = Path(__file__).parent / 'config.json'

# Загрузить конфиг из JSON
def _load_config() -> Dict[str, Any]:
    """Загрузить конфиг из JSON файла"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Fallback на пустой конфиг
        return {
            'site_config': {},
            'data': {},
            'translations': {},
            'languages': {},
            'pages': {}
        }

# Загрузить данные
_config_data = _load_config()

# Экспортировать данные как константы
SITE_CONFIG = _config_data.get('site_config', {})
DATA = _config_data.get('data', {})
TRANSLATIONS = _config_data.get('translations', {})
LANGUAGES = _config_data.get('languages', {})
PAGES = _config_data.get('pages', {})


def _camel_to_snake(name: str) -> str:
    """Конвертировать camelCase в snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def _snake_to_camel(name: str) -> str:
    """Конвертировать snake_case в camelCase"""
    components = name.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

def get_translation(lang: str, key_path: str, default: Optional[str] = None) -> Any:
    """Получить перевод по пути ключа (например, 'nav.home' -> 'nav': {'home': ...})
    Поддерживает как snake_case, так и camelCase ключи в JSON"""
    keys = key_path.split('.')
    translations = TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {}))
    
    value = translations
    for key in keys:
        if isinstance(value, dict):
            # Сначала пробуем ключ как есть
            if key in value:
                value = value[key]
            else:
                # Если не нашли, пробуем конвертировать snake_case -> camelCase
                camel_key = _snake_to_camel(key)
                if camel_key in value:
                    value = value[camel_key]
                else:
                    # Или наоборот camelCase -> snake_case
                    snake_key = _camel_to_snake(key)
                    if snake_key in value:
                        value = value[snake_key]
                    else:
                        return default if default is not None else key_path
        else:
            return default if default is not None else key_path
    return value


def get_page_url(page_name: str, lang: str) -> str:
    """Получить URL страницы для языка"""
    if page_name in PAGES and lang in PAGES[page_name]:
        return PAGES[page_name][lang]['path']
    return '/'


def get_page_meta(page_name: str, lang: str) -> Dict[str, str]:
    """Получить мета-данные страницы (title, description, keywords)"""
    # Для всех страниц берем из pages[page_name][lang]
    page_config = PAGES.get(page_name, {})
    lang_config = page_config.get(lang, page_config.get('en', {}))
    
    # Если есть явные title, description, keywords - используем их
    if 'title' in lang_config or 'description' in lang_config or 'keywords' in lang_config:
        return {
            'title': lang_config.get('title', get_translation(lang, lang_config.get('title_key', 'site.title'))),
            'description': lang_config.get('description', get_translation(lang, 'site.description')),
            'keywords': lang_config.get('keywords', 'data scanner, PII discovery, sensitive data, PCI DSS, data protection, free data scanner')
        }
    
    # Fallback - используем title_key и site.description
    title_key = lang_config.get('title_key', 'site.title')
    return {
        'title': get_translation(lang, title_key),
        'description': get_translation(lang, 'site.description'),
        'keywords': 'data scanner, PII discovery, sensitive data, PCI DSS, data protection, free data scanner'
    }


def _convert_keys_to_camel_case(obj: Any) -> Any:
    """
    Рекурсивно конвертирует все ключи словаря из snake_case в camelCase
    """
    if isinstance(obj, dict):
        converted = {}
        for key, value in obj.items():
            # Конвертировать ключ из snake_case в camelCase
            camel_key = _snake_to_camel(key)
            # Рекурсивно конвертировать значение
            converted[camel_key] = _convert_keys_to_camel_case(value)
        return converted
    elif isinstance(obj, list):
        # Для списков рекурсивно конвертировать каждый элемент
        return [_convert_keys_to_camel_case(item) for item in obj]
    else:
        # Для примитивных типов возвращать как есть
        return obj


def get_i18n_for_js() -> Dict[str, Any]:
    """
    Получить переводы в формате для JavaScript (window.I18N)
    Конвертирует ключи из snake_case (config.json) в camelCase (как в старом i18n.js)
    для совместимости с существующим JavaScript кодом
    """
    import copy
    result = {}
    
    # Пройтись по всем языкам и конвертировать ключи
    for lang_code, translations in TRANSLATIONS.items():
        result[lang_code] = _convert_keys_to_camel_case(copy.deepcopy(translations))
    
    return result


def get_config_for_js() -> Dict[str, Any]:
    """
    Получить конфигурацию в формате для JavaScript (window.CONFIG)
    Конвертирует данные из config.json (snake_case) в camelCase для совместимости
    Рекурсивно конвертирует все ключи, включая вложенные объекты в массивах
    """
    import copy
    
    # Копируем данные из config.json
    config_data = copy.deepcopy(DATA)
    
    # Рекурсивно конвертируем все ключи из snake_case в camelCase
    converted_data = _convert_keys_to_camel_case(config_data)
    
    # Создаем результат с правильными ключами верхнего уровня
    result = {}
    
    # Маппинг ключей верхнего уровня (они уже конвертированы, но нужно убедиться в правильном именовании)
    key_mapping = {
        'personalDataNumbers': 'personalDataNumbers',
        'personalDataText': 'personalDataText',
        'pciDss': 'pciDss',
        'bankingSecrecy': 'bankingSecrecy',
        'itAssets': 'itAssets',
        'customSignatures': 'customSignatures',
        'fileTypes': 'fileTypes',
        'dataSources': 'dataSources',
        'useCases': 'useCases',
        'downloads': 'downloads',
        'features': 'features',
        'systemRequirements': 'systemRequirements',
        'crypto': 'crypto'
    }
    
    # Переносим конвертированные данные
    for old_key, new_key in key_mapping.items():
        if old_key in converted_data:
            result[new_key] = converted_data[old_key]
    
    # Добавляем site metadata из site_config
    result['site'] = {
        'title': 'Angry Data Scanner - Sensitive Data Discovery Tool',
        'description': 'Free open source sensitive data discovery tool',
        'githubUrl': SITE_CONFIG.get('github_url', ''),
        'email': SITE_CONFIG.get('email', '')
    }
    
    return result
