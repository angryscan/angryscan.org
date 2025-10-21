#!/usr/bin/env python3
"""Sync documentation from sibling repositories into the local docs directory."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Tuple

from config_utils import get_all_locales, get_translation_locales, get_remove_headers, should_skip_until_first_header, should_process_translation_links

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
SOURCES_ROOT = ROOT / "sources"

REPOSITORIES: Tuple[Tuple[str, str, str], ...] = (
    ("angrydata-app", "AngryData App", "https://github.com/angryscan/angrydata-app.git"),
    ("angrydata-core", "AngryData Core", "https://github.com/angryscan/angrydata-core.git"),
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


def clone_repository(repo_url: str, repo_dir: Path) -> bool:
    """Clone repository from URL."""
    if repo_dir.exists():
        print(f"Repository {repo_dir.name} already exists, skipping clone", file=sys.stderr)
        return True
    
    try:
        print(f"Cloning repository: {repo_url}")
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Repository {repo_dir.name} cloned successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_dir.name}: {e}", file=sys.stderr)
        if e.stderr:
            print(f"Git error: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Git not found in system. Make sure git is installed.", file=sys.stderr)
        return False


def clone_repositories(repos: Iterable[Tuple[str, str, str]]) -> None:
    """Clone all repositories."""
    SOURCES_ROOT.mkdir(exist_ok=True)
    
    success_count = 0
    total_count = 0
    
    for slug, title, repo_url in repos:
        total_count += 1
        repo_dir = SOURCES_ROOT / slug
        if clone_repository(repo_url, repo_dir):
            success_count += 1
    
    print(f"\nCloning completed: {success_count}/{total_count} repositories cloned successfully")


def update_repository(repo_dir: Path) -> bool:
    """Update repository using git pull."""
    if not repo_dir.exists():
        print(f"Repository {repo_dir} does not exist, skipping update", file=sys.stderr)
        return False
    
    if not (repo_dir / ".git").exists():
        print(f"Directory {repo_dir} is not a git repository, skipping update", file=sys.stderr)
        return False
    
    try:
        print(f"Updating repository: {repo_dir.name}")
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Repository {repo_dir.name} updated successfully")
        if result.stdout.strip():
            print(f"Git pull output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating repository {repo_dir.name}: {e}", file=sys.stderr)
        if e.stderr:
            print(f"Git error: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Git not found in system. Make sure git is installed.", file=sys.stderr)
        return False


def update_repositories(repos: Iterable[Tuple[str, str, str]]) -> None:
    """Update all repositories."""
    if not SOURCES_ROOT.exists():
        print(f"Directory {SOURCES_ROOT} does not exist. Create it and clone repositories.", file=sys.stderr)
        return
    
    success_count = 0
    total_count = 0
    
    for slug, title, repo_url in repos:
        total_count += 1
        repo_dir = SOURCES_ROOT / slug
        if update_repository(repo_dir):
            success_count += 1
    
    print(f"\nUpdate completed: {success_count}/{total_count} repositories updated successfully")


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


def process_content_lines(content_lines: list[str]) -> list[str]:
    """Process content lines to remove configured sections and translation links."""
    processed_lines = []
    
    # Получаем конфигурацию
    remove_headers = get_remove_headers()
    skip_until_first_header = should_skip_until_first_header()
    process_translation_links = should_process_translation_links()
    
    # Флаги для обработки контента
    skip_until_first_header_flag = skip_until_first_header
    in_removable_section = False
    current_removable_header = None
    first_header_found = False
    
    for line in content_lines:
        line_no_bom = line.lstrip("\ufeff")
        stripped = line_no_bom.strip()
        
        # Пропускаем пустые строки и строки с переводами до первого заголовка
        if skip_until_first_header_flag:
            if stripped.startswith("#"):
                first_header_found = True
                skip_until_first_header_flag = False
                processed_lines.append(line_no_bom.rstrip())
                continue
            elif stripped == "" or (process_translation_links and TRANSLATION_LINK_PATTERN.fullmatch(stripped)):
                continue
            else:
                # Если это не заголовок и не пустая строка, пропускаем до первого заголовка
                continue
        
        # Проверяем начало любого из удаляемых разделов
        if stripped in remove_headers:
            in_removable_section = True
            current_removable_header = stripped
            continue
        
        # Если мы в удаляемом разделе, пропускаем все до следующего заголовка
        if in_removable_section:
            if stripped.startswith("##") and stripped not in remove_headers:
                in_removable_section = False
                current_removable_header = None
                # Не добавляем эту строку, так как мы пропускаем весь удаляемый раздел
                continue
            else:
                continue
        
        # Обрабатываем ссылки на переводы (если включено)
        if process_translation_links:
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
        else:
            processed_lines.append(line_no_bom.rstrip())
    
    return processed_lines


def sanitize_translation_links(doc_dir: Path) -> None:
    """Strip links that point to translation markdown files and remove Direct Download section."""
    for md_file in doc_dir.rglob("*.md"):
        if is_translation_filename(md_file.name):
            continue
        # Пропускаем корневой index.md - это файл-редирект
        if md_file.name == "index.md" and md_file.parent == doc_dir:
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
                
                lines = [f"---\n{front_matter}\n---\n{content}"]
            else:
                lines = original.splitlines()
        else:
            # Добавляем front matter с hide: navigation и toc
            lines = ["---", "hide:", "  - navigation", "  - toc", "---", ""] + original.splitlines()
            modified = True
        
        # Обрабатываем остальную часть как раньше
        if not has_front_matter or modified:
            if not has_front_matter:
                # Если front matter добавлялся, берем контент после него
                content_lines = lines[5:]  # Пропускаем добавленный front matter (включая пустую строку)
            else:
                # Если front matter уже был, берем весь контент
                content_lines = lines
            
            processed_lines = process_content_lines(content_lines)
            
            if not has_front_matter:
                # Объединяем добавленный front matter с обработанным контентом
                lines = lines[:5] + processed_lines  # Включаем пустую строку после front matter
            else:
                # Заменяем только контент, сохраняя front matter
                lines = lines[:4] + processed_lines

        if modified or not has_front_matter:
            md_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_pages_metadata(doc_dir: Path, slug: str, title: str) -> None:
    pages_file = doc_dir / ".pages"
    title_line = f"title: {title}\n"
    if slug != "angrydata-app":
        pages_file.write_text(title_line, encoding="utf-8")
        return

    download_dir = doc_dir / "download"
    placeholder_path = download_dir / "index.md"
    if not download_dir.exists():
        download_dir.mkdir(parents=True, exist_ok=True)
    download_meta = download_dir / ".pages"
    if not download_meta.exists():
        download_meta.write_text("collapse_single_pages: true\n", encoding="utf-8")
    if not placeholder_path.exists():
        placeholder_path.write_text(
            "---\n"
            "title: Download\n"
            "---\n\n"
            "Download will be generated automatically. "
            "Run `python scripts/generate_download_page.py` to populate this section.\n",
            encoding="utf-8",
        )

    # Упрощенная навигация - только основные разделы без внутренних переходов
    pages_file.write_text(
        title_line + "arrange:\n  - ...\n  - download\n",
        encoding="utf-8",
    )


def get_repository_title(slug: str, title: str) -> str:
    normalized = title.strip()
    if slug == "angrydata-app":
        normalized = "Main"
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


def sync_repo(repo_slug: str, title: str, repo_url: str) -> None:
    repo_dir = SOURCES_ROOT / repo_slug
    if not repo_dir.exists():
        print(f"Repository {repo_slug} not found, attempting to clone...")
        SOURCES_ROOT.mkdir(exist_ok=True)
        if not clone_repository(repo_url, repo_dir):
            raise FileNotFoundError(
                f"Failed to clone repository {repo_slug} from {repo_url}."
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


def sync(repos: Iterable[Tuple[str, str, str]]) -> None:
    reset_docs_root()
    repo_entries: list[tuple[str, str]] = []
    for slug, title, repo_url in repos:
        sync_repo(slug, title, repo_url)
        repo_entries.append((slug, get_repository_title(slug, title)))

    root_pages = DOCS_ROOT / ".pages"
    # Упрощенная навигация - только основные разделы
    nav_content = """title: Angry Data Scanner
