"""MkDocs event hooks used by the AngryScan documentation build."""

from __future__ import annotations

from mkdocs.structure.nav import Navigation


def on_nav(nav: Navigation, config, files):
    """Ensure a homepage exists so downstream plugins (i18n) do not warn."""
    if nav.homepage is None:
        for page in nav.pages:
            nav.homepage = page
            break
    return nav
