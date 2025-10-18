#!/usr/bin/env python3
"""Generate the downloads page from angrydata-app GitHub releases."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
OUTPUT_DIR = DOCS_ROOT / "downloads"
OUTPUT_PATH = OUTPUT_DIR / "index.md"

REPO_OWNER = "angryscan"
REPO_NAME = "angrydata-app"
RELEASES_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
RELEASES_HTML = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"

FRONT_MATTER = """---
title: Downloads
---

# Downloads

Use the links below to download pre-built packages for Angry Data Scanner.
"""

CATEGORY_DEFINITIONS: Tuple[
    Tuple[str, str, str, Tuple[str, ...], str],
    ...
] = (
    (
        "linux_portable",
        "Linux",
        "Portable tarball",
        ("-linux-amd64.tar.gz",),
        "https://img.shields.io/badge/Linux-111111?logo=linux&logoColor=white",
    ),
    (
        "windows_installer",
        "Windows",
        "Installer",
        (".exe", ".msix", ".appinstaller"),
        "https://img.shields.io/badge/Windows%20Installer-0067b8?logo=windows&logoColor=white",
    ),
    (
        "debian",
        "Linux",
        "Debian package",
        (".deb",),
        "https://img.shields.io/badge/Debian%20Package-a80030?logo=debian&logoColor=white",
    ),
    (
        "windows_portable",
        "Windows",
        "Portable zip",
        ("-windows-amd64.zip",),
        "https://img.shields.io/badge/Windows%20Portable-444?logo=windows&logoColor=white",
    ),
)

CATEGORY_ORDER = [definition[0] for definition in CATEGORY_DEFINITIONS] + ["other"]

CATEGORY_METADATA = {
    key: {"os": os_label, "installer": installer, "badge": badge_url}
    for key, os_label, installer, _, badge_url in CATEGORY_DEFINITIONS
}


def fetch_releases(limit: int) -> List[dict]:
    response = requests.get(
        RELEASES_API,
        params={"per_page": limit},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024.0 or unit == "GB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} GB"


def categorize_assets(assets: Iterable[dict]) -> Dict[str, List[dict]]:
    categorized: Dict[str, List[dict]] = {key: [] for key in CATEGORY_ORDER}
    for asset in assets:
        name = asset.get("name", "")
        target_category = "other"
        for key, _, _, suffixes, _ in CATEGORY_DEFINITIONS:
            if any(name.endswith(suffix) for suffix in suffixes):
                target_category = key
                break
        categorized.setdefault(target_category, []).append(asset)
    return {key: items for key, items in categorized.items() if items}


def render_category_table(category: str, assets: List[dict]) -> List[str]:
    meta = CATEGORY_METADATA.get(
        category,
        {
            "os": "Other",
            "installer": "Artifacts",
            "badge": "https://img.shields.io/badge/Download-555555?style=flat",
        },
    )
    lines = ["| OS | Installer | Size | |", "| --- | --- | ---: | --- |"]
    for asset in assets:
        asset_name = asset.get("name", "artifact")
        size = human_size(asset.get("size", 0))
        download_url = asset.get("browser_download_url", asset.get("html_url", "#"))
        badge = meta["badge"]
        lines.append(
            f'| ![]({badge}) | {meta["installer"]} (`{asset_name}`) | {size} | '
            f'[![Download](https://img.shields.io/badge/Download-4c1?logo=github&style=flat)]({download_url}) |'
        )
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
    if not assets:
        body_lines.append(
            "No binary assets were published for this release. Visit the "
            f"[GitHub release page]({release.get('html_url')}) for more details."
        )
        return "\n".join(body_lines)

    categorized_assets = categorize_assets(assets)
    for key in CATEGORY_ORDER:
        if key not in categorized_assets:
            continue
        body_lines.append("")
        meta = CATEGORY_METADATA.get(key, {"os": "Other", "installer": "Artifacts", "badge": ""})
        body_lines.append(
            f'### {meta.get("os", "Other")} · {meta.get("installer", "Artifacts")}'
        )
        body_lines.extend(render_category_table(key, categorized_assets[key]))

    body_lines.append("")
    body_lines.append(
        f"[View full release notes]({release.get('html_url')}) for installation instructions."
    )
    return "\n".join(body_lines)


def render_content(releases: Iterable[dict]) -> str:
    sections = [FRONT_MATTER.rstrip()]
    for release in releases:
        sections.append(format_release(release))
    if len(sections) == 1:
        sections.append(
            "No releases are currently available. Please check the "
            f"[{REPO_NAME} releases]({RELEASES_HTML}) page for updates."
        )
    sections.append(
        "\n> **Tip:** Builds are fetched automatically. Regenerate this page by running "
        "`python scripts/generate_downloads_page.py`."
    )
    return "\n\n".join(sections).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recent releases to include (default: %(default)s).",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        releases = fetch_releases(limit=args.limit)
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

    OUTPUT_PATH.write_text(render_content(releases[: args.limit]), encoding="utf-8")


if __name__ == "__main__":
    main()
