#!/usr/bin/env python3
"""Shared helpers for reading MkDocs configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
MKDOCS_PATH = ROOT / "mkdocs.yml"
SYNC_CONFIG_PATH = Path(__file__).parent / "sync_config.yaml"
METADATA_CONFIG_PATH = Path(__file__).parent / "metadata_config.yaml"


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


def load_metadata_config() -> Dict[str, Any]:
    """Load metadata configuration from YAML file."""
    if not METADATA_CONFIG_PATH.exists():
        return {}
    
    with METADATA_CONFIG_PATH.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def is_metadata_enabled() -> bool:
    """Check if metadata processing is enabled."""
    config = load_metadata_config()
    metadata_config = config.get("metadata", {})
    return metadata_config.get("enabled", True)


def get_file_metadata(file_path: str) -> Dict[str, str]:
    """Get custom metadata for a specific file."""
    if not is_metadata_enabled():
        return {}
    
    config = load_metadata_config()
    metadata_config = config.get("metadata", {})
    
    # Check for exact file match
    files_config = metadata_config.get("files", {})
    if file_path in files_config:
        return files_config[file_path]
    
    # Check for pattern matches
    patterns_config = metadata_config.get("patterns", {})
    for pattern, pattern_config in patterns_config.items():
        if _match_pattern(file_path, pattern):
            return pattern_config
    
    # Return defaults if no specific configuration found
    defaults = metadata_config.get("defaults", {})
    return defaults


def _match_pattern(file_path: str, pattern: str) -> bool:
    """Check if file path matches a pattern (supports wildcards)."""
    import fnmatch
    return fnmatch.fnmatch(file_path, pattern)


def apply_metadata_to_content(content: str, file_path: str) -> str:
    """Apply custom metadata to markdown content."""
    metadata = get_file_metadata(file_path)
    if not metadata:
        return content
    
    # Check if front matter already exists
    if content.startswith("---"):
        # Extract existing front matter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            content_after = parts[2].lstrip("\n")
            
            # Parse existing front matter
            existing_metadata = {}
            lines = front_matter.split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if ":" in line and not line.startswith("  "):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Check if this is a multi-line value (like hide: with list)
                    if i + 1 < len(lines) and lines[i + 1].startswith("  "):
                        # Collect all indented lines
                        multi_line_value = [value] if value else []
                        i += 1
                        while i < len(lines) and lines[i].startswith("  "):
                            multi_line_value.append(lines[i].strip())
                            i += 1
                        existing_metadata[key] = "\n".join(multi_line_value)
                        i -= 1  # Adjust for the loop increment
                    else:
                        existing_metadata[key] = value
                i += 1
            
            # Apply new metadata
            for key, value in metadata.items():
                if key == "title":
                    existing_metadata["title"] = value
                elif key == "description":
                    existing_metadata["description"] = value
                elif key == "title_prefix":
                    # Add prefix to existing title or use as new title
                    if "title" in existing_metadata:
                        existing_metadata["title"] = value + existing_metadata["title"]
                    else:
                        existing_metadata["title"] = value
            
            # Preserve existing hide values if they exist - don't override them
            # This prevents duplication of hide entries
            
            # Rebuild front matter
            new_front_matter = []
            for key, value in existing_metadata.items():
                if "\n" in value:
                    # Multi-line value (like hide: with list)
                    new_front_matter.append(f"{key}:")
                    for line in value.split("\n"):
                        if line.strip():
                            new_front_matter.append(f"  {line}")
                else:
                    # Single-line value
                    new_front_matter.append(f"{key}: {value}")
            
            return f"---\n" + "\n".join(new_front_matter) + f"\n---\n{content_after}"
    else:
        # Create new front matter
        front_matter_lines = ["---"]
        
        # Apply metadata
        for key, value in metadata.items():
            if key == "title":
                front_matter_lines.append(f"title: {value}")
            elif key == "description":
                front_matter_lines.append(f"description: {value}")
            elif key == "title_prefix":
                front_matter_lines.append(f"title: {value}")
        
        front_matter_lines.append("---")
        front_matter_lines.append("")
        
        return "\n".join(front_matter_lines) + "\n" + content