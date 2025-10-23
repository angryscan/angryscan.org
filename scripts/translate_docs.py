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

from config_utils import get_i18n_languages, get_translation_locales, update_mkdocs_alternate_menu, update_menu_translations_json
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
CONFIG_PATH = ROOT / "scripts" / "download_config.yaml"
METADATA_CONFIG_PATH = ROOT / "scripts" / "metadata_config.yaml"

LANGUAGE_METADATA = get_i18n_languages()
TRANSLATION_LOCALES = get_translation_locales()

TRANSLATION_SUFFIXES = {locale: f".{locale}.md" for locale in TRANSLATION_LOCALES}

IGNORED_NAMES = {".gitignore", ".pages"}
IGNORED_DIRS = {".git", "__pycache__", "assets"}
FENCE_PREFIX = "```"


def load_translation_exclusions() -> dict:
    """Load translation exclusions from config file."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('translation_exclusions', {})
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def get_exclusion_config():
    """Get cached exclusion configuration."""
    if not hasattr(get_exclusion_config, '_config'):
        get_exclusion_config._config = load_translation_exclusions()
    return get_exclusion_config._config


def load_metadata_config() -> dict:
    """Load metadata configuration from metadata_config.yaml."""
    try:
        with open(METADATA_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('metadata', {})
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load metadata config: {e}")
        return {}


def get_metadata_config():
    """Get cached metadata configuration."""
    if not hasattr(get_metadata_config, '_config'):
        get_metadata_config._config = load_metadata_config()
    return get_metadata_config._config


def get_metadata_for_file(file_path: Path, language: str = None) -> dict:
    """
    Get metadata (title, description) for a specific file and language.
    
    Args:
        file_path: Path to the markdown file
        language: Target language code (e.g., 'ru', 'de'). If None, returns default metadata.
    
    Returns:
        Dictionary with 'title' and 'description' keys, or empty dict if not configured.
    """
    metadata_config = get_metadata_config()
    
    if not metadata_config.get('enabled', False):
        return {}
    
    # Get relative path from docs root
    try:
        rel_path = file_path.relative_to(DOCS_ROOT)
        file_key = str(rel_path).replace('\\', '/')
    except ValueError:
        # File is not in docs root
        return {}
    
    files_config = metadata_config.get('files', {})
    
    if file_key not in files_config:
        return {}
    
    file_metadata = files_config[file_key]
    
    # If language is specified and translations exist, use them
    if language and 'translations' in file_metadata:
        lang_metadata = file_metadata.get('translations', {}).get(language, {})
        if lang_metadata:
            return {
                'title': lang_metadata.get('title'),
                'description': lang_metadata.get('description')
            }
    
    # Return default metadata (will be auto-translated if language is specified)
    return {
        'title': file_metadata.get('title'),
        'description': file_metadata.get('description')
    }

# Async configuration
MAX_CONCURRENT_TRANSLATIONS = 10  # Increased for parallel language translation
MAX_CONCURRENT_FILES = 2  # Reduced since each file now processes multiple languages in parallel
TRANSLATION_DELAY = 0.05  # Reduced delay since we have better concurrency control

# Protected terms that should not be translated
PROTECTED_TERMS = [
    "Angry Data Scanner",
    "Angry Data Core",
    "AngryScan",
    "angryscan.org",
    "packetdima",
    "datascanner"
]

# CSS classes and HTML attributes that should not be translated
PROTECTED_CSS_CLASSES = [
    "download-container",
    "download-card",
    "download-button",
    "download-badge",
    "download-info",
    "download-name",
    "download-size",
    "no-downloads",
    "release-info",
    "release-date",
    "os-header",
    "download-content",
    "windows",
    "linux",
    "apple"
]


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


def translate_front_matter(front_matter: str, translator: GoogleTranslator, 
                          file_path: Path = None, target_lang: str = None) -> str:
    """
    Translate title and description in front matter YAML.
    
    Args:
        front_matter: The front matter YAML content
        translator: GoogleTranslator instance for translation
        file_path: Path to the source file (for metadata override lookup)
        target_lang: Target language code (for metadata override lookup)
    
    Returns:
        Translated front matter YAML content
    """
    if not front_matter:
        return front_matter
    
    import re
    
    # Get metadata overrides if available
    metadata_overrides = {}
    if file_path and target_lang:
        metadata_overrides = get_metadata_for_file(file_path, target_lang)
    
    # Parse YAML-like content to find title and description
    lines = front_matter.split('\n')
    translated_lines = []
    
    for line in lines:
        # Check if this line contains title or description
        if line.strip().startswith('title:') or line.strip().startswith('description:'):
            # Extract the key and value
            match = re.match(r'^(\s*)(title|description):\s*(.+)$', line)
            if match:
                indent = match.group(1)
                key = match.group(2)
                value = match.group(3).strip()
                
                # Check if we have an override for this field
                override_value = metadata_overrides.get(key)
                
                if override_value:
                    # Use the override value directly (no translation needed)
                    translated_value = override_value
                else:
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Protect terms before translation
                    protected_value, protected_mapping = protect_terms(value)
                    translated_value = translator.translate(protected_value)
                    # Restore protected terms after translation
                    translated_value = restore_terms(translated_value, protected_mapping)
                
                # Re-add quotes if the original had them
                if (match.group(3).strip().startswith('"') and match.group(3).strip().endswith('"')) or \
                   (match.group(3).strip().startswith("'") and match.group(3).strip().endswith("'")):
                    translated_value = f'"{translated_value}"'
                
                translated_line = f"{indent}{key}: {translated_value}"
                translated_lines.append(translated_line)
            else:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
    
    return '\n'.join(translated_lines)


def protect_backticks(text: str) -> tuple[str, dict]:
    """Replace content in backticks with placeholders and return mapping."""
    import re
    protected_mapping = {}
    protected_text = text
    
    # Find all content in backticks (but not code blocks)
    pattern = r'`([^`]*)`'
    matches = re.finditer(pattern, protected_text)
    
    for i, match in enumerate(matches):
        backtick_content = match.group(1)
        if backtick_content.strip():  # Only protect non-empty content
            placeholder = f"__PROTECTED_BACKTICK_{i}__"
            protected_mapping[placeholder] = f"`{backtick_content}`"
            protected_text = protected_text.replace(f"`{backtick_content}`", placeholder)
    
    return protected_text, protected_mapping


def protect_terms(text: str) -> tuple[str, dict]:
    """Replace protected terms with placeholders and return mapping."""
    protected_mapping = {}
    protected_text = text
    
    # Get exclusion configuration
    exclusion_config = get_exclusion_config()
    
    # Protect content in backticks first
    protected_text, backtick_mapping = protect_backticks(protected_text)
    protected_mapping.update(backtick_mapping)
    
    # Protect regular terms
    for i, term in enumerate(PROTECTED_TERMS):
        placeholder = f"__PROTECTED_TERM_{i}__"
        if term in protected_text:
            protected_mapping[placeholder] = term
            protected_text = protected_text.replace(term, placeholder)
    
    # Protect CSS classes from config
    css_classes = exclusion_config.get('css_classes', [])
    for i, css_class in enumerate(css_classes):
        placeholder = f"__PROTECTED_CSS_{i}__"
        if css_class in protected_text:
            protected_mapping[placeholder] = css_class
            protected_text = protected_text.replace(css_class, placeholder)
    
    # Protect text patterns from config
    text_patterns = exclusion_config.get('text_patterns', [])
    for i, pattern in enumerate(text_patterns):
        placeholder = f"__PROTECTED_PATTERN_{i}__"
        if pattern in protected_text:
            protected_mapping[placeholder] = pattern
            protected_text = protected_text.replace(pattern, placeholder)
    
    return protected_text, protected_mapping


def restore_terms(text: str, protected_mapping: dict) -> str:
    """Restore protected terms from placeholders."""
    restored_text = text
    for placeholder, original_term in protected_mapping.items():
        restored_text = restored_text.replace(placeholder, original_term)
    return restored_text


def translate_blocks(text: str, translator: GoogleTranslator) -> str:
    lines = text.splitlines()
    translated: List[str] = []
    buffer: List[str] = []
    in_code = False
    in_html_tag = False
    in_style_block = False

    def flush() -> None:
        if not buffer:
            return
        chunk = "\n".join(buffer)
        
        # Protect terms before translation
        protected_chunk, protected_mapping = protect_terms(chunk)
        translated_chunk = translator.translate(protected_chunk)
        # Restore protected terms after translation
        translated_chunk = restore_terms(translated_chunk, protected_mapping)
        
        translated.extend(translated_chunk.splitlines())
        buffer.clear()

    for line in lines:
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith(FENCE_PREFIX):
            flush()
            translated.append(line)
            in_code = not in_code
            continue
            
        # Handle HTML style blocks
        if stripped.startswith("<style>") or stripped.startswith("<style "):
            flush()
            translated.append(line)
            in_style_block = True
            continue
        if stripped.startswith("</style>"):
            flush()
            translated.append(line)
            in_style_block = False
            continue
            
        # Handle HTML tags - but translate text content inside them
        if "<" in line and ">" in line:
            # Get exclusion configuration
            exclusion_config = get_exclusion_config()
            excluded_elements = exclusion_config.get('html_elements', [])
            
            # Check if this is a simple HTML tag with text content that should be translated
            should_translate = False
            for tag in ["<p", "<h1", "<h2", "<h3", "<h4", "<h5", "<h6", "<span", "<div", "<a"]:
                if tag in line and tag[1:] not in excluded_elements:
                    should_translate = True
                    break
            
            if should_translate:
                # Extract text content and translate it
                import re
                # Find text content between HTML tags
                text_match = re.search(r'>([^<]+)<', line)
                if text_match:
                    text_content = text_match.group(1).strip()
                    if text_content and not any(term in text_content for term in PROTECTED_TERMS):
                        # Check if text contains excluded patterns
                        text_patterns = exclusion_config.get('text_patterns', [])
                        if not any(pattern in text_content for pattern in text_patterns):
                            # Protect terms before translation
                            protected_content, protected_mapping = protect_terms(text_content)
                            translated_content = translator.translate(protected_content)
                            # Restore protected terms after translation
                            translated_content = restore_terms(translated_content, protected_mapping)
                            # Replace the text content in the line
                            translated_line = line.replace(text_content, translated_content)
                            translated.append(translated_line)
                            continue
            flush()
            translated.append(line)
            continue
            
        # Skip code blocks, empty lines, and style blocks
        if in_code or not stripped or in_style_block or stripped.startswith("```"):
            flush()
            translated.append(line)
            continue
            
        # Handle blockquotes
        if stripped.startswith(">"):
            flush()
            quote_content = line.lstrip("> ").strip()
            # Protect terms before translation
            protected_content, protected_mapping = protect_terms(quote_content)
            translated_content = translator.translate(protected_content)
            # Restore protected terms after translation
            translated_content = restore_terms(translated_content, protected_mapping)
            translated.append("> " + translated_content)
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
        
        # Translate front matter if present (with metadata override support)
        translated_front_matter = front_matter
        if front_matter:
            translated_front_matter = translate_front_matter(
                front_matter, translator, file_path=path, target_lang=lang
            )
        
        pieces = []
        if translated_front_matter:
            pieces.append(translated_front_matter)
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
        
        # Translate front matter if present (with metadata override support)
        translated_front_matter = front_matter
        if front_matter:
            # Run front matter translation in thread pool for consistency
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                translated_front_matter = await loop.run_in_executor(
                    executor, translate_front_matter, front_matter, translator, path, lang
                )
        
        pieces = []
        if translated_front_matter:
            pieces.append(translated_front_matter)
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


async def run_async(targets: List[str], args: argparse.Namespace) -> None:
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
        
        # Update menu items automatically (unless disabled)
        if not getattr(args, 'no_menu_update', False):
            print("Updating menu items...")
            try:
                update_mkdocs_alternate_menu()
                print("Menu items updated successfully!")
            except Exception as e:
                print(f"Warning: Failed to update menu items: {e}")
            
            print("Updating menu translations...")
            try:
                update_menu_translations_json()
                print("Menu translations updated successfully!")
            except Exception as e:
                print(f"Warning: Failed to update menu translations: {e}")


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
    parser.add_argument(
        "--no-menu-update",
        action="store_true",
        help="Skip automatic menu items update.",
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
            asyncio.run(run_async(args.targets, args))


if __name__ == "__main__":
    main()
