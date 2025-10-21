#!/usr/bin/env python3
"""Sync documentation from sibling repositories into the local docs directory."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Iterable, Tuple

from config_utils import get_all_locales, get_translation_locales

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
SOURCES_ROOT = ROOT / "sources"

REPOSITORIES: Tuple[Tuple[str, str], ...] = (
    ("angrydata-app", "AngryData App"),
    ("angrydata-core", "AngryData Core"),
)

ALL_LOCALES = [locale for locale in get_all_locales() if locale]
TRANSLATION_LOCALES = [locale for locale in get_translation_locales() if locale]

TRANSLATION_SUFFIXES = tuple(
    suffix
    for locale in ALL_LOCALES
    for suffix in (f".{locale}.md", f".{locale}.markdown")
)

if ALL_LOCALES:
    escaped_locales = sorted(
        {re.escape(locale) for locale in ALL_LOCALES},
        key=len,
        reverse=True,
    )
    locale_pattern = "|".join(escaped_locales)
else:
    locale_pattern = "ru|es|de"

TRANSLATION_LINK_PATTERN = re.compile(
    rf"\[([^\]]+)\]\(([^)]+\.({locale_pattern})\.(?:md|markdown))\)", re.IGNORECASE
)


def is_translation_filename(name: str) -> bool:
    lowered = name.lower()
    return any(lowered.endswith(suffix) for suffix in TRANSLATION_SUFFIXES)


ASSET_PRESERVE = {"assets"}


def reset_docs_root() -> None:
    """Remove any previously generated documentation from this repository."""
    if not DOCS_ROOT.exists():
        DOCS_ROOT.mkdir(parents=True)
        return

    for path in DOCS_ROOT.iterdir():
        if path.name in {".gitignore", *ASSET_PRESERVE}:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def copytree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    if TRANSLATION_SUFFIXES:
        patterns = [f"*{suffix}" for suffix in TRANSLATION_SUFFIXES]
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*patterns))
    else:
        shutil.copytree(src, dest)


def ensure_index(doc_dir: Path) -> None:
    """Make sure the directory contains an index file for MkDocs."""
    index_candidates = [doc_dir / f"index.{ext}" for ext in ("md", "markdown")]
    if any(candidate.exists() for candidate in index_candidates):
        return

    readme_candidates = [doc_dir / f"README.{ext}" for ext in ("md", "markdown")]
    for readme in readme_candidates:
        if readme.exists():
            readme.rename(doc_dir / "index.md")
            return

    # Create a placeholder index to avoid MkDocs build failures.
    (doc_dir / "index.md").write_text(
        "# Documentation\n\n"
        "This documentation set was imported automatically, but no index page was found."
        "\n\nPlease add an `index.md` (or `README.md`) file to the upstream repository.\n",
        encoding="utf-8",
    )


def sanitize_translation_links(doc_dir: Path) -> None:
    """Strip links that point to translation markdown files."""
    for md_file in doc_dir.rglob("*.md"):
        if is_translation_filename(md_file.name):
            continue
        original = md_file.read_text(encoding="utf-8")
        lines: list[str] = []
        modified = False
        
        # Проверяем, есть ли уже front matter
        has_front_matter = original.startswith("---")
        if has_front_matter:
            # Извлекаем существующий front matter
            parts = original.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1].strip()
                content = parts[2].lstrip("\n")
                
                # Добавляем hide: navigation и toc если их нет
                if "hide:" not in front_matter:
                    front_matter += "\nhide:\n  - navigation\n  - toc"
                    modified = True
                else:
                    # Если hide уже есть, добавляем navigation и toc если их нет
                    if "navigation" not in front_matter:
                        front_matter = front_matter.replace("hide:", "hide:\n  - navigation")
                        modified = True
                    if "toc" not in front_matter:
                        front_matter = front_matter.replace("hide:", "hide:\n  - toc")
                        modified = True
                
                lines = [f"---\n{front_matter}\n---{content}"]
            else:
                lines = original.splitlines()
        else:
            # Добавляем front matter с hide: navigation и toc
            lines = ["---", "hide:", "  - navigation", "  - toc", "---", ""] + original.splitlines()
            modified = True
        
        # Обрабатываем остальную часть как раньше
        if not has_front_matter or modified:
            content_lines = lines[4:] if not has_front_matter else lines
            processed_lines = []
            
            for line in content_lines:
                line_no_bom = line.lstrip("\ufeff")
                stripped = line_no_bom.strip()
                if TRANSLATION_LINK_PATTERN.fullmatch(stripped):
                    continue
                skip_line = False
                for prefix in ("- ", "* ", "+ "):
                    if stripped.startswith(prefix):
                        candidate = stripped[len(prefix) :].strip()
                        if TRANSLATION_LINK_PATTERN.fullmatch(candidate):
                            skip_line = True
                            break
                if skip_line:
                    continue
                if TRANSLATION_LINK_PATTERN.search(line_no_bom):
                    without_links = TRANSLATION_LINK_PATTERN.sub("", line_no_bom)
                    trimmed = without_links.strip()
                    trimmed = trimmed.lstrip("-*+•·—–:| ").strip()
                    if not trimmed:
                        continue
                    if not any(char.isalnum() for char in trimmed):
                        continue
                    replaced_line = TRANSLATION_LINK_PATTERN.sub(
                        lambda match: match.group(1), line_no_bom
                    )
                    processed_lines.append(replaced_line.rstrip())
                else:
                    processed_lines.append(line_no_bom.rstrip())
            
            if not has_front_matter:
                lines = lines[:4] + processed_lines
            else:
                lines = processed_lines

        if modified or not has_front_matter:
            md_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_pages_metadata(doc_dir: Path, slug: str, title: str) -> None:
    pages_file = doc_dir / ".pages"
    title_line = f"title: {title}\n"
    if slug != "angrydata-app":
        pages_file.write_text(title_line, encoding="utf-8")
        return

    downloads_dir = doc_dir / "downloads"
    placeholder_path = downloads_dir / "index.md"
    if not downloads_dir.exists():
        downloads_dir.mkdir(parents=True, exist_ok=True)
    downloads_meta = downloads_dir / ".pages"
    if not downloads_meta.exists():
        downloads_meta.write_text("collapse_single_pages: true\n", encoding="utf-8")
    if not placeholder_path.exists():
        placeholder_path.write_text(
            "---\n"
            "title: Downloads\n"
            "---\n\n"
            "Downloads will be generated automatically. "
            "Run `python scripts/generate_downloads_page.py` to populate this section.\n",
            encoding="utf-8",
        )

    # Упрощенная навигация - только основные разделы без внутренних переходов
    pages_file.write_text(
        title_line + "arrange:\n  - ...\n  - downloads\n",
        encoding="utf-8",
    )


def get_repository_title(slug: str, title: str) -> str:
    normalized = title.strip()
    if slug == "angrydata-app":
        normalized = "Angry Data Scanner"
    return normalized
    pages_file.write_text(f"title: {title}\n", encoding="utf-8")


def find_doc_root(repo_dir: Path) -> Path | None:
    candidates = [
        repo_dir / "docs",
        repo_dir / "documentation",
        repo_dir / "doc",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    readme = repo_dir / "README.md"
    if readme.exists():
        temp_dir = repo_dir / ".aggregated-docs"
        temp_dir.mkdir(exist_ok=True)
        shutil.copy2(readme, temp_dir / "index.md")
        return temp_dir
    return None


def sync_repo(repo_slug: str, title: str) -> None:
    repo_dir = SOURCES_ROOT / repo_slug
    if not repo_dir.exists():
        raise FileNotFoundError(
            f"Expected repository at {repo_dir}. Make sure it has been checked out first."
        )

    doc_root = find_doc_root(repo_dir)
    if doc_root is None:
        raise FileNotFoundError(
            f"Could not locate documentation inside {repo_slug}."
            " Provide a docs/ directory or README.md."
        )

    has_inline_index = any((doc_root / f"index.{ext}").exists() for ext in ("md", "markdown"))
    has_inline_readme = any((doc_root / f"README.{ext}").exists() for ext in ("md", "markdown"))
    repo_readme = repo_dir / "README.md"
    should_inject_repo_readme = not has_inline_index and not has_inline_readme and repo_readme.exists()

    destination = DOCS_ROOT / repo_slug
    copytree(doc_root, destination)

    if should_inject_repo_readme:
        content = repo_readme.read_text(encoding="utf-8")
        doc_prefix = f"{doc_root.name}/"
        link_prefix_pattern = re.compile(rf"(\[[^\]]+\]\()({re.escape(doc_prefix)})([^)]+)\)")
        content = content.replace("(README.md", "(index.md")
        content = link_prefix_pattern.sub(r"\1\3)", content)
        destination.joinpath("index.md").write_text(content, encoding="utf-8")
    else:
        ensure_index(destination)

    sanitize_translation_links(destination)

    write_pages_metadata(destination, repo_slug, get_repository_title(repo_slug, title))

    temp_dir = repo_dir / ".aggregated-docs"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def sync(repos: Iterable[Tuple[str, str]]) -> None:
    reset_docs_root()
    repo_entries: list[tuple[str, str]] = []
    for slug, title in repos:
        sync_repo(slug, title)
        repo_entries.append((slug, get_repository_title(slug, title)))

    root_pages = DOCS_ROOT / ".pages"
    # Упрощенная навигация - только основные разделы
    nav_content = """title: Angry Data Scanner
nav:
  - Angry Data Scanner: angrydata-app
  - Downloads: angrydata-app/downloads
  - Angry Data Core: angrydata-core
"""
    root_pages.write_text(nav_content, encoding="utf-8")

    default_slug, default_title = repos[0]
    redirect = DOCS_ROOT / "index.md"
    redirect.write_text(
        (
            "---\n"
            "title: Home\n"
            "---\n\n"
            f'<meta http-equiv="refresh" content="0; url={default_slug}/" />\n'
            "<script>"
            f'window.location.replace("{default_slug}/");'
            "</script>\n\n"
            f"If you are not redirected automatically, open [{default_title}]({default_slug}/index.md).\n"
        ),
        encoding="utf-8",
    )

    sanitize_translation_links(DOCS_ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    sync(REPOSITORIES)


if __name__ == "__main__":
    main()
