# Angry Data Scanner Docs

This repository powers the public documentation site for the Angry Data Scanner project. The site
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
   python scripts/generate_downloads_page.py
   python scripts/translate_docs.py
   mkdocs serve
   ```

The documentation from each project is copied verbatim into the built site. No pages authored in this
repository are published—when the site loads, visitors are automatically redirected into the AngryData
App documentation (as the default entry point), and the navigation exposes each upstream project plus
an automatically generated downloads page with the latest release artifacts. Language switching happens
through the Material UI selector (Russian, Spanish, and German are generated from the English originals);
the translated markdown files themselves are hidden from the navigation. To add another language, simply
append it to the `i18n.languages` list in `mkdocs.yml`—the helper scripts discover the configuration
automatically.

## Continuous deployment

GitHub Actions builds and deploys the site to GitHub Pages on every push to the default
branch. The workflow fetches the latest documentation from the two upstream repositories,
runs `scripts/sync_docs.py`, `scripts/generate_downloads_page.py`, and `scripts/translate_docs.py`, builds the MkDocs site,
and publishes the resulting static files.
