---
hide:
  - navigation
  - toc
  - navigation
  - toc
  - navigation
  - toc
  - navigation
  - toc
---
# Metadata Configuration for .md Files

This document describes the functionality for configuring custom title and description for .md files in the project.

## Overview

The functionality allows configuring metadata (title and description) for markdown files through YAML configuration. Metadata is applied automatically when running `sync_docs.py`.

## Configuration File

Configuration is stored in `scripts/metadata_config.yaml`:

```yaml
# Configuration for custom metadata (title and description) for .md files
metadata:
  # Global settings
  enabled: true

  # File-specific metadata configuration
  files:
    # Example configurations for different files
    # Path is relative to docs directory
    "index.md":
      title: "Sensitive data discovery tool with friendly UI for Mac, Win, Linux"
      description: "Advanced sensitive data discovery tool combining personal data discovery, payment card discovery, and passwords finder in one solution."
      # Language-specific overrides (optional)
      # If not specified, the default title/description will be auto-translated
      translations:
        ru:
          title: "Инструмент обнаружения конфиденциальных данных с дружественным интерфейсом для Mac, Win, Linux"
          description: "Продвинутый инструмент для обнаружения конфиденциальных данных, объединяющий обнаружение персональных данных, платежных карт и паролей в одном решении."
        de:
          title: "Tool zur Erkennung sensibler Daten mit benutzerfreundlicher Oberfläche für Mac, Win, Linux"
          description: "Fortschrittliches Tool zur Erkennung sensibler Daten, das die Erkennung personenbezogener Daten, Zahlungskarten und Passwörter in einer Lösung vereint."

    "angrydata-core/index.md":
      title: "Core Library | Angry Data Scanner"
      description: "Library for sensitive data processing"
      translations:
        ru:
          title: "Основная библиотека | Angry Data Scanner"
          description: "Библиотека для обработки конфиденциальных данных"

    "download/index.md":
      title: "Download | Angry Data Scanner"
      description: "Download the latest version of Angry Data Scanner"
      translations:
        ru:
          title: "Скачать | Angry Data Scanner"
          description: "Скачайте последнюю версию Angry Data Scanner"

    "CONSOLE.md":
      title: "Console Mode | Angry Data Scanner"
      description: "Using Angry Data Scanner in console mode"
      translations:
        ru:
          title: "Консольный режим | Angry Data Scanner"
          description: "Использование Angry Data Scanner в консольном режиме"

  # Default metadata for files not explicitly configured
  defaults:
    description: "Advanced sensitive data discovery tool combining personal data discovery, payment card discovery, and passwords finder in one solution."
```

## Configuration Structure

### Main Sections

- `metadata.enabled` - enable/disable metadata processing (default: true)
- `metadata.files` - exact file paths with their metadata
- `metadata.defaults` - default metadata for files without specific configuration

### Supported Metadata Fields

- `title` - full page title
- `description` - page description
- `translations` - language-specific overrides for title and description

### Language-Specific Overrides

You can define custom title and description for each language using the `translations` section. This is useful when:

- Automatic translation doesn't capture the right meaning
- You want to use specific terminology for a language
- You need SEO-optimized titles and descriptions for different markets

**How it works:**

1. If a language-specific override exists in the `translations` section, it will be used directly (no automatic translation)
2. If no override is defined for a language, the default title/description will be automatically translated
3. Each language can have its own `title` and `description`

**Example:**

```yaml
"index.md":
  title: "Sensitive data discovery tool"
  description: "Tool for discovering sensitive data"
  translations:
    ru:
      title: "Инструмент обнаружения конфиденциальных данных"
      description: "Инструмент для обнаружения конфиденциальных данных"
    de:
      title: "Tool zur Erkennung sensibler Daten"
      # description will be auto-translated if not specified
    es:
      # Both title and description will be auto-translated
```

**Supported language codes:**
- `ru` - Russian
- `de` - German
- `es` - Spanish
- `fr` - French
- And any other language code supported by Google Translate

### File Patterns

The following wildcard patterns are supported:
- `*` - any number of characters (except `/`)
- `**` - any number of characters including `/`
- `?` - single character

Examples:
- `"angrydata-core/*.md"` - all .md files in angrydata-core folder
- `"**/README.md"` - all README.md files in any subfolders
- `"download/*.md"` - all .md files in download folder

## Metadata Application Priority

### For Translation (translate_docs.py)

When translating documents, metadata is applied in the following priority order:

1. **Language-specific override** in `translations` section for the target language
2. **Auto-translation** of default title/description if no override exists

Example:
```yaml
"index.md":
  title: "Main Page"
  description: "Welcome"
  translations:
    ru:
      title: "Главная страница"  # ← Will be used for Russian
      # description not specified, will be auto-translated
    de:
      # Both title and description will be auto-translated
```

For Russian translation:
- Title: "Главная страница" (from override)
- Description: Auto-translated "Welcome"

For German translation:
- Title: Auto-translated "Main Page"
- Description: Auto-translated "Welcome"

### For Source Files (sync_docs.py)

Metadata is applied in the following priority order:

1. **Exact match** in `files` section
2. **Default values** from `defaults` section

## Usage Examples

### Example 1: Main Page Configuration with Language Overrides

```yaml
metadata:
  files:
    "index.md":
      title: "Angry Data Scanner - Main Page"
      description: "Welcome to Angry Data Scanner"
      translations:
        ru:
          title: "Angry Data Scanner - Главная страница"
          description: "Добро пожаловать в Angry Data Scanner"
        de:
          title: "Angry Data Scanner - Hauptseite"
          description: "Willkommen bei Angry Data Scanner"
```

### Example 2: Partial Language Override

```yaml
metadata:
  files:
    "download/index.md":
      title: "Download | Angry Data Scanner"
      description: "Download the latest version"
      translations:
        ru:
          # Only override title, description will be auto-translated
          title: "Скачать | Angry Data Scanner"
        de:
          # Only override description, title will be auto-translated
          description: "Laden Sie die neueste Version herunter"
```

### Example 3: Auto-Translation (No Overrides)

```yaml
metadata:
  files:
    "CONSOLE.md":
      title: "Console Mode | Angry Data Scanner"
      description: "Using Angry Data Scanner in console mode"
      # No translations section - all languages will be auto-translated
```

### Example 4: Default Configuration

```yaml
metadata:
  defaults:
    description: "Angry Data Scanner project documentation"
```

## Integration with Existing Front Matter

The functionality works correctly with existing front matter in markdown files:

- If front matter already exists, new metadata is added or updates existing ones
- If front matter is missing, it is created automatically
- Existing fields are preserved if they are not overridden in configuration

## Running

### Translation with Metadata Overrides

When translating documentation, language-specific metadata overrides are automatically applied:

```bash
# Translate to all configured languages (async mode)
python scripts/translate_docs.py

# Translate to specific languages
python scripts/translate_docs.py --targets ru de es

# Translate in synchronous mode (slower but more reliable)
python scripts/translate_docs.py --sync
```

The script will:
1. Check `metadata_config.yaml` for language-specific overrides
2. Use overrides if available for the target language
3. Auto-translate title/description if no override is defined

### Applying Metadata to Source Files

Metadata can also be applied to source files when running:

```bash
python scripts/sync_docs.py
```

Or with repository updates:

```bash
python scripts/sync_docs.py --update-repos
```

## Disabling Functionality

To disable metadata processing, set:

```yaml
metadata:
  enabled: false
```

## Logging

When applying metadata, files are updated only if content actually changes, which minimizes unnecessary write operations.
