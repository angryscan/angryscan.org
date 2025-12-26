#!/usr/bin/env python3
"""
Скрипт для генерации HTML страниц из Jinja2 шаблонов
"""

import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import config


def setup_jinja_environment(templates_dir):
    """Настроить окружение Jinja2"""
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Добавить функции в контекст шаблонов
    env.globals.update({
        'site_config': config.SITE_CONFIG,
        'data': config.DATA,
        'languages': config.LANGUAGES,
        'pages': config.PAGES,
        'get_page_url': config.get_page_url
    })
    
    return env


def get_asset_path(lang):
    """Получить путь к ассетам в зависимости от языка"""
    if lang == 'en':
        return 'assets/'
    return '../assets/'


def generate_page(env, page_name, lang, output_dir):
    """Сгенерировать HTML страницу"""
    # Загрузить шаблон страницы
    template_path = f'pages/{page_name}.html'
    try:
        template = env.get_template(template_path)
    except Exception as e:
        print(f"Warning: Template {template_path} not found, skipping... ({e})")
        return
    
    # Получить переводы для языка
    translations = config.TRANSLATIONS.get(lang, config.TRANSLATIONS['en'])
    
    # Создать функцию перевода для текущего языка
    def t(key_path, default=None):
        return config.get_translation(lang, key_path, default)
    
    # Определить путь страницы
    page_path = config.get_page_url(page_name, lang)
    
    # Определить путь к ассетам
    asset_path = get_asset_path(lang)
    
    # Получить переводы для JavaScript (I18N) в виде JSON строки
    i18n_for_js = config.get_i18n_for_js()
    i18n_json = json.dumps(i18n_for_js, ensure_ascii=False)
    
    # Получить конфигурацию для JavaScript (CONFIG) в виде JSON строки
    config_for_js = config.get_config_for_js()
    config_json = json.dumps(config_for_js, ensure_ascii=False)
    
    # Получить мета-данные страницы
    page_meta = config.get_page_meta(page_name, lang)
    
    # Рендерить шаблон
    html = template.render(
        lang=lang,
        page_name=page_name,
        page_path=page_path,
        asset_path=asset_path,
        t=t,
        translations=translations,
        site_config=config.SITE_CONFIG,
        data=config.DATA,
        languages=config.LANGUAGES,
        get_page_url=lambda pname, l: config.get_page_url(pname, l),
        get_translation=lambda key_path, default=None: config.get_translation(lang, key_path, default),
        i18n_json=i18n_json,
        config_json=config_json,
        page_meta=page_meta,
        # Для use-cases - сначала проверяем translations, потом data как fallback
        use_cases_list=translations.get('sections', {}).get('use_cases', {}).get('cases', []) or config.DATA.get('use_cases', [])
    )
    
    # Определить выходной путь
    if lang == 'en':
        output_file = output_dir / f'{page_name}.html'
    else:
        lang_dir = output_dir / lang
        lang_dir.mkdir(exist_ok=True)
        output_file = lang_dir / f'{page_name}.html'
    
    # Сохранить HTML
    output_file.write_text(html, encoding='utf-8')
    try:
        rel_path = output_file.relative_to(Path.cwd())
        print(f"Generated: {rel_path}")
    except ValueError:
        # Если относительный путь не работает, используем абсолютный
        print(f"Generated: {output_file}")


def main():
    """Главная функция"""
    # Пути
    project_root = Path(__file__).parent
    templates_dir = project_root / 'templates'
    output_dir = project_root / 'src'
    
    # Проверить существование директорий
    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}")
        return
    
    output_dir.mkdir(exist_ok=True)
    
    # Настроить Jinja2
    env = setup_jinja_environment(str(templates_dir))
    
    # Список страниц для генерации
    pages = ['index', 'discovery', 'features', 'use-cases', 'download']
    
    # Список языков
    languages = list(config.LANGUAGES.keys())
    
    # Генерировать страницы для каждого языка
    for lang in languages:
        print(f"\nGenerating pages for language: {lang}")
        for page_name in pages:
            try:
                generate_page(env, page_name, lang, output_dir)
            except Exception as e:
                print(f"Error generating {page_name} for {lang}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\nHTML generation complete!")


if __name__ == '__main__':
    main()

