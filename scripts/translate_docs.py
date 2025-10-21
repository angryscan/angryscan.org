#!/usr/bin/env python3
"""Generate machine translations of aggregated documentation."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import time
from pathlib import Path
from typing import Iterable, Iterator, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import aiofiles

from deep_translator import GoogleTranslator
from tqdm.asyncio import tqdm

from config_utils import get_i18n_languages, get_translation_locales

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"

LANGUAGE_METADATA = get_i18n_languages()
TRANSLATION_LOCALES = get_translation_locales()

TRANSLATION_SUFFIXES = {locale: f".{locale}.md" for locale in TRANSLATION_LOCALES}

IGNORED_NAMES = {".gitignore", ".pages"}
IGNORED_DIRS = {".git", "__pycache__", "assets"}
FENCE_PREFIX = "```"

# Async configuration
MAX_CONCURRENT_TRANSLATIONS = 10  # Increased for parallel language translation
MAX_CONCURRENT_FILES = 2  # Reduced since each file now processes multiple languages in parallel
TRANSLATION_DELAY = 0.05  # Reduced delay since we have better concurrency control


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


async def translate_blocks_async(text: str, translator: GoogleTranslator, semaphore: asyncio.Semaphore) -> str:
    """Async version of translate_blocks with rate limiting."""
    async with semaphore:
        # Run the synchronous translation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, translate_blocks, text, translator)
        await asyncio.sleep(TRANSLATION_DELAY)  # Rate limiting
        return result


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


async def translate_single_language(path: Path, lang: str, body: str, front_matter: str | None, 
                                   semaphore: asyncio.Semaphore, progress_bar: tqdm) -> None:
    """Translate a single file to a single language."""
    try:
        suffix = TRANSLATION_SUFFIXES.get(lang, f".{lang}.md")
        translator = GoogleTranslator(source="auto", target=lang)
        translated_body = await translate_blocks_async(body, translator, semaphore)
        
        pieces = []
        if front_matter:
            pieces.append(front_matter)
            pieces.append("")
        pieces.append(translated_body)
        output_path = build_translation_path(path, suffix)
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write("\n".join(pieces).strip() + "\n")
        
        progress_bar.set_description(f"Translated {path.name} to {lang}")
        progress_bar.update(1)
        
    except Exception as e:
        print(f"Error translating {path.name} to {lang}: {e}")
        progress_bar.update(1)


async def translate_file_async(path: Path, targets: List[str], semaphore: asyncio.Semaphore, progress_bar: tqdm) -> None:
    """Async version of translate_file with parallel language translation."""
    try:
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        front_matter, body = split_front_matter(content)
        
        # Create tasks for all language translations to run in parallel
        tasks = []
        for lang in targets:
            task = translate_single_language(path, lang, body, front_matter, semaphore, progress_bar)
            tasks.append(task)
        
        # Execute all language translations concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
                
    except Exception as e:
        print(f"Error processing file {path}: {e}")
        progress_bar.update(len(targets))


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


async def run_async(targets: List[str]) -> None:
    """Async version of run with progress tracking and concurrent processing."""
    if not targets:
        return
    
    DOCS_ROOT.mkdir(exist_ok=True)
    
    # Collect all markdown files
    md_files = list(iter_markdown_files(DOCS_ROOT))
    if not md_files:
        print("No markdown files found to translate.")
        return
    
    # Calculate total operations (files * languages)
    total_operations = len(md_files) * len(targets)
    
    print(f"Starting translation of {len(md_files)} files to {len(targets)} languages...")
    print(f"Total operations: {total_operations}")
    print(f"Using {MAX_CONCURRENT_TRANSLATIONS} concurrent translations with {MAX_CONCURRENT_FILES} concurrent files")
    print(f"Each file will be translated to all languages in parallel for maximum speed")
    
    # Create semaphores for rate limiting
    translation_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TRANSLATIONS)
    file_semaphore = asyncio.Semaphore(MAX_CONCURRENT_FILES)
    
    # Create progress bar
    progress_bar = tqdm(total=total_operations, desc="Translating", unit="ops")
    
    start_time = time.time()
    
    try:
        # Process files in batches to avoid overwhelming the system
        batch_size = MAX_CONCURRENT_FILES
        for i in range(0, len(md_files), batch_size):
            batch = md_files[i:i + batch_size]
            
            # Create tasks for this batch
            tasks = []
            for md_file in batch:
                task = translate_file_async(md_file, targets, translation_semaphore, progress_bar)
                tasks.append(task)
            
            # Wait for this batch to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay between batches
            if i + batch_size < len(md_files):
                await asyncio.sleep(0.5)
    
    except Exception as e:
        print(f"Error during translation: {e}")
    
    finally:
        progress_bar.close()
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nTranslation completed in {duration:.2f} seconds")
        print(f"Average time per operation: {duration/total_operations:.2f} seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--targets",
        nargs="+",
        default=TRANSLATION_LOCALES,
        help="Language codes to translate into (default: %(default)s).",
    )
    parser.add_argument(
        "--max-concurrent-translations",
        type=int,
        default=MAX_CONCURRENT_TRANSLATIONS,
        help=f"Maximum concurrent translations (default: {MAX_CONCURRENT_TRANSLATIONS}).",
    )
    parser.add_argument(
        "--max-concurrent-files",
        type=int,
        default=MAX_CONCURRENT_FILES,
        help=f"Maximum concurrent files (default: {MAX_CONCURRENT_FILES}).",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Use synchronous processing instead of async (slower but more reliable).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Update global constants based on command line arguments
    global MAX_CONCURRENT_TRANSLATIONS, MAX_CONCURRENT_FILES
    MAX_CONCURRENT_TRANSLATIONS = args.max_concurrent_translations
    MAX_CONCURRENT_FILES = args.max_concurrent_files
    
    with contextlib.ExitStack():
        if args.sync:
            print("Using synchronous processing...")
            run(args.targets)
        else:
            print("Using asynchronous processing...")
            asyncio.run(run_async(args.targets))


if __name__ == "__main__":
    main()
