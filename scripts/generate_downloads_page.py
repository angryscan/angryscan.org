#!/usr/bin/env python3
"""Generate the download page from the latest angrydata-app GitHub release."""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
OUTPUT_DIR = DOCS_ROOT / "download"
OUTPUT_PATH = OUTPUT_DIR / "index.md"
CONFIG_PATH = ROOT / "scripts" / "download_config.yaml"


@dataclass(frozen=True)
class AssetRule:
    """Configuration describing how to surface a release asset on the download page."""
    os_name: str
    display_name: str
    description: str
    badge_url: str
    alt_text: str
    suffixes: Tuple[str, ...]
    preferred_substrings: Tuple[str, ...] = ()

    def matches(self, asset_name: str) -> bool:
        return any(asset_name.endswith(suffix) for suffix in self.suffixes)


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_config():
    """Get loaded configuration."""
    if not hasattr(get_config, '_config'):
        get_config._config = load_config()
    return get_config._config


def get_releases_api_url() -> str:
    """Get GitHub releases API URL from config."""
    config = get_config()
    repo = config['repository']
    return f"https://api.github.com/repos/{repo['owner']}/{repo['name']}/releases"


def get_releases_html_url() -> str:
    """Get GitHub releases HTML URL from config."""
    config = get_config()
    repo = config['repository']
    return f"https://github.com/{repo['owner']}/{repo['name']}/releases"


def get_front_matter() -> str:
    """Get front matter for the page."""
    config = get_config()
    page = config['page']
    return f"""---
title: {page['title']}
description: {page['description']}
hide:
  - navigation
  - toc
---

# {page['title']}
"""


def get_asset_rules() -> List[AssetRule]:
    """Get asset rules from configuration."""
    config = get_config()
    rules = []
    for rule_data in config['asset_rules']:
        rule = AssetRule(
            os_name=rule_data['os_name'],
            display_name=rule_data['display_name'],
            description=rule_data['description'],
            badge_url=rule_data['badge_url'],
            alt_text=rule_data['alt_text'],
            suffixes=tuple(rule_data['suffixes']),
            preferred_substrings=tuple(rule_data.get('preferred_substrings', []))
        )
        rules.append(rule)
    return rules


def get_os_config() -> dict:
    """Get operating systems configuration."""
    return get_config()['operating_systems']


def get_os_order() -> List[str]:
    """Get operating systems order."""
    return get_config()['os_order']


