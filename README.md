# Angry Data Scanner Website

This repository contains the source code for the [Angry Data Scanner](https://angryscan.org) website.

## Project Structure

```
.
├── src/              # Source files for the static website
│   ├── assets/       # Images, icons, screenshots
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files (i18n, config, components, script)
│   └── *.html        # HTML pages
├── static/           # Static files (robots.txt, BingSiteAuth.xml, etc.)
├── docs/             # Minimal MkDocs documentation (required for build)
├── hooks.py          # MkDocs build hook (replaces site with src content)
├── mkdocs.yml        # MkDocs configuration
└── requirements.txt  # Python dependencies
```

## Local Development

1. Clone this repository:

   ```bash
   git clone https://github.com/angryscan/angryscan.org.git
   cd angryscan.org
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate and translate language-specific pages (optional, done automatically during build):

   ```bash
   # Generate base pages for all languages
   python3 generate_lang_pages.py
   
   # Translate pages for de, fr, es using Google Translate API
   python3 translate_html_pages.py
   ```

   This creates `/ru/`, `/de/`, `/fr/`, and `/es/` directories:
   - `/ru/` - Russian pages with custom translations
   - `/de/`, `/fr/`, `/es/` - Translated pages using Google Translate API

4. Build the site:

   ```bash
   mkdocs build
   ```

   This will copy files from `src/` and `static/` to `site/` directory, including language-specific pages.

4. Start local development server:

   ```bash
   mkdocs serve
   ```

   Or use a simple HTTP server with URL rewrite support:

   ```bash
   python3 dev_server.py
   ```

   This server supports clean URLs (without .html extension):
   - `/discovery` → `discovery.html`
   - `/features` → `features.html`
   - `/ru/discovery` → `ru/discovery.html`
   - etc.

   Or use a basic HTTP server (without rewrite support):

   ```bash
   cd src && python3 -m http.server 8000
   ```

## Features

- **Multi-language support**: 
  - English (root pages: `/`, `/index.html`, etc.)
  - Russian with custom translations (`/ru/`)
  - German with Google Translate (`/de/`)
  - French with Google Translate (`/fr/`)
  - Spanish with Google Translate (`/es/`)
- **Analytics**: Yandex Metrika, Google Tag Manager, and Bing verification
- **Modern design**: Responsive, dark/light theme support
- **Static site**: Fast, SEO-friendly static HTML

## Deployment

### Автоматический деплой (GitHub Pages)

Сайт автоматически деплоится на GitHub Pages при каждом push в ветку `main`:

1. **Настройка GitHub Pages** (один раз):
   - Перейдите в Settings → Pages
   - Source: выберите "GitHub Actions"
   - Сохраните настройки

2. **Процесс деплоя**:
   - При push в `main` запускается GitHub Actions workflow
   - Устанавливаются зависимости (`pip install -r requirements.txt`)
   - Запускается сборка (`mkdocs build`)
   - `hooks.py` копирует файлы из `src/` и `static/` в `site/`
   - Содержимое `site/` деплоится на GitHub Pages
   - Сайт доступен по адресу: `https://<username>.github.io/<repository>/` или `https://angryscan.org/`

3. **Ручной запуск деплоя**:
   - Перейдите в Actions → Deploy documentation
   - Нажмите "Run workflow" → "Run workflow"

### Ручной деплой на сервер

Если нужно задеплоить на другой сервер:

```bash
# 1. Собрать сайт
mkdocs build

# 2. Скопировать содержимое папки site/ на сервер
# Например, через rsync:
rsync -avz --delete site/ user@server:/var/www/html/

# Или через scp:
scp -r site/* user@server:/var/www/html/
```

### Альтернативные варианты хостинга

- **Netlify**: подключите репозиторий, укажите build command: `mkdocs build`, publish directory: `site`
- **Vercel**: аналогично Netlify
- **Cloudflare Pages**: подключите репозиторий, укажите build command и output directory
- **Любой статический хостинг**: просто загрузите содержимое папки `site/` после сборки
