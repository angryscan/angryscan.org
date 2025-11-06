---
hide:
  - navigation
  - toc
---
# Конфигурация синхронизации документации

Файл `sync_config.yaml` позволяет настраивать процесс синхронизации документации.

## Структура конфигурации

```yaml
sync:
  # Заголовки для удаления из документации
  remove_headers:
    - "## Direct Download"
    - "## Another Section"

  # Пропускать контент до первого заголовка
  skip_until_first_header: true

  # Обрабатывать ссылки на переводы
  process_translation_links: true
```

## Параметры

### `remove_headers`
Список заголовков, которые должны быть удалены из документации. Поддерживаются точные совпадения заголовков.

**Примеры:**
- `"## Direct Download"` - удалит раздел Direct Download
- `"## [Console mode](CONSOLE.md)"` - удалит раздел Console mode
- `"## Another Section"` - удалит любой раздел с таким заголовком

### `skip_until_first_header`
Если `true`, то весь контент до первого заголовка (начинающегося с `#`) будет пропущен.

### `process_translation_links`
Если `true`, то ссылки на файлы переводов будут обрабатываться и удаляться.

## Примеры использования

### Удалить только Direct Download
```yaml
sync:
  remove_headers:
    - "## Direct Download"
  skip_until_first_header: true
  process_translation_links: true
```

### Удалить несколько разделов
```yaml
sync:
  remove_headers:
    - "## Direct Download"
    - "## [Console mode](CONSOLE.md)"
    - "## Installation"
  skip_until_first_header: true
  process_translation_links: true
```

### Отключить обработку ссылок на переводы
```yaml
sync:
  remove_headers:
    - "## Direct Download"
  skip_until_first_header: true
  process_translation_links: false
```

### Не пропускать контент до первого заголовка
```yaml
sync:
  remove_headers:
    - "## Direct Download"
  skip_until_first_header: false
  process_translation_links: true
```