def fetch_latest_release() -> dict:
    """Fetch the latest release from GitHub API."""
    response = requests.get(
        get_releases_api_url(),
        params={"per_page": 1},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()
    releases = response.json()
    return releases[0] if releases else {}


def human_size(num_bytes: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024.0 or unit == "GB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} GB"


def select_preferred_asset(
    current_asset: dict, candidate_asset: dict, preferred_substrings: tuple[str, ...]
) -> dict:
    """Choose the most appropriate asset when multiple match the same rule."""
    if not current_asset:
        return candidate_asset
    if not preferred_substrings:
        return current_asset

    def score(asset: dict) -> tuple[int, int]:
        name = asset.get("name", "").lower()
        for idx, token in enumerate(preferred_substrings):
            if token and token.lower() in name:
                return idx, -asset.get("size", 0)
        return len(preferred_substrings), -asset.get("size", 0)

    return candidate_asset if score(candidate_asset) < score(current_asset) else current_asset


def build_os_downloads(assets: list[dict]) -> Dict[str, list[dict]]:
    """
    Group release assets by operating system.
    
    Returns a mapping of OS name to list of matching assets in the order defined in YAML.
    """
    asset_rules = get_asset_rules()
    os_order = get_os_order()
    
    selected: Dict[AssetRule, dict] = {}
    
    for asset in assets:
        name = asset.get("name", "")
        matched_rule = next((rule for rule in asset_rules if rule.matches(name)), None)
        if matched_rule is None:
            continue  # Skip assets that don't match any rule

        existing_asset = selected.get(matched_rule)
        preferred_asset = select_preferred_asset(
            existing_asset, asset, matched_rule.preferred_substrings
        )
        selected[matched_rule] = preferred_asset

    # Group selected assets by OS in the order defined in YAML
    os_assets: Dict[str, list[dict]] = {os_name: [] for os_name in os_order}
    
    # Process rules in the order they appear in YAML configuration
    for rule in asset_rules:
        if rule in selected:
            os_assets[rule.os_name].append({
                "asset": selected[rule],
                "rule": rule
            })
    
    return os_assets


def render_download_card(os_name: str, assets: list[dict]) -> str:
    """Render a modern download card for an operating system."""
    os_config = get_os_config()
    os_info = os_config[os_name]
    
    if not assets:
        # No assets available for this OS
        return f"""
<div class="download-card {os_info['icon']}">
    <div class="os-header">
        <h3>{os_info['label']}</h3>
    </div>
    <div class="download-content">
        <p class="no-downloads">Temporarily unavailable</p>
        {os_info['placeholder']}
    </div>
</div>"""

    # Build download buttons for available assets
    buttons = []
    for asset_info in assets:
        asset = asset_info["asset"]
        rule = asset_info["rule"]
        
        url = asset.get("browser_download_url", asset.get("html_url", "#"))
        size = human_size(asset.get("size", 0))
        
        button_html = f'''
        <a href="{url}" class="download-button">
            <div class="download-badge">
                <img src="{rule.badge_url}" alt="{rule.alt_text}">
            </div>
            <div class="download-info">
                <span class="download-name">{rule.display_name}</span>
                <span class="download-size">({size})</span>
            </div>
        </a>'''
        buttons.append(button_html)
    
    buttons_html = "\n        ".join(buttons)
    
    return f"""
<div class="download-card {os_info['icon']}">
    <div class="os-header">
        <h3>{os_info['label']}</h3>
    </div>
    <div class="download-content">
        {buttons_html}
    </div>
</div>"""


def render_css_styles() -> str:
    """Generate modern CSS styles for the download page."""
    return """
<style>
.download-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.download-card {
    border: 2px solid #e1e5e9;
    border-radius: 16px;
    padding: 2rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.download-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    border-color: #0078d6;
}

.download-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0078d6, #00bcf2);
}

.download-card.windows::before {
    background: linear-gradient(90deg, #0078d6, #00bcf2);
}

.download-card.linux::before {
    background: linear-gradient(90deg, #a81d33, #ff6b35);
}

.download-card.apple::before {
    background: linear-gradient(90deg, #000000, #666666);
}

.os-header h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
}

.download-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.download-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    border: 1px solid #e1e5e9;
    border-radius: 12px;
    background: #ffffff;
    transition: all 0.2s ease;
    text-decoration: none;
    color: inherit;
    cursor: pointer;
}

.download-button:hover {
    border-color: #0078d6;
    background: #f8f9ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 120, 214, 0.15);
}

.download-badge {
    display: block;
}

.download-badge img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}

.download-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}

.download-name {
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.9rem;
}

.download-size {
    font-size: 0.8rem;
    color: #6c757d;
}

.no-downloads {
    text-align: center;
    color: #6c757d;
    font-style: italic;
    margin: 1rem 0;
}

.release-info {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    margin: 2rem 0;
    text-align: center;
}

.release-info h2 {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
    font-weight: 700;
}

.release-date {
    opacity: 0.9;
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .download-container {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .download-card {
        padding: 1.5rem;
    }
    
    .release-info h2 {
        font-size: 1.5rem;
    }
}
</style>"""


def format_release(release: dict) -> str:
    """Format a single release with modern styling."""
    name = release.get("name") or release.get("tag_name", "Unnamed release")
    published_at = release.get("published_at")
    
    published_str = ""
    if published_at:
        published_str = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00")).strftime(
            "%d.%m.%Y"
        )

    # Build download cards for each OS
    assets: list[dict] = release.get("assets") or []
    os_assets = build_os_downloads(assets)
    os_order = get_os_order()
    
    download_cards = []
    for os_name in os_order:
        assets_for_os = os_assets.get(os_name, [])
        card_html = render_download_card(os_name, assets_for_os)
        download_cards.append(card_html)
    
    cards_html = "\n".join(download_cards)
    
    # Build release info section
    release_info = ""
    if published_str:
        release_info = f"""
<div class="release-info">
    <h2>{name}</h2>
    <p class="release-date">Published on {published_str}</p>
</div>"""
    
    return f"""
{release_info}

<div class="download-container">
{cards_html}
</div>

<div style="text-align: center; margin-top: 2rem;">
    <p><a href="{release.get('html_url')}" target="_blank" style="color: #0078d6; text-decoration: none; font-weight: 500;">
        📋 View full release notes
    </a></p>
</div>"""


def render_content(release: dict) -> str:
    """Render the complete page content."""
    sections = [get_front_matter().rstrip()]
    
    if not release:
        sections.append("""
<div class="no-releases">
    <h2>Releases temporarily unavailable</h2>
    <p>Please check the <a href="{}" target="_blank">GitHub releases page</a> for updates.</p>
</div>""".format(get_releases_html_url()))
    else:
        sections.append(format_release(release))
    
    # Add CSS styles
    sections.append(render_css_styles())
    
    return "\n\n".join(sections).strip() + "\n"


def main() -> None:
    """Main function to generate the download page."""
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        release = fetch_latest_release()
    except Exception as exc:  # pylint: disable=broad-except
        fallback = (
            get_front_matter()
            + "\n"
            + f"""
<div class="error-message" style="padding: 2rem; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; color: #721c24;">
    <h3>Error loading release information</h3>
    <p>Failed to load release information at this time.</p>
    <p><strong>Error:</strong> <code>{exc}</code></p>
    <p><a href="{get_releases_html_url()}" target="_blank" style="color: #721c24;">Visit the GitHub releases page directly</a></p>
</div>"""
        )
        OUTPUT_PATH.write_text(fallback.strip() + "\n", encoding="utf-8")
        return

    OUTPUT_PATH.write_text(render_content(release), encoding="utf-8")


if __name__ == "__main__":
    main()