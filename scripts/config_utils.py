#!/usr/bin/env python3
"""Shared helpers for reading MkDocs configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
MKDOCS_PATH = ROOT / "mkdocs.yml"
SYNC_CONFIG_PATH = Path(__file__).parent / "sync_config.yaml"


def load_mkdocs_config() -> Dict[str, Any]:
    with MKDOCS_PATH.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def get_i18n_languages(config: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    config = config or load_mkdocs_config()
    plugins = config.get("plugins", [])
    for plugin in plugins:
        if isinstance(plugin, dict) and "i18n" in plugin:
            languages = plugin["i18n"].get("languages", [])
            normalized: List[Dict[str, Any]] = []
            for entry in languages:
                if isinstance(entry, dict):
                    normalized.append(
                        {
                            "locale": entry.get("locale"),
                            "name": entry.get("name", entry.get("locale")),
                            "default": bool(entry.get("default")),
                        }
                    )
                else:
                    normalized.append({"locale": entry, "name": entry, "default": False})
            return [lang for lang in normalized if lang.get("locale")]
    return []


def get_translation_locales(config: Dict[str, Any] | None = None) -> List[str]:
    locales: List[str] = []
    for lang in get_i18n_languages(config=config):
        if not lang.get("default"):
            locales.append(str(lang["locale"]))
    return locales


def get_all_locales(config: Dict[str, Any] | None = None) -> List[str]:
    return [str(lang["locale"]) for lang in get_i18n_languages(config=config)]


def generate_alternate_menu_items(config: Dict[str, Any] | None = None) -> List[Dict[str, str]]:
    """Generate alternate menu items for all languages."""
    languages = get_i18n_languages(config)
    alternate_items = []
    
    for lang in languages:
        locale = lang["locale"]
        name = lang["name"]
        
        # Create link path
        if lang.get("default"):
            link = "/"
        else:
            link = f"/{locale}/"
        
        alternate_items.append({
            "name": name,
            "lang": locale,
            "link": link
        })
    
    return alternate_items


def update_mkdocs_alternate_menu(config_path: Path | None = None) -> None:
    """Update mkdocs.yml with auto-generated alternate menu items."""
    if config_path is None:
        config_path = MKDOCS_PATH
    
    # Load current config
    config = load_mkdocs_config()
    
    # Generate new alternate menu items
    alternate_items = generate_alternate_menu_items(config)
    
    # Update the config
    if "extra" not in config:
        config["extra"] = {}
    
    config["extra"]["alternate"] = alternate_items
    
    # Write back to file
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_js_language_mappings(config: Dict[str, Any] | None = None) -> Dict[str, Dict[str, str]]:
    """Generate JavaScript language mappings for custom-menu.js."""
    languages = get_i18n_languages(config)
    js_mappings = {}
    
    # Language name mappings for JavaScript
    language_names = {
        'en': 'English',
        'ru': 'Русский', 
        'es': 'Español',
        'de': 'Deutsch',
        'fr': 'Français'
    }
    
    # Menu text translations
    menu_translations = {
        'en': {'main': 'Main', 'library': 'Angry Data Core', 'download': 'Download'},
        'ru': {'main': 'Главная', 'library': 'Angry Data Core', 'download': 'Скачать'},
        'es': {'main': 'Principal', 'library': 'Angry Data Core', 'download': 'Descargas'},
        'de': {'main': 'Hauptseite', 'library': 'Angry Data Core', 'download': 'Downloads'},
        'fr': {'main': 'Principal', 'library': 'Angry Data Core', 'download': 'Téléchargements'}
    }
    
    for lang in languages:
        locale = lang["locale"]
        if locale in menu_translations:
            js_mappings[locale] = menu_translations[locale]
    
    return js_mappings


def update_menu_translations_json(config: Dict[str, Any] | None = None, json_path: Path | None = None) -> None:
    """Update menu-translations.json with auto-generated language mappings."""
    if json_path is None:
        json_path = ROOT / "docs" / "assets" / "menu-translations.json"
    
    # Generate language mappings
    js_mappings = generate_js_language_mappings(config)
    
    # Write JSON file
    import json
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(js_mappings, f, ensure_ascii=False, indent=2)


def load_sync_config() -> Dict[str, Any]:
    """Load sync configuration from YAML file."""
    if not SYNC_CONFIG_PATH.exists():
        return {}
    
    with SYNC_CONFIG_PATH.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def get_remove_headers() -> List[str]:
    """Get list of headers to remove from documentation."""
    config = load_sync_config()
    sync_config = config.get("sync", {})
    return sync_config.get("remove_headers", ["## Direct Download"])


def should_skip_until_first_header() -> bool:
    """Check if content should be skipped until first header."""
    config = load_sync_config()
    sync_config = config.get("sync", {})
    return sync_config.get("skip_until_first_header", True)


def should_process_translation_links() -> bool:
    """Check if translation links should be processed."""
    config = load_sync_config()
    sync_config = config.get("sync", {})
    return sync_config.get("process_translation_links", True)