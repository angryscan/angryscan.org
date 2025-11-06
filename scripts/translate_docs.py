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
TRANSLATION_CONFIG_PATH = ROOT / "scripts" / "translation_config.yaml"

LANGUAGE_METADATA = get_i18n_languages()
TRANSLATION_LOCALES = get_translation_locales()

# For folder structure, we don't use suffixes
TRANSLATION_SUFFIXES = {locale: f".{locale}.md" for locale in TRANSLATION_LOCALES}

IGNORED_NAMES = {".gitignore", ".pages"}
# Add language folders to ignored directories
IGNORED_DIRS = {".git", "__pycache__", "assets"} | set(TRANSLATION_LOCALES)
FENCE_PREFIX = "```"


def load_translation_exclusions() -> dict:
    """Load translation exclusions from config file."""
    # No translation exclusions config file available
    return {}


def get_exclusion_config():
    """Get cached exclusion configuration."""
    if not hasattr(get_exclusion_config, '_config'):
        get_exclusion_config._config = load_translation_exclusions()
    return get_exclusion_config._config


def load_translation_config() -> dict:
    """Load translation configuration from translation_config.yaml."""
    try:
        with open(TRANSLATION_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config or {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load translation config: {e}")
        return {}


def load_metadata_config() -> dict:
    """Load metadata configuration from translation_config.yaml."""
    config = load_translation_config()
    return config.get('metadata', {})


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
    
    # If language is specified, check for explicit translation
    if language and 'translations' in file_metadata:
        lang_metadata = file_metadata.get('translations', {}).get(language, {})
        if lang_metadata:
            # Return explicit translation for this language
            return {
                'title': lang_metadata.get('title'),
                'description': lang_metadata.get('description')
            }
        else:
            # Language specified but no explicit translation - return empty dict
            # This signals that default metadata should be auto-translated
            return {}
    
    # Return default metadata (for original files or when language is None)
    return {
        'title': file_metadata.get('title'),
        'description': file_metadata.get('description')
    }


def get_file_key(file_path: Path) -> str | None:
    """Get file key (relative path) for config lookup."""
    try:
        rel_path = file_path.relative_to(DOCS_ROOT)
        return str(rel_path).replace('\\', '/')
    except ValueError:
        return None


def get_table_config_for_file(file_path: Path) -> List[dict]:
    """Get table translation configuration for a specific file."""
    config = load_translation_config()
    if not config:
        return []
    translation_config = config.get('translation', {})
    if not translation_config:
        return []
    tables_config = translation_config.get('tables', {})
    if not tables_config:
        return []
    files_config = tables_config.get('files', {})
    if not files_config:
        return []
    
    file_key = get_file_key(file_path)
    if not file_key or file_key not in files_config:
        return []
    
    result = files_config[file_key]
    # Ensure result is a list and filter out None values
    if not isinstance(result, list):
        return []
    return [cfg for cfg in result if cfg is not None]


def get_header_config_for_file(file_path: Path) -> List[dict]:
    """Get header translation configuration for a specific file."""
    config = load_translation_config()
    if not config:
        return []
    translation_config = config.get('translation', {})
    if not translation_config:
        return []
    headers_config = translation_config.get('headers', {})
    if not headers_config:
        return []
    files_config = headers_config.get('files', {})
    if not files_config:
        return []
    
    file_key = get_file_key(file_path)
    if not file_key or file_key not in files_config:
        return []
    
    result = files_config[file_key]
    # Ensure result is a list and filter out None values
    if not isinstance(result, list):
        return []
    return [cfg for cfg in result if cfg is not None]

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
    "release-info",
    "release-date",
    "os-header",
    "windows",
    "linux",
    "apple"
]


def iter_markdown_files(root: Path) -> Iterator[Path]:
    """Iterate over markdown files in the root directory, excluding translations."""
    for path in root.rglob("*.md"):
        # Skip files with translation suffixes (legacy)
        if any(path.name.endswith(suffix) for suffix in TRANSLATION_SUFFIXES.values()):
            continue
        if path.name in IGNORED_NAMES:
            continue
        # Skip files in ignored directories (including language folders)
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        # Only process files directly in docs root or its subdirectories (not in language folders)
        try:
            rel_path = path.relative_to(root)
            # Check if the first directory component is a language code
            if len(rel_path.parts) > 1 and rel_path.parts[0] in TRANSLATION_LOCALES:
                continue
        except ValueError:
            continue
        yield path


def split_front_matter(content: str) -> tuple[str | None, str]:
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end != -1:
            end += len("\n---")
            return content[:end], content[end:].lstrip("\n")
    return None, content


def add_metadata_to_front_matter(front_matter: str, metadata: dict, lang: str = None, 
                                 translator: GoogleTranslator = None, file_path: Path = None) -> str:
    """
    Add title and description to front matter if they don't exist.
    
    Args:
        front_matter: Existing front matter string
        metadata: Metadata dict with title/description
        lang: Target language code
        translator: Translator instance (for auto-translation if needed)
        file_path: Path to file (for language-specific metadata lookup)
    
    Returns:
        Updated front matter with title/description added
    """
    if not metadata:
        return front_matter
    
    # Check if title/description already exist
    has_title = 'title:' in front_matter
    has_description = 'description:' in front_matter
    
    if has_title and has_description:
        return front_matter
    
    # Get language-specific metadata if available
    lang_metadata = {}
    if lang and file_path:
        lang_metadata = get_metadata_for_file(file_path, lang)
    
    # Parse front matter lines
    lines = front_matter.split('\n')
    new_lines = []
    title_added = has_title
    description_added = has_description
    
    # Find where to insert (after first ---, before last ---)
    first_dash_idx = -1
    last_dash_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if first_dash_idx == -1:
                first_dash_idx = i
            last_dash_idx = i
    
    # Build new front matter
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add title after first --- if not present
        if i == first_dash_idx and not title_added:
            title = None
            if lang_metadata and lang_metadata.get('title'):
                title = lang_metadata['title']
            elif metadata.get('title'):
                title = metadata['title']
                # Translate if no language-specific version
                if translator and (not lang_metadata or not lang_metadata.get('title')):
                    try:
                        title = translator.translate(title)
                    except Exception:
                        pass
            
            if title:
                new_lines.append(f"title: {title}")
                title_added = True
        
        # Add description after title (or after first --- if no title)
        if (line.strip().startswith('title:') or (i == first_dash_idx and title_added)) and not description_added:
            description = None
            if lang_metadata and lang_metadata.get('description'):
                description = lang_metadata['description']
            elif metadata.get('description'):
                description = metadata['description']
                # Translate if no language-specific version
                if translator and (not lang_metadata or not lang_metadata.get('description')):
                    try:
                        description = translator.translate(description)
                    except Exception:
                        pass
            
            if description:
                # Insert after current line (title) or after first ---
                insert_idx = len(new_lines)
                new_lines.insert(insert_idx, f"description: {description}")
                description_added = True
    
    # If still not added, add before last ---
    if not title_added and metadata.get('title'):
        title = None
        if lang_metadata and lang_metadata.get('title'):
            title = lang_metadata['title']
        elif metadata.get('title'):
            title = metadata['title']
            if translator and (not lang_metadata or not lang_metadata.get('title')):
                try:
                    title = translator.translate(title)
                except Exception:
                    pass
        
        if title and last_dash_idx >= 0:
            new_lines.insert(last_dash_idx, f"title: {title}")
            title_added = True
    
    if not description_added and metadata.get('description'):
        description = None
        if lang_metadata and lang_metadata.get('description'):
            description = lang_metadata['description']
        elif metadata.get('description'):
            description = metadata['description']
            if translator and (not lang_metadata or not lang_metadata.get('description')):
                try:
                    description = translator.translate(description)
                except Exception:
                    pass
        
        if description and last_dash_idx >= 0:
            # Find title to insert after it, or insert before last ---
            title_idx = -1
            for i, line in enumerate(new_lines):
                if line.strip().startswith('title:'):
                    title_idx = i
                    break
            
            if title_idx >= 0:
                new_lines.insert(title_idx + 1, f"description: {description}")
            else:
                new_lines.insert(last_dash_idx, f"description: {description}")
    
    return '\n'.join(new_lines)


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
    
    # Protect excluded column placeholders first (before other protections)
    import re
    # Match placeholders - use non-greedy match to get the shortest possible match
    # Pattern: __EXCLUDE_COL_<number>__<content>__EXCLUDE_COL_<same number>__
    # We need to match the content between the markers, which should not contain the closing marker
    exclude_col_pattern = r'__EXCLUDE_COL_(\d+)__(.*?)__EXCLUDE_COL_\1__'
    exclude_col_matches = list(re.finditer(exclude_col_pattern, protected_text))
    # Process matches in reverse order to preserve indices when replacing
    for i, match in enumerate(reversed(exclude_col_matches)):
        placeholder = f"__PROTECTED_EXCLUDE_COL_{len(exclude_col_matches) - 1 - i}__"
        full_match = match.group(0)
        protected_mapping[placeholder] = full_match
        # Replace from end to start to preserve positions
        start, end = match.span()
        protected_text = protected_text[:start] + placeholder + protected_text[end:]
    
    # Protect content in backticks
    protected_text, backtick_mapping = protect_backticks(protected_text)
    protected_mapping.update(backtick_mapping)
    
    # Protect regular terms
    for i, term in enumerate(PROTECTED_TERMS):
        placeholder = f"__PROTECTED_TERM_{i}__"
        if term in protected_text:
            protected_mapping[placeholder] = term
            protected_text = protected_text.replace(term, placeholder)
    
    # Protect CSS classes from config
    css_classes = exclusion_config.get('css_classes')
    if css_classes is None:
        css_classes = []
    for i, css_class in enumerate(css_classes):
        placeholder = f"__PROTECTED_CSS_{i}__"
        if css_class in protected_text:
            protected_mapping[placeholder] = css_class
            protected_text = protected_text.replace(css_class, placeholder)
    
    # Protect text patterns from config
    text_patterns = exclusion_config.get('text_patterns')
    if text_patterns is None:
        text_patterns = []
    for i, pattern in enumerate(text_patterns):
        placeholder = f"__PROTECTED_PATTERN_{i}__"
        if pattern in protected_text:
            protected_mapping[placeholder] = pattern
            protected_text = protected_text.replace(pattern, placeholder)
    
    return protected_text, protected_mapping


def restore_terms(text: str, protected_mapping: dict) -> str:
    """Restore protected terms from placeholders."""
    restored_text = text
    # Restore in reverse order to avoid conflicts (exclude_col placeholders first)
    # Sort by placeholder name to ensure consistent order
    sorted_items = sorted(protected_mapping.items(), key=lambda x: x[0], reverse=True)
    for placeholder, original_term in sorted_items:
        restored_text = restored_text.replace(placeholder, original_term)
    return restored_text


def is_table_line(line: str) -> bool:
    """Check if a line is part of a markdown table."""
    stripped = line.strip()
    # Table line should start and end with | or contain | with proper spacing
    return stripped.startswith('|') and stripped.endswith('|') and '|' in stripped[1:-1]


def parse_table_line(line: str) -> List[str]:
    """Parse a table line into columns."""
    # Split by | and strip whitespace, remove empty first/last if they exist
    parts = [part.strip() for part in line.split('|')]
    # Remove empty parts at start/end (from leading/trailing |)
    if parts and not parts[0]:
        parts = parts[1:]
    if parts and not parts[-1]:
        parts = parts[:-1]
    return parts


def find_table_ranges(lines: List[str]) -> List[Tuple[int, int]]:
    """
    Find all table ranges in lines.
    Returns list of (start_index, end_index) tuples.
    """
    table_ranges = []
    i = 0
    while i < len(lines):
        if is_table_line(lines[i]):
            start = i
            # Find the end of the table
            i += 1
            while i < len(lines) and is_table_line(lines[i]):
                i += 1
            end = i
            # Only include if we have at least 2 lines (header + separator)
            if end - start >= 2:
                table_ranges.append((start, end))
        else:
            i += 1
    return table_ranges


def find_headers_with_numbers(lines: List[str]) -> Tuple[dict, dict]:
    """
    Find all h1 and h2 headers and assign numbers.
    Returns (h1_dict, h2_dict) where:
    - h1_dict: {number: (index, text)}
    - h2_dict: {h1_number: {h2_number: (index, text)}}
    """
    h1_dict = {}
    h2_dict = {}
    h1_counter = 0
    h2_counters = {}  # Track h2 counters per h1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# '):
            h1_counter += 1
            h1_dict[h1_counter] = (i, stripped)
            h2_counters[h1_counter] = 0
        elif stripped.startswith('## '):
            # Find which h1 this h2 belongs to
            current_h1 = h1_counter
            if current_h1 > 0:
                if current_h1 not in h2_dict:
                    h2_dict[current_h1] = {}
                h2_counters[current_h1] += 1
                h2_number = h2_counters[current_h1]
                h2_dict[current_h1][h2_number] = (i, stripped)
    
    return h1_dict, h2_dict


def get_table_config_by_header(table_configs: List[dict], header_text: str) -> dict | None:
    """Find table config by matching header text."""
    for config in table_configs:
        if config.get('match_by_header') == header_text:
            return config
    return None


def get_table_config_by_number(table_configs: List[dict], table_number: int) -> dict | None:
    """Find table config by table number."""
    for config in table_configs:
        if config.get('table_number') == table_number:
            return config
    return None


def get_header_translation(header_configs: List[dict], header_text: str, header_level: int,
                          h1_number: int | None = None, h2_number: int | None = None,
                          language: str = None) -> str | None:
    """
    Get manual translation for a header.
    
    Args:
        header_configs: List of header configs from file
        header_text: The header text to match
        header_level: 1 for h1, 2 for h2
        h1_number: H1 number (for h2 identification)
        h2_number: H2 number within parent h1 (for h2 identification)
        language: Target language code
    
    Returns:
        Translated header text or None if not found
    """
    if not language:
        return None
    
    for config in header_configs:
        if config.get('level') != header_level:
            continue
        
        # Check if this config matches
        matched = False
        
        if header_level == 1:
            # H1: match by text or number
            if 'text' in config and config['text'] == header_text:
                matched = True
            elif 'number' in config:
                # Need to find h1 number from context - this will be handled by caller
                pass
        elif header_level == 2:
            # H2: match by text or by parent_h1_number + number
            if 'text' in config and config['text'] == header_text:
                matched = True
            elif h1_number and h2_number:
                if config.get('parent_h1_number') == h1_number and config.get('number') == h2_number:
                    matched = True
        
        if matched and 'translations' in config:
            return config['translations'].get(language)
    
    return None


def process_table_line(line: str, exclude_columns: List[int] = None, 
                      exclude_header: bool = False, is_header_row: bool = False) -> str:
    """
    Process a table line by excluding specified columns from translation.
    
    Args:
        line: The table line to process
        exclude_columns: List of column indices (1-based) to exclude
        exclude_header: Whether to exclude the header row from translation
        is_header_row: Whether this is the header row
    
    Returns:
        Processed line with excluded columns replaced by placeholders
    """
    if not exclude_columns or exclude_columns is None:
        return line
    
    # Always process columns if exclude_columns is specified, regardless of is_header_row
    # exclude_header only affects whether the header row gets translated, not column exclusion
    
    columns = parse_table_line(line)
    if not columns:
        return line
    
    # Create placeholders for excluded columns
    processed_columns = []
    for i, col in enumerate(columns):
        col_index = i + 1  # 1-based index
        if exclude_columns and col_index in exclude_columns:
            # Replace with placeholder that won't be translated
            placeholder = f"__EXCLUDE_COL_{col_index}__{col}__EXCLUDE_COL_{col_index}__"
            processed_columns.append(placeholder)
        else:
            processed_columns.append(col)
    
    # Reconstruct table line
    return '| ' + ' | '.join(processed_columns) + ' |'


def restore_table_line(line: str) -> str:
    """Restore excluded columns in a table line after translation."""
    import re
    # Pattern: __EXCLUDE_COL_N__content__EXCLUDE_COL_N__
    # Use non-greedy match to get the shortest possible match
    # The pattern should match: __EXCLUDE_COL_<number>__<any content>__EXCLUDE_COL_<same number>__
    pattern = r'__EXCLUDE_COL_(\d+)__(.*?)__EXCLUDE_COL_\1__'
    
    def replace_placeholder(match):
        col_num = match.group(1)
        content = match.group(2)
        return content
    
    result = re.sub(pattern, replace_placeholder, line)
    return result


def translate_blocks(text: str, translator: GoogleTranslator, file_path: Path = None, language: str = None) -> str:
    """
    Translate markdown blocks with support for table/column exclusions and manual header translations.
    
    Args:
        text: The text to translate
        translator: GoogleTranslator instance
        file_path: Path to the source file (for config lookup)
        language: Target language code (for header translations)
    """
    lines = text.splitlines()
    
    # Get configurations for tables and headers
    table_configs = get_table_config_for_file(file_path) if file_path else []
    header_configs = get_header_config_for_file(file_path) if file_path else []
    
    # Find headers with numbers for identification
    h1_dict, h2_dict = find_headers_with_numbers(lines)
    
    # Find table ranges
    table_ranges = find_table_ranges(lines)
    
    # Map table numbers and find preceding headers for each table
    table_info = {}  # {table_index: (table_number, preceding_header, config)}
    table_counter = 0
    for start, end in table_ranges:
        table_counter += 1
        # Find preceding header (look backwards from table start)
        # Look for h2 (##) or h3 (###) headers
        preceding_header = None
        for i in range(start - 1, -1, -1):
            if i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith('### '):
                    preceding_header = stripped
                    break
                elif stripped.startswith('## '):
                    preceding_header = stripped
                    break
                elif stripped.startswith('# '):
                    # Stop at h1, don't use it
                    break
        
        table_info[table_counter] = (start, end, preceding_header)
    
    # Process headers - replace with manual translations
    processed_lines = lines.copy()
    
    # Process h1 headers
    for h1_num, (idx, h1_text) in h1_dict.items():
        manual_trans = None
        # First check for manual translation by text
        for config in header_configs:
            if config and config.get('level') == 1:
                translations = config.get('translations')
                if translations is None:
                    translations = {}
                if config.get('text') == h1_text:
                    manual_trans = translations.get(language) if isinstance(translations, dict) else None
                    if manual_trans:
                        break
                elif config.get('number') == h1_num:
                    manual_trans = translations.get(language) if isinstance(translations, dict) else None
                    if manual_trans:
                        break
        
        if manual_trans:
            processed_lines[idx] = manual_trans
    
    # Process h2 headers
    for h1_num, h2_dict_inner in h2_dict.items():
        for h2_num, (idx, h2_text) in h2_dict_inner.items():
            manual_trans = None
            # First check for manual translation by text
            for config in header_configs:
                if config and config.get('level') == 2:
                    translations = config.get('translations')
                    if translations is None:
                        translations = {}
                    if config.get('text') == h2_text:
                        manual_trans = translations.get(language) if isinstance(translations, dict) else None
                        if manual_trans:
                            break
                    elif (config.get('parent_h1_number') == h1_num and 
                          config.get('number') == h2_num):
                        manual_trans = translations.get(language) if isinstance(translations, dict) else None
                        if manual_trans:
                            break
            
            if manual_trans:
                processed_lines[idx] = manual_trans
    
    # Store original lines for excluded tables
    original_lines = lines.copy()
    
    # Process tables - apply exclusions
    for table_num, (start, end, preceding_header) in table_info.items():
        # Find matching config
        table_config = None
        if preceding_header:
            table_config = get_table_config_by_header(table_configs, preceding_header)
        if not table_config:
            table_config = get_table_config_by_number(table_configs, table_num)
        
        if table_config:
            # Check if entire table should be excluded
            if table_config.get('exclude_table'):
                # Replace table with placeholders that include original line index
                for i in range(start, end):
                    processed_lines[i] = f"__EXCLUDE_TABLE_LINE_{i}__"
            else:
                # Process columns
                exclude_columns = table_config.get('exclude_columns')
                if exclude_columns is None:
                    exclude_columns = []
                exclude_header = table_config.get('exclude_header', False)
                
                if exclude_columns:
                    # Process table lines
                    for i in range(start, end):
                        line = processed_lines[i]
                        # Check if this is separator row (second row, typically contains dashes)
                        is_separator = (i == start + 1 and 
                                       ('---' in line or all(c in '-:| ' for c in line.strip())))
                        is_header_row = i == start
                        
                        if is_separator:
                            # Don't modify separator row
                            continue
                        elif is_header_row:
                            # If exclude_header is False, header should be translated
                            # But excluded columns should NOT be translated
                            if not exclude_header:
                                # Mark this as a header that should be translated (even if all columns are excluded)
                                # We'll use a special marker to identify header rows during translation
                                processed_line = process_table_line(line, exclude_columns, exclude_header, True)
                                # Mark as header that should be translated (but not excluded)
                                processed_line = f"__TRANSLATE_HEADER__{processed_line}__TRANSLATE_HEADER__"
                            else:
                                # exclude_header is True, just process normally and mark to skip translation
                                processed_line = process_table_line(line, exclude_columns, exclude_header, True)
                                processed_line = f"__EXCLUDE_HEADER__{processed_line}__EXCLUDE_HEADER__"
                            processed_lines[i] = processed_line
                        else:
                            processed_lines[i] = process_table_line(line, exclude_columns, exclude_header, False)
    
    # Now translate the processed lines
    # Store original lines for excluded table restoration
    original_lines_for_translation = lines.copy()
    lines = processed_lines
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
        try:
            translated_chunk = translator.translate(protected_chunk)
        except Exception as e:
            # If translation fails, use original chunk
            print(f"Warning: Translation failed: {e}")
            translated_chunk = protected_chunk
        
        # Ensure translated_chunk is not None
        if translated_chunk is None:
            translated_chunk = protected_chunk
        
        # Restore protected terms after translation
        translated_chunk = restore_terms(translated_chunk, protected_mapping)
        
        # Ensure translated_chunk is still not None and is a string
        if translated_chunk is None:
            translated_chunk = chunk
        
        # Split and filter out None values
        lines = translated_chunk.splitlines()
        translated.extend([line for line in lines if line is not None])
        buffer.clear()

    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle excluded table lines (entire table excluded)
        if stripped.startswith("__EXCLUDE_TABLE_LINE_"):
            # Restore original line from original lines
            # Extract index from placeholder: __EXCLUDE_TABLE_LINE_{idx}__
            try:
                idx_str = stripped.replace("__EXCLUDE_TABLE_LINE_", "").replace("__", "")
                original_idx = int(idx_str)
                if original_idx < len(original_lines_for_translation):
                    translated.append(original_lines_for_translation[original_idx])
                else:
                    translated.append(line)
            except (ValueError, IndexError):
                translated.append(line)
            continue
        
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
            excluded_elements = exclusion_config.get('html_elements')
            if excluded_elements is None:
                excluded_elements = []
            
            # Check if this is a simple HTML tag with text content that should be translated
            should_translate = False
            for tag in ["<p", "<h1", "<h2", "<h3", "<h4", "<h5", "<h6", "<span", "<div", "<a"]:
                if tag in line and (not excluded_elements or tag[1:] not in excluded_elements):
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
                        text_patterns = exclusion_config.get('text_patterns')
                        if text_patterns is None:
                            text_patterns = []
                        if not text_patterns or not any(pattern in text_content for pattern in text_patterns):
                            # Protect terms before translation
                            protected_content, protected_mapping = protect_terms(text_content)
                            try:
                                translated_content = translator.translate(protected_content)
                            except Exception as e:
                                print(f"Warning: Translation failed for HTML content: {e}")
                                translated_content = protected_content
                            
                            # Ensure translated_content is not None
                            if translated_content is None:
                                translated_content = protected_content
                            
                            # Restore protected terms after translation
                            translated_content = restore_terms(translated_content, protected_mapping)
                            
                            # Ensure final content is not None
                            if translated_content is not None:
                                # Replace the text content in the line
                                translated_line = line.replace(text_content, translated_content)
                                translated.append(translated_line)
                            else:
                                translated.append(line)
                            continue
            flush()
            translated.append(line)
            continue
        
        # Handle table lines (with column exclusions)
        # Note: Table lines are processed individually to preserve structure
        # but we still use buffer for efficiency when possible
        if is_table_line(line) or (line.startswith("__EXCLUDE_HEADER__") and line.endswith("__EXCLUDE_HEADER__")) or \
           (line.startswith("__TRANSLATE_HEADER__") and line.endswith("__TRANSLATE_HEADER__")):
            flush()
            # Check if this is a header that should be excluded from translation
            if line.startswith("__EXCLUDE_HEADER__") and line.endswith("__EXCLUDE_HEADER__"):
                # Remove the markers and restore excluded columns without translation
                line_without_markers = line.replace("__EXCLUDE_HEADER__", "")
                translated_line = restore_table_line(line_without_markers)
                translated.append(translated_line)
                continue
            
            # Check if this is a header that should be translated (even if all columns are excluded)
            is_translate_header = line.startswith("__TRANSLATE_HEADER__") and line.endswith("__TRANSLATE_HEADER__")
            if is_translate_header:
                # Remove the markers first
                line_without_markers = line.replace("__TRANSLATE_HEADER__", "")
                # Now process as normal table line with excluded columns
                # This will translate non-excluded columns and preserve excluded ones
                line = line_without_markers
            
            # Check if this line has excluded columns (has placeholders)
            if "__EXCLUDE_COL_" in line:
                # First, extract content from placeholders to check if we need to translate it
                # This is needed for header rows when exclude_header is not set
                import re
                exclude_col_pattern = r'__EXCLUDE_COL_(\d+)__(.*?)__EXCLUDE_COL_\1__'
                placeholder_matches = list(re.finditer(exclude_col_pattern, line))
                
                # If line contains only placeholders (all columns excluded), we need special handling
                # Check if there's any non-placeholder content
                line_without_placeholders = line
                for match in placeholder_matches:
                    line_without_placeholders = line_without_placeholders.replace(match.group(0), "")
                # Remove table separators and whitespace
                line_without_placeholders = line_without_placeholders.replace("|", "").strip()
                
                # If line is only placeholders and separators, we need special handling
                # This can happen when all columns are excluded
                # For headers that should be translated (is_translate_header), we need to translate
                # But excluded columns should NOT be translated, so we just restore them
                if not line_without_placeholders and placeholder_matches:
                    # This is a line with only excluded columns (placeholders)
                    # For headers that should be translated, we still need to go through translation
                    # to ensure the structure is preserved, but excluded columns will remain unchanged
                    if is_translate_header:
                        # For headers that should be translated, we still translate the line
                        # (even though it only has placeholders) to ensure structure is preserved
                        # The excluded columns will be restored unchanged
                        protected_line, protected_mapping = protect_terms(line)
                        try:
                            translated_line = translator.translate(protected_line)
                        except Exception as e:
                            translated_line = protected_line
                        if translated_line is None:
                            translated_line = protected_line
                        translated_line = restore_terms(translated_line, protected_mapping)
                        translated_line = restore_table_line(translated_line)
                        translated.append(translated_line)
                        continue
                    else:
                        # For non-header lines or headers with exclude_header=True, just restore
                        restored_line = restore_table_line(line)
                        translated.append(restored_line)
                        continue
                
                # Normal case: line has both placeholders and translatable content
                # Translate the line, then restore excluded columns
                # First protect the excluded column placeholders
                protected_line, protected_mapping = protect_terms(line)
                
                # Check if there's any translatable content left (not just placeholders)
                # If the line is only placeholders and separators, we still need to translate it
                # to ensure the structure is preserved, but the placeholders will be restored
                try:
                    translated_line = translator.translate(protected_line)
                except Exception as e:
                    # If translation fails, use original line
                    print(f"Warning: Translation failed for table line: {e}")
                    translated_line = protected_line
                
                # Ensure translated_line is not None
                if translated_line is None:
                    translated_line = protected_line
                
                # Restore protected terms (including excluded column placeholders)
                translated_line = restore_terms(translated_line, protected_mapping)
                # Restore excluded columns (extract content from placeholders)
                translated_line = restore_table_line(translated_line)
                
                # Ensure final line is not None
                if translated_line is not None:
                    translated.append(translated_line)
                else:
                    translated.append(line)
            else:
                # Normal table line - translate it
                protected_line, protected_mapping = protect_terms(line)
                try:
                    translated_line = translator.translate(protected_line)
                except Exception as e:
                    # If translation fails, use original line
                    print(f"Warning: Translation failed for table line: {e}")
                    translated_line = protected_line
                
                # Ensure translated_line is not None
                if translated_line is None:
                    translated_line = protected_line
                
                translated_line = restore_terms(translated_line, protected_mapping)
                
                # Ensure final line is not None
                if translated_line is not None:
                    translated.append(translated_line)
                else:
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
            try:
                translated_content = translator.translate(protected_content)
            except Exception as e:
                print(f"Warning: Translation failed for blockquote: {e}")
                translated_content = protected_content
            
            # Ensure translated_content is not None
            if translated_content is None:
                translated_content = protected_content
            
            # Restore protected terms after translation
            translated_content = restore_terms(translated_content, protected_mapping)
            
            # Ensure final content is not None
            if translated_content is not None:
                translated.append("> " + translated_content)
            else:
                translated.append(line)
            continue
            
        buffer.append(line)

    flush()
    # Filter out any None values before joining
    translated = [line for line in translated if line is not None]
    return "\n".join(translated)


async def translate_blocks_async(text: str, translator: GoogleTranslator, semaphore: asyncio.Semaphore,
                                 file_path: Path = None, language: str = None) -> str:
    """Async version of translate_blocks with rate limiting."""
    async with semaphore:
        # Run the synchronous translation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, translate_blocks, text, translator, file_path, language
            )
        await asyncio.sleep(TRANSLATION_DELAY)  # Rate limiting
        return result


