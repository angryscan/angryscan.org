#!/usr/bin/env python3
"""Sync documentation from sibling repositories into the local docs directory."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Iterable, Tuple

from config_utils import (
    get_all_locales, 
    get_translation_locales, 
    get_remove_headers, 
    should_skip_until_first_header, 
    should_process_translation_links,
    apply_metadata_to_content
)

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
SOURCES_ROOT = ROOT / "sources"

REPOSITORIES: Tuple[Tuple[str, str, str], ...] = (
    ("angrydata-app", "AngryData App", "https://github.com/angryscan/angrydata-app.git"),
    # ("angrydata-core", "AngryData Core", "https://github.com/angryscan/angrydata-core.git"),
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
    patterns = ["CONSOLE.md", "CONSOLE.*.md"]
    if TRANSLATION_SUFFIXES:
        patterns.extend([f"*{suffix}" for suffix in TRANSLATION_SUFFIXES])
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*patterns))


def copytree_to_root(src: Path, dest: Path) -> None:
    """Copy tree to root directory, preserving existing files like .gitignore and assets."""
    # Copy files from src to dest without removing existing files
    for item in src.iterdir():
        # Check if file should be ignored
        should_ignore = False
        
        # Ignore CONSOLE.md and its translations
        if item.name == "CONSOLE.md" or (item.name.startswith("CONSOLE.") and item.name.endswith(".md")):
            should_ignore = True
        
        if not should_ignore and TRANSLATION_SUFFIXES:
            for suffix in TRANSLATION_SUFFIXES:
                if item.name.lower().endswith(suffix):
                    should_ignore = True
                    break
        
        if should_ignore:
            continue
        
        dest_item = dest / item.name
        
        if item.is_file():
            # Copy file, overwriting existing
            shutil.copy2(item, dest_item)
        elif item.is_dir():
            # Copy directory
            if dest_item.exists():
                shutil.rmtree(dest_item)
            patterns = ["CONSOLE.md", "CONSOLE.*.md"]
            if TRANSLATION_SUFFIXES:
                patterns.extend([f"*{suffix}" for suffix in TRANSLATION_SUFFIXES])
            shutil.copytree(item, dest_item, ignore=shutil.ignore_patterns(*patterns))


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
    
    # Get configuration
    remove_headers = get_remove_headers()
    skip_until_first_header = should_skip_until_first_header()
    process_translation_links = should_process_translation_links()
    
    # Flags for content processing
    skip_until_first_header_flag = skip_until_first_header
    in_removable_section = False
    current_removable_header = None
    first_header_found = False
    
    for line in content_lines:
        line_no_bom = line.lstrip("\ufeff")
        stripped = line_no_bom.strip()
        
        # Skip empty lines and translation lines until first header
        if skip_until_first_header_flag:
            if stripped.startswith("#"):
                first_header_found = True
                skip_until_first_header_flag = False
                processed_lines.append(line_no_bom.rstrip())
                continue
            elif stripped == "" or (process_translation_links and TRANSLATION_LINK_PATTERN.fullmatch(stripped)):
                continue
            else:
                # If not a header and not empty line, skip until first header
                continue
        
        # Check for start of any removable section
        if stripped in remove_headers:
            in_removable_section = True
            current_removable_header = stripped
            continue
        
        # If in removable section, skip everything until next header
        if in_removable_section:
            if stripped.startswith("##") and stripped not in remove_headers:
                in_removable_section = False
                current_removable_header = None
                # Don't add this line as we skip the entire removable section
                continue
            else:
                continue
        
        # Process translation links (if enabled)
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


def apply_custom_metadata(doc_dir: Path) -> None:
    """Apply custom metadata to markdown files based on configuration."""
    for md_file in doc_dir.rglob("*.md"):
        if is_translation_filename(md_file.name):
            continue
        # Skip root index.md only if it's a redirect (contains meta refresh)
        if md_file.name == "index.md" and md_file.parent == doc_dir:
            content = md_file.read_text(encoding="utf-8")
            if "meta http-equiv=\"refresh\"" in content or "window.location.replace" in content:
                continue
        
        # Get relative path for metadata lookup
        relative_path = md_file.relative_to(doc_dir)
        file_path_str = str(relative_path).replace("\\", "/")
        
        # Apply custom metadata
        original_content = md_file.read_text(encoding="utf-8")
        updated_content = apply_metadata_to_content(original_content, file_path_str)
        
        if updated_content != original_content:
            md_file.write_text(updated_content, encoding="utf-8")


def clean_hide_duplicates(content: str) -> str:
    """Clean up duplicate hide entries in front matter."""
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    front_matter = parts[1].strip()
    content_after = parts[2].lstrip("\n")
    
    if "hide:" not in front_matter:
        return content
    
    # Check if there are duplicates
    nav_count = front_matter.count('- navigation')
    toc_count = front_matter.count('- toc')
    
    if nav_count <= 1 and toc_count <= 1:
        return content  # No duplicates, return as is
    
    # Replace the entire hide section with a clean one
    lines = front_matter.split('\n')
    new_lines = []
    in_hide_section = False
    hide_added = False
    hide_values = set()  # Track unique hide values to avoid duplicates
    
    for line in lines:
        if line.strip().startswith('hide:'):
            in_hide_section = True
            new_lines.append(line)
            if not hide_added:
                # Only add if not already present
                if '- navigation' not in hide_values:
                    new_lines.append('  - navigation')
                    hide_values.add('- navigation')
                if '- toc' not in hide_values:
                    new_lines.append('  - toc')
                    hide_values.add('- toc')
                hide_added = True
        elif in_hide_section and line.startswith('  -'):
            # Track existing hide entries to avoid duplicates
            hide_value = line.strip()
            if hide_value not in hide_values:
                hide_values.add(hide_value)
                new_lines.append(line)
            # Skip duplicates
        elif in_hide_section and not line.startswith('  '):
            in_hide_section = False
            new_lines.append(line)
        elif not in_hide_section:
            new_lines.append(line)
    
    new_front_matter = '\n'.join(new_lines)
    return f"---\n{new_front_matter}\n---\n{content_after}"


def parse_badge_url(badge_url: str) -> tuple[str, str] | None:
    """
    Parse shields.io badge URL to extract left and right text.
    
    Example: https://img.shields.io/badge/x64-Portable-0078D6?style=for-the-badge
    Returns: ("x64", "Portable")
    
    Example: https://img.shields.io/badge/Online%20Installer-x64-0078D6
    Returns: ("Online Installer", "x64")
    """
    # Extract the badge path (everything between /badge/ and the color or query params)
    badge_match = re.search(r'/badge/([^?]+)', badge_url)
    if not badge_match:
        return None
    
    badge_text = badge_match.group(1)
    
    # Split by hyphen, but only the last occurrence before the color code
    # Badge format: text1-text2-color where color is hex or color name
    parts = badge_text.split('-')
    
    if len(parts) < 2:
        return None
    
    # The last part is typically the color (hex code or color name)
    # Check if last part looks like a color code (3 or 6 hex chars)
    last_part_is_hex = (
        (len(parts[-1]) == 6 or len(parts[-1]) == 3) and 
        all(c in '0123456789ABCDEFabcdef' for c in parts[-1])
    )
    
    if last_part_is_hex:
        # Last part is color, take the one before as right text
        if len(parts) < 3:
            return None
        right_text = parts[-2]
        left_text = '-'.join(parts[:-2])
    else:
        # No color in URL, split into two parts
        right_text = parts[-1]
        left_text = '-'.join(parts[:-1])
    
    # Decode URL encoding
    left_text = urllib.parse.unquote_plus(left_text.replace('%20', ' '))
    right_text = urllib.parse.unquote_plus(right_text.replace('%20', ' '))
    
    return (left_text, right_text)


def replace_badge_with_divs(content: str) -> str:
    """
    Replace <img> badge elements with div elements containing parsed text.
    
    Converts:
        <img src="https://img.shields.io/badge/x64-Portable-..." alt="...">
    To:
        <div class="badge-left">x64</div><div class="badge-right">Portable</div>
    
    Special case for "in progress":
        <img src="https://img.shields.io/badge/macOS-in%20progress-..." alt="...">
    To:
        <div class="badge-only">in progress</div>
    """
    # Pattern to match img tags with shields.io badge URLs (flexible attribute order)
    # Matches both: src before alt and alt before src
    img_pattern = r'<img\s+(?:src="(https?://img\.shields\.io/badge/[^"]+)"\s+alt="[^"]*"|alt="[^"]*"\s+src="(https?://img\.shields\.io/badge/[^"]+)")\s*/?>'
    
    def replace_img(match):
        # Get URL from either group 1 or group 2
        img_url = match.group(1) if match.group(1) else match.group(2)
        parsed = parse_badge_url(img_url)
        
        if parsed:
            left_text, right_text = parsed
            
            # Special case: if right text is "in progress", show only that
            if right_text.lower() in ['in progress', 'in_progress', 'coming soon', 'coming_soon']:
                return f'<div class="badge-only">{right_text}</div>'
            
            return f'<div class="badge-left">{left_text}</div><div class="badge-right">{right_text}</div>'
        
        # If parsing failed, return original
        return match.group(0)
    
    return re.sub(img_pattern, replace_img, content)


def process_badge_images(doc_dir: Path) -> None:
    """Process all markdown files to replace badge images with div elements."""
    for md_file in doc_dir.rglob("*.md"):
        if is_translation_filename(md_file.name):
            continue
        
        # Skip root index.md only if it's a redirect (contains meta refresh)
        if md_file.name == "index.md" and md_file.parent == doc_dir:
            content = md_file.read_text(encoding="utf-8")
            if "meta http-equiv=\"refresh\"" in content or "window.location.replace" in content:
                continue
        
        original_content = md_file.read_text(encoding="utf-8")
        updated_content = replace_badge_with_divs(original_content)
        
        if updated_content != original_content:
            md_file.write_text(updated_content, encoding="utf-8")
            print(f"Processed badges in: {md_file.relative_to(doc_dir)}")


def sanitize_translation_links(doc_dir: Path) -> None:
    """Strip links that point to translation markdown files and remove Direct Download section."""
    for md_file in doc_dir.rglob("*.md"):
        if is_translation_filename(md_file.name):
            continue
        # Skip root index.md only if it's a redirect (contains meta refresh)
        if md_file.name == "index.md" and md_file.parent == doc_dir:
            content = md_file.read_text(encoding="utf-8")
            if "meta http-equiv=\"refresh\"" in content or "window.location.replace" in content:
                continue
        original = md_file.read_text(encoding="utf-8")
        lines: list[str] = []
        modified = False
        
        # First, clean up any existing duplicates
        cleaned_content = clean_hide_duplicates(original)
        if cleaned_content != original:
            original = cleaned_content
            modified = True
        
        # Check if front matter already exists
        has_front_matter = original.startswith("---")
        if has_front_matter:
            # Extract existing front matter
            parts = original.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1].strip()
                content = parts[2].lstrip("\n")
                
                # Add hide: navigation and toc if not present
                if "hide:" not in front_matter:
                    front_matter += "\nhide:\n  - navigation\n  - toc"
                    modified = True
                else:
                    # Check if hide: exists but has no values (just "hide:" or "hide: ")
                    hide_pattern = r'hide:\s*$'
                    import re
                    if re.search(hide_pattern, front_matter, re.MULTILINE):
                        # Replace empty hide with proper values
                        front_matter = re.sub(hide_pattern, "hide:\n  - navigation\n  - toc", front_matter, flags=re.MULTILINE)
                        modified = True
                    else:
                        # If hide already exists with values, check if navigation and toc are present
                        nav_count = front_matter.count('- navigation')
                        toc_count = front_matter.count('- toc')
                        
                        if nav_count == 0 or toc_count == 0:
                            # Parse hide section and add missing values properly
                            lines = front_matter.split('\n')
                            new_lines = []
                            in_hide_section = False
                            hide_added = False
                            
                            for line in lines:
                                if line.strip().startswith('hide:'):
                                    in_hide_section = True
                                    new_lines.append(line)
                                    if not hide_added:
                                        if nav_count == 0:
                                            new_lines.append('  - navigation')
                                        if toc_count == 0:
                                            new_lines.append('  - toc')
                                        hide_added = True
                                elif in_hide_section and line.startswith('  -'):
                                    # Skip existing hide entries to avoid duplicates
                                    continue
                                elif in_hide_section and not line.startswith('  '):
                                    in_hide_section = False
                                    new_lines.append(line)
                                elif not in_hide_section:
                                    new_lines.append(line)
                            
                            front_matter = '\n'.join(new_lines)
                            modified = True
                
                lines = [f"---\n{front_matter}\n---\n{content}"]
            else:
                lines = original.splitlines()
        else:
            # Add front matter with hide: navigation and toc
            lines = ["---", "hide:", "  - navigation", "  - toc", "---", ""] + original.splitlines()
            modified = True
        
        # Process the rest as before
        if not has_front_matter or modified:
            if not has_front_matter:
                # If front matter was added, take content after it
                content_lines = lines[5:]  # Skip added front matter (including empty line)
            else:
                # If front matter already existed, take all content
                content_lines = lines
            
            processed_lines = process_content_lines(content_lines)
            
            if not has_front_matter:
                # Combine added front matter with processed content
                lines = lines[:5] + processed_lines  # Include empty line after front matter
            else:
                # Replace only content, preserving front matter
                lines = lines[:4] + processed_lines

        if modified or not has_front_matter:
            final_content = "\n".join(lines).rstrip() + "\n"
            # Final cleanup to ensure no duplicates remain
            cleaned_final = clean_hide_duplicates(final_content)
            md_file.write_text(cleaned_final, encoding="utf-8")


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

    # For angrydata-app copy content to docs root, for others - to subdirectories
    if repo_slug == "angrydata-app":
        destination = DOCS_ROOT
        copytree_to_root(doc_root, destination)
    else:
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
    
    # Apply custom metadata
    apply_custom_metadata(destination)
    
    # Process badge images
    process_badge_images(destination)

    temp_dir = repo_dir / ".aggregated-docs"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def copy_static_files() -> None:
    """Copy static files from scripts/static to docs root."""
    static_dir = ROOT / "scripts" / "static"
    if not static_dir.exists():
        print(f"Warning: Static directory {static_dir} does not exist", file=sys.stderr)
        return
    
    for static_file in static_dir.iterdir():
        if static_file.is_file():
            dest_file = DOCS_ROOT / static_file.name
            shutil.copy2(static_file, dest_file)
            print(f"Copied {static_file.name} to docs root")


def sync(repos: Iterable[Tuple[str, str, str]]) -> None:
    reset_docs_root()
    for slug, title, repo_url in repos:
        sync_repo(slug, title, repo_url)

    # For angrydata-app in root, don't create redirect as content is already in root
    # Main content of angrydata-app is already copied to root, so no need to create redirect

    sanitize_translation_links(DOCS_ROOT)
    
    # Apply custom metadata to all documentation
    apply_custom_metadata(DOCS_ROOT)
    
    # Process badge images in all documentation
    process_badge_images(DOCS_ROOT)
    
    # Copy static files (robots.txt, BingSiteAuth.xml, etc.)
    copy_static_files()


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
