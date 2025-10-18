#!/usr/bin/env python3
"""Generate machine translations of aggregated documentation."""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
from typing import Iterable, Iterator, List

from deep_translator import GoogleTranslator

from config_utils import get_i18n_languages, get_translation_locales

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"

LANGUAGE_METADATA = get_i18n_languages()
TRANSLATION_LOCALES = get_translation_locales()

TRANSLATION_SUFFIXES = {locale: f".{locale}.md" for locale in TRANSLATION_LOCALES}

IGNORED_NAMES = {".gitignore", ".pages"}
IGNORED_DIRS = {".git", "__pycache__", "assets"}
FENCE_PREFIX = "```"


def iter_markdown_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.md"):
        if any(path.name.endswith(suffix) for suffix in TRANSLATION_SUFFIXES.values()):
            continue
        if path.name in IGNORED_NAMES:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def split_front_matter(content: str) -> tuple[str | None, str]:
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end != -1:
            end += len("\n---")
            return content[:end], content[end:].lstrip("\n")
    return None, content


def translate_blocks(text: str, translator: GoogleTranslator) -> str:
    lines = text.splitlines()
    translated: List[str] = []
    buffer: List[str] = []
    in_code = False

    def flush() -> None:
        if not buffer:
            return
        chunk = "\n".join(buffer)
        translated_chunk = translator.translate(chunk)
        translated.extend(translated_chunk.splitlines())
        buffer.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(FENCE_PREFIX):
            flush()
            translated.append(line)
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("```"):
            flush()
            translated.append(line)
            continue
        if stripped.startswith(">"):
            flush()
            translated_line = translator.translate(line.lstrip("> ").strip())
            translated.append("> " + translated_line)
            continue
        buffer.append(line)

    flush()
    return "\n".join(translated)


def translate_file(path: Path, targets: Iterable[str]) -> None:
    content = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(content)

    for lang in targets:
        suffix = TRANSLATION_SUFFIXES.get(lang, f".{lang}.md")
        translator = GoogleTranslator(source="auto", target=lang)
        translated_body = translate_blocks(body, translator)
        pieces = []
        if front_matter:
            pieces.append(front_matter)
            pieces.append("")
        pieces.append(translated_body)
        output_path = build_translation_path(path, suffix)
        output_path.write_text("\n".join(pieces).strip() + "\n", encoding="utf-8")


def build_translation_path(path: Path, suffix: str) -> Path:
    base_name = path.name
    if base_name.endswith(".markdown"):
        core = base_name[: -len(".markdown")]
        return path.with_name(f"{core}{suffix[:-3]}.markdown")
    if base_name.endswith(".md"):
        core = base_name[: -len(".md")]
        return path.with_name(f"{core}{suffix}")
    return path.with_name(f"{base_name}{suffix}")


def run(targets: Iterable[str]) -> None:
    targets = list(targets)
    if not targets:
        return
    DOCS_ROOT.mkdir(exist_ok=True)
    for md_file in iter_markdown_files(DOCS_ROOT):
        translate_file(md_file, targets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--targets",
        nargs="+",
        default=TRANSLATION_LOCALES,
        help="Language codes to translate into (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with contextlib.ExitStack():
        run(args.targets)


if __name__ == "__main__":
    main()