def translate_file(path: Path, targets: Iterable[str]) -> None:
    content = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(content)

    for lang in targets:
        suffix = TRANSLATION_SUFFIXES.get(lang, f".{lang}.md")
        translator = GoogleTranslator(source="auto", target=lang)
        translated_body = translate_blocks(body, translator, file_path=path, language=lang)
        
        # Translate front matter if present (with metadata override support)
        translated_front_matter = front_matter
        if front_matter:
            # Check if front matter has title or description
            has_title = 'title:' in front_matter
            has_description = 'description:' in front_matter
            
            # If front matter exists but lacks title/description, add metadata
            if not has_title or not has_description:
                metadata = get_metadata_for_file(path, None)  # Get default metadata
                if metadata:
                    translated_front_matter = add_metadata_to_front_matter(
                        front_matter, metadata, lang=lang, translator=translator, file_path=path
                    )
                else:
                    # No metadata, just translate existing front matter
                    translated_front_matter = translate_front_matter(
                        front_matter, translator, file_path=path, target_lang=lang
                    )
            else:
                # Front matter has title/description, just translate it
                translated_front_matter = translate_front_matter(
                    front_matter, translator, file_path=path, target_lang=lang
                )
        else:
            # If no front matter exists, create one with metadata if available
            metadata = get_metadata_for_file(path, None)  # Get default metadata
            if metadata and (metadata.get('title') or metadata.get('description')):
                front_matter_lines = ["---"]
                # Get language-specific metadata if available
                lang_metadata = get_metadata_for_file(path, lang) if lang else {}
                
                if lang_metadata and lang_metadata.get('title'):
                    front_matter_lines.append(f"title: {lang_metadata['title']}")
                elif metadata.get('title'):
                    # Translate default title if no language-specific version
                    if not lang_metadata or not lang_metadata.get('title'):
                        try:
                            translated_title = translator.translate(metadata['title'])
                            front_matter_lines.append(f"title: {translated_title}")
                        except Exception:
                            front_matter_lines.append(f"title: {metadata['title']}")
                    else:
                        front_matter_lines.append(f"title: {metadata['title']}")
                
                if lang_metadata and lang_metadata.get('description'):
                    front_matter_lines.append(f"description: {lang_metadata['description']}")
                elif metadata.get('description'):
                    # Translate default description if no language-specific version
                    if not lang_metadata or not lang_metadata.get('description'):
                        try:
                            translated_description = translator.translate(metadata['description'])
                            front_matter_lines.append(f"description: {translated_description}")
                        except Exception:
                            front_matter_lines.append(f"description: {metadata['description']}")
                    else:
                        front_matter_lines.append(f"description: {metadata['description']}")
                
                front_matter_lines.append("---")
                translated_front_matter = "\n".join(front_matter_lines)
        
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
        translated_body = await translate_blocks_async(body, translator, semaphore, file_path=path, language=lang)
        
        # Translate front matter if present (with metadata override support)
        translated_front_matter = front_matter
        if front_matter:
            # Check if front matter has title or description
            has_title = 'title:' in front_matter
            has_description = 'description:' in front_matter
            
            # If front matter exists but lacks title/description, add metadata
            if not has_title or not has_description:
                metadata = get_metadata_for_file(path, None)  # Get default metadata
                if metadata:
                    # Run add_metadata_to_front_matter in thread pool
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        translated_front_matter = await loop.run_in_executor(
                            executor, add_metadata_to_front_matter, 
                            front_matter, metadata, lang, translator, path
                        )
                else:
                    # No metadata, just translate existing front matter
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        translated_front_matter = await loop.run_in_executor(
                            executor, translate_front_matter, front_matter, translator, path, lang
                        )
            else:
                # Front matter has title/description, just translate it
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    translated_front_matter = await loop.run_in_executor(
                        executor, translate_front_matter, front_matter, translator, path, lang
                    )
        else:
            # If no front matter exists, create one with metadata if available
            metadata = get_metadata_for_file(path, None)  # Get default metadata
            if metadata and (metadata.get('title') or metadata.get('description')):
                front_matter_lines = ["---"]
                # Get language-specific metadata if available
                lang_metadata = get_metadata_for_file(path, lang) if lang else {}
                
                if lang_metadata and lang_metadata.get('title'):
                    front_matter_lines.append(f"title: {lang_metadata['title']}")
                elif metadata.get('title'):
                    # Translate default title if no language-specific version
                    if not lang_metadata or not lang_metadata.get('title'):
                        try:
                            translated_title = translator.translate(metadata['title'])
                            front_matter_lines.append(f"title: {translated_title}")
                        except Exception:
                            front_matter_lines.append(f"title: {metadata['title']}")
                    else:
                        front_matter_lines.append(f"title: {metadata['title']}")
                
                if lang_metadata and lang_metadata.get('description'):
                    front_matter_lines.append(f"description: {lang_metadata['description']}")
                elif metadata.get('description'):
                    # Translate default description if no language-specific version
                    if not lang_metadata or not lang_metadata.get('description'):
                        try:
                            translated_description = translator.translate(metadata['description'])
                            front_matter_lines.append(f"description: {translated_description}")
                        except Exception:
                            front_matter_lines.append(f"description: {metadata['description']}")
                    else:
                        front_matter_lines.append(f"description: {metadata['description']}")
                
                front_matter_lines.append("---")
                translated_front_matter = "\n".join(front_matter_lines)
        
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