nav:
  - Main: angrydata-app
  - Angry Data Core: angrydata-core
  - Download: angrydata-app/download
"""
    root_pages.write_text(nav_content, encoding="utf-8")

    default_slug, default_title, _ = repos[0]
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
    parser.add_argument(
        "--update-repos",
        action="store_true",
        help="Update repositories before syncing documentation"
    )
    parser.add_argument(
        "--only-update",
        action="store_true", 
        help="Only update repositories without syncing documentation"
    )
    parser.add_argument(
        "--clone-repos",
        action="store_true",
        help="Clone repositories before syncing documentation"
    )
    parser.add_argument(
        "--only-clone",
        action="store_true",
        help="Only clone repositories without syncing documentation"
    )
    args = parser.parse_args()
    
    if args.only_clone:
        print("Cloning repositories...")
        clone_repositories(REPOSITORIES)
    elif args.only_update:
        print("Updating repositories...")
        update_repositories(REPOSITORIES)
    elif args.clone_repos:
        print("Cloning repositories and syncing documentation...")
        clone_repositories(REPOSITORIES)
        sync(REPOSITORIES)
    elif args.update_repos:
        print("Updating repositories and syncing documentation...")
        update_repositories(REPOSITORIES)
        sync(REPOSITORIES)
    else:
        print("Syncing documentation...")
        sync(REPOSITORIES)


if __name__ == "__main__":
    main()
