# AngryScan GitHub Pages

This repository powers the public documentation site for the AngryScan project. The site
is built with [MkDocs](https://www.mkdocs.org/) and aggregates documentation from two
companion repositories:

- [`angrydata-app`](https://github.com/angryscan/angrydata-app)
- [`angrydata-core`](https://github.com/angryscan/angrydata-core)

The aggregation happens automatically in CI and whenever you run the helper script locally.

## Local development

1. Clone this repository alongside the other documentation sources:

   ```bash
   git clone https://github.com/angryscan/angryscan.org.git
   git clone https://github.com/angryscan/angrydata-app.git sources/angrydata-app
   git clone https://github.com/angryscan/angrydata-core.git sources/angrydata-core
   ```

2. Install the documentation dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Sync the external documentation and start the local development server:

   ```bash
   python scripts/sync_docs.py
   mkdocs serve
   ```

The documentation from each project will appear in its own section in the navigation.

## Localization

The site uses [`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n) to provide
localized builds. English is the default language and a Russian translation is included for the
landing page. To translate any additional page, create a sibling file with the appropriate language
suffix—for example, add `page.ru.md` next to `page.md`. Missing translations automatically fall back
to the English source.

Visitors are redirected to the best-matching language based on their browser settings. Their manual
language choice is remembered locally so returning visitors keep their preference.

## Continuous deployment

GitHub Actions builds and deploys the site to GitHub Pages on every push to the default
branch. The workflow fetches the latest documentation from the two upstream repositories,
runs `scripts/sync_docs.py`, builds the MkDocs site, and publishes the resulting static
files.