def add_metadata_to_original_files() -> None:
    """Add metadata to original markdown files before translation."""
    metadata_config = get_metadata_config()
    
    if not metadata_config.get('enabled', False):
        return
    
    for md_file in iter_markdown_files(DOCS_ROOT):
        content = md_file.read_text(encoding="utf-8")
        front_matter, body = split_front_matter(content)
        
        # Get metadata for this file
        metadata = get_metadata_for_file(md_file, None)
        if not metadata or (not metadata.get('title') and not metadata.get('description')):
            continue
        
        # Check if front matter has title or description
        has_title = front_matter and 'title:' in front_matter if front_matter else False
        has_description = front_matter and 'description:' in front_matter if front_matter else False
        
        # If both exist, skip
        if has_title and has_description:
            continue
        
        # Add metadata to front matter
        if front_matter:
            updated_front_matter = add_metadata_to_front_matter(
                front_matter, metadata, lang=None, translator=None, file_path=md_file
            )
        else:
            # Create new front matter
            front_matter_lines = ["---"]
            if metadata.get('title'):
                front_matter_lines.append(f"title: {metadata['title']}")
            if metadata.get('description'):
                front_matter_lines.append(f"description: {metadata['description']}")
            front_matter_lines.append("---")
            updated_front_matter = "\n".join(front_matter_lines)
        
        # Write updated content
        pieces = []
        if updated_front_matter:
            pieces.append(updated_front_matter)
            pieces.append("")
        pieces.append(body)
        md_file.write_text("\n".join(pieces).strip() + "\n", encoding="utf-8")


