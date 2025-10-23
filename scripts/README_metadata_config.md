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
      title: "Angry Data Scanner - Главная"
      description: "Мощный инструмент для сканирования и анализа данных"

    "angrydata-core/index.md":
      title: "Angry Data Core - Библиотека"
      description: "Основная библиотека для работы с данными"

    "download/index.md":
      title: "Скачать Angry Data Scanner"
      description: "Загрузите последнюю версию Angry Data Scanner"

    "CONSOLE.md":
      title: "Консольный режим"
      description: "Использование Angry Data Scanner в консольном режиме"

  # Pattern-based configuration (supports wildcards)
  patterns:
    # All files in angrydata-core directory
    "angrydata-core/*.md":
      title_prefix: "Angry Data Core - "
      description: "Документация по библиотеке Angry Data Core"

    # All README files
    "**/README.md":
      title_suffix: " - Документация"
      description: "Документация проекта"

  # Default metadata for files not explicitly configured
  defaults:
    title_suffix: " - Angry Data Scanner"
    description: "Документация Angry Data Scanner"
```

## Configuration Structure

### Main Sections

- `metadata.enabled` - enable/disable metadata processing (default: true)
- `metadata.files` - exact file paths with their metadata
- `metadata.patterns` - patterns for file groups (supports wildcards)
- `metadata.defaults` - default metadata for files without specific configuration

### Supported Metadata Fields

- `title` - full page title
- `description` - page description
- `title_prefix` - title prefix (added to existing or used as new)
- `title_suffix` - title suffix (added to existing or used as new)

### File Patterns

The following wildcard patterns are supported:
- `*` - any number of characters (except `/`)
- `**` - any number of characters including `/`
- `?` - single character

Examples:
- `"angrydata-core/*.md"` - all .md files in angrydata-core folder
- `"**/README.md"` - all README.md files in any subfolders
- `"download/*.md"` - all .md files in download folder

## Metadata Application

Metadata is applied in the following priority order:

1. **Exact match** in `files` section
2. **Pattern** in `patterns` section (first matching)
3. **Default values** from `defaults` section

## Usage Examples

### Example 1: Main Page Configuration

```yaml
metadata:
  files:
    "index.md":
      title: "Angry Data Scanner - Main Page"
      description: "Welcome to Angry Data Scanner"
```

### Example 2: Configuration for All Files in Folder

```yaml
metadata:
  patterns:
    "angrydata-core/*.md":
      title_prefix: "Angry Data Core - "
      description: "Angry Data Core library documentation"
```

### Example 3: Default Configuration

```yaml
metadata:
  defaults:
    title_suffix: " - Angry Data Scanner"
    description: "Angry Data Scanner project documentation"
```

## Integration with Existing Front Matter

The functionality works correctly with existing front matter in markdown files:

- If front matter already exists, new metadata is added or updates existing ones
- If front matter is missing, it is created automatically
- Existing fields are preserved if they are not overridden in configuration

## Running

Metadata is applied automatically when running:

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
