#!/usr/bin/env python3
"""Generate the downloads page from angrydata-app GitHub releases."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Iterable, List

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

    body_lines.append("")
    body_lines.append("| File | Size | Download |")
    body_lines.append("| --- | ---: | --- |")
    for asset in assets:
        asset_name = asset.get("name", "artifact")
        size = human_size(asset.get("size", 0))
        download_url = asset.get("browser_download_url", release.get("html_url", "#"))
        body_lines.append(f"| `{asset_name}` | {size} | [Download]({download_url}) |")

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