def build_translation_path(path: Path, suffix: str) -> Path:
    """
    Build path for translated file using folder structure.
    
    For folder structure:
    docs/index.md -> docs/ru/index.md
    docs/subdir/page.md -> docs/ru/subdir/page.md
    """
    # Extract language code from suffix (e.g., ".ru.md" -> "ru")
    lang_code = suffix.split('.')[1] if '.' in suffix else suffix
    
    # Get relative path from docs root
    try:
        rel_path = path.relative_to(DOCS_ROOT)
    except ValueError:
        # If path is not relative to docs root, fall back to old behavior
        return path.with_name(f"{path.stem}{suffix}")
    
    # Build new path: docs/lang_code/original_relative_path
    translated_path = DOCS_ROOT / lang_code / rel_path
    
    # Create parent directory if it doesn't exist
    translated_path.parent.mkdir(parents=True, exist_ok=True)
    
    return translated_path


def run(targets: Iterable[str]) -> None:
    targets = list(targets)
    if not targets:
        return
    DOCS_ROOT.mkdir(exist_ok=True)
    # Add metadata to original files before translation
    add_metadata_to_original_files()
    for md_file in iter_markdown_files(DOCS_ROOT):
        translate_file(md_file, targets)


async def run_async(targets: List[str], args: argparse.Namespace) -> None:
    """Async version of run with progress tracking and concurrent processing."""
    if not targets:
        return
    
    DOCS_ROOT.mkdir(exist_ok=True)
    
    # Add metadata to original files before translation
    add_metadata_to_original_files()
    
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
