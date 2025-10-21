#!/usr/bin/env python3
"""Generate the download page from the latest angrydata-app GitHub release."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
OUTPUT_DIR = DOCS_ROOT / "angrydata-app" / "download"
OUTPUT_PATH = OUTPUT_DIR / "index.md"

REPO_OWNER = "angryscan"
REPO_NAME = "angrydata-app"
RELEASES_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
RELEASES_HTML = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"

FRONT_MATTER = """---
title: Download
hide:
  - navigation
  - toc
---

# Download

Use the links below to download pre-built packages for Angry Data Scanner.
"""

@dataclass(frozen=True)
class AssetRule:
    """Configuration describing how to surface a release asset on the download page."""

    os_name: str
    badge_url: str
    alt_text: str
    suffixes: Tuple[str, ...]
    preferred_substrings: Tuple[str, ...] = ()

    def matches(self, asset_name: str) -> bool:
        return any(asset_name.endswith(suffix) for suffix in self.suffixes)


ASSET_RULES: Tuple[AssetRule, ...] = (
    AssetRule(
        os_name="Windows",
        badge_url="https://img.shields.io/badge/Setup-x64-0078D6?style=for-the-badge&logo=windows",
        alt_text="Windows setup (x64)",
        suffixes=(".exe",),
        preferred_substrings=("amd64", "x64"),
    ),
    AssetRule(
        os_name="Windows",
        badge_url="https://img.shields.io/badge/Portable-x64-0078D6?style=for-the-badge&logo=windows",
        alt_text="Windows portable .zip",
        suffixes=("-windows-amd64.zip",),
        preferred_substrings=("amd64", "x64"),
    ),
    AssetRule(
        os_name="Linux",
        badge_url="https://img.shields.io/badge/DEB-x64-A81D33?style=for-the-badge&logo=debian",
        alt_text="Linux .deb (amd64)",
        suffixes=(".deb",),
        preferred_substrings=("amd64", "x86_64"),
    ),
    AssetRule(
        os_name="Linux",
        badge_url="https://img.shields.io/badge/Portable-x64-333333?style=for-the-badge&logo=linux",
        alt_text="Linux portable tarball",
        suffixes=("-linux-amd64.tar.gz",),
        preferred_substrings=("amd64", "x86_64"),
    ),
    AssetRule(
        os_name="macOS",
        badge_url="https://img.shields.io/badge/macOS-x64-000000?style=for-the-badge&logo=apple",
        alt_text="macOS build",
        suffixes=(".dmg", ".pkg", "-macos.zip"),
        preferred_substrings=("universal", "arm64", "x86_64"),
    ),
)

OS_ORDER = ("Windows", "Linux", "macOS")
OS_LABELS = {
    "Windows": "**Windows**",
    "Linux": "**Linux**",
    "macOS": "**macOS**",
}
OS_PLACEHOLDER = {
    "Windows": "N/A",
    "Linux": "N/A",
    "macOS": '<img src="https://img.shields.io/badge/macOS-in%20progress-000000?style=for-the-badge&logo=apple" alt="macOS build in progress">',
}


def fetch_latest_release() -> dict:
    response = requests.get(
        RELEASES_API,
        params={"per_page": 1},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()
    releases = response.json()
    return releases[0] if releases else {}


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024.0 or unit == "GB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} GB"


def select_preferred_asset(
    current_asset: dict, candidate_asset: dict, preferred_substrings: Tuple[str, ...]
) -> dict:
    """Choose the most appropriate asset when multiple match the same rule."""

    if not current_asset:
        return candidate_asset
    if not preferred_substrings:
        return current_asset

    def score(asset: dict) -> Tuple[int, int]:
        name = asset.get("name", "").lower()
        for idx, token in enumerate(preferred_substrings):
            if token and token.lower() in name:
                return idx, -asset.get("size", 0)
        return len(preferred_substrings), -asset.get("size", 0)

    return candidate_asset if score(candidate_asset) < score(current_asset) else current_asset


def build_os_download(assets: Iterable[dict]) -> Tuple[Dict[str, list[str]], list[dict]]:
    """
    Group release assets by operating system and prepare HTML button markup.

    Returns a mapping of OS name to button HTML snippets and a list of assets that
    were not matched by any rule so they can be surfaced as additional download.
    """

    selected: Dict[AssetRule, dict] = {}
    extras: list[dict] = []

    for asset in assets:
        name = asset.get("name", "")
        matched_rule = next((rule for rule in ASSET_RULES if rule.matches(name)), None)
        if matched_rule is None:
            extras.append(asset)
            continue

        existing_asset = selected.get(matched_rule)
        preferred_asset = select_preferred_asset(
            existing_asset, asset, matched_rule.preferred_substrings
        )
        if preferred_asset is asset and existing_asset is not None:
            extras.append(existing_asset)
        elif preferred_asset is existing_asset:
            extras.append(asset)
            continue
        selected[matched_rule] = preferred_asset

    rows: Dict[str, list[str]] = {os_name: [] for os_name in OS_ORDER}
    for rule in ASSET_RULES:
        asset = selected.get(rule)
        if not asset:
            continue
        url = asset.get("browser_download_url", asset.get("html_url", "#"))
        rows[rule.os_name].append(
            f'<a href="{url}"><img src="{rule.badge_url}" alt="{rule.alt_text}"></a>'
        )

    return rows, extras


def render_os_table(os_buttons: Dict[str, list[str]]) -> list[str]:
    lines = ["| Operating system | Download |", "| --- | --- |"]
    for os_name in OS_ORDER:
        buttons = os_buttons.get(os_name) or []
        content = "<br/>".join(buttons) if buttons else OS_PLACEHOLDER.get(os_name, "—")
        lines.append(f"| {OS_LABELS.get(os_name, os_name)} | {content} |")
    return lines


def render_additional_assets(assets: list) -> list[str]:
    if not assets:
        return []
    lines = ["", "**Additional assets**", ""]
    for asset in assets:
        name = asset.get("name", "artifact")
        url = asset.get("browser_download_url", asset.get("html_url", "#"))
        size = human_size(asset.get("size", 0))
        lines.append(f"[`{name}`]({url}) ({size})  ")
    return lines


def format_release(release: dict) -> str:
    name = release.get("name") or release.get("tag_name", "Unnamed release")
    published_at = release.get("published_at")
    published_str = ""
    if published_at:
        published_str = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d"
        )
    body_lines = [f"## {name}"]
    if published_str:
        body_lines.append(f"*Published on {published_str}*")

    assets: Iterable[dict] = release.get("assets") or []
    os_buttons, unmatched_assets = build_os_download(assets)
    has_any_button = any(os_buttons.get(os_name) for os_name in OS_ORDER)
    if not has_any_button and not unmatched_assets:
        body_lines.append(
            "No binary assets were published for this release. Visit the "
            f"[GitHub release page]({release.get('html_url')}) for more details."
        )
        return "\n".join(body_lines)

    body_lines.append("")
    body_lines.extend(render_os_table(os_buttons))

    body_lines.extend(render_additional_assets(unmatched_assets))

    body_lines.append("")
    body_lines.append(
        f"[View full release notes]({release.get('html_url')}) for installation instructions."
    )
    return "\n".join(body_lines)


def render_content(release: dict) -> str:
    sections = [FRONT_MATTER.rstrip()]
    
    if not release:
        sections.append(
            "No releases are currently available. Please check the "
            f"[{REPO_NAME} releases]({RELEASES_HTML}) page for updates."
        )
    else:
        sections.append(format_release(release))
    
    sections.append(
        "\n> **Tip:** Builds are fetched automatically. Regenerate this page by running "
        "`python scripts/generate_download_page.py`."
    )
    return "\n\n".join(sections).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        release = fetch_latest_release()
    except Exception as exc:  # pylint: disable=broad-except
        fallback = (
            FRONT_MATTER
            + "\n"
            + "Failed to load release information at this time.\n\n"
            + f"Error: `{exc}`\n\n"
            + f"Visit the [GitHub releases page]({RELEASES_HTML}) directly."
        )
        OUTPUT_PATH.write_text(fallback.strip() + "\n", encoding="utf-8")
        return

    OUTPUT_PATH.write_text(render_content(release), encoding="utf-8")


if __name__ == "__main__":
    main()
