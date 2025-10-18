#!/usr/bin/env python3
"""Sync documentation from sibling repositories into the local docs directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
SOURCES_ROOT = ROOT / "sources"

REPOSITORIES: Tuple[Tuple[str, str], ...] = (
    ("angrydata-app", "AngryData App"),
    ("angrydata-core", "AngryData Core"),
)


def reset_docs_root() -> None:
    """Remove any previously generated documentation from this repository."""
    if not DOCS_ROOT.exists():
        DOCS_ROOT.mkdir(parents=True)
        return

    for path in DOCS_ROOT.iterdir():
        if path.name == ".gitignore":
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def copytree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
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


def write_pages_metadata(doc_dir: Path, title: str) -> None:
    pages_file = doc_dir / ".pages"
    if pages_file.exists():
        return

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

    destination = DOCS_ROOT / repo_slug
    copytree(doc_root, destination)
    ensure_index(destination)
    write_pages_metadata(destination, title)

    temp_dir = repo_dir / ".aggregated-docs"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def sync(repos: Iterable[Tuple[str, str]]) -> None:
    reset_docs_root()
    for slug, title in repos:
        sync_repo(slug, title)

    root_pages = DOCS_ROOT / ".pages"
    nav_items = "\n".join(f"  - {slug}" for slug, _ in repos)
    root_pages.write_text(
        f"title: AngryScan\nnav:\n{nav_items}\n",
        encoding="utf-8",
    )

    default_slug, default_title = repos[0]
    redirect = DOCS_ROOT / "index.md"
    redirect.write_text(
        (
            "---\n"
            "title: Redirecting...\n"
            "hide:\n"
            "  - navigation\n"
            "  - toc\n"
            "---\n\n"
            f'<meta http-equiv="refresh" content="0; url={default_slug}/" />\n'
            "<script>"
            f'window.location.replace("{default_slug}/");'
            "</script>\n\n"
            f"If you are not redirected automatically, open [{default_title}]({default_slug}/index.md).\n"
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    sync(REPOSITORIES)


if __name__ == "__main__":
    main()
