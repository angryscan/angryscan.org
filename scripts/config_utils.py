#!/usr/bin/env python3
"""Shared helpers for reading MkDocs configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
MKDOCS_PATH = ROOT / "mkdocs.yml"


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
