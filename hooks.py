"""MkDocs event hooks used by the AngryScan documentation build."""

from __future__ import annotations

from mkdocs.structure.nav import Navigation


def on_nav(nav: Navigation, config, files):
    """Ensure a homepage exists so downstream plugins (i18n) do not warn."""
    if nav.homepage is None:
        for page in nav.pages:
            nav.homepage = page
            break
    return nav


def on_post_build(config):
    """Replace MkDocs build with static site from src directory."""
    import shutil
    import subprocess
    from pathlib import Path
    
    # Get the site directory
    site_dir = Path(config['site_dir'])
    src_dir = Path(__file__).parent / 'src'
    static_dir = Path(__file__).parent / 'static'
    
    # Check if src directory exists
    if not src_dir.exists():
        print(f"Warning: src directory not found at {src_dir}")
        return
    
    # Get current language being built (from i18n plugin)
    # The i18n plugin sets site_dir to include language subdirectory for non-default languages
    # For default language (en), site_dir is just 'site', for others it's 'site/ru', 'site/de', etc.
    current_lang = None
    site_dir_str = str(site_dir)
    if '/site/' in site_dir_str or '\\site\\' in site_dir_str:
        # Extract language from path like 'site/ru' or 'site/de'
        parts = site_dir_str.replace('\\', '/').split('/')
        if 'site' in parts:
            site_idx = parts.index('site')
            if site_idx + 1 < len(parts):
                potential_lang = parts[site_idx + 1]
                if potential_lang in ['ru', 'de', 'fr', 'es']:
                    current_lang = potential_lang
    
    # Only run generation and translation scripts once (for the first language build, typically 'en')
    # Use a marker file to track if scripts have already run
    marker_file = Path(__file__).parent / '.scripts_run_marker'
    
    if not marker_file.exists():
        # First build - run scripts
        marker_file.touch()
        
        # Generate HTML pages from templates (includes all languages from config.json)
        generate_html_script = Path(__file__).parent / 'generate_html.py'
        if generate_html_script.exists():
            print("Generating HTML pages from templates...")
            try:
                subprocess.run(['python3', str(generate_html_script)], check=True, cwd=generate_html_script.parent)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to generate HTML pages: {e}")
            except FileNotFoundError:
                print("Warning: python3 not found, skipping HTML generation")
    else:
        # Scripts already run for this build - skip
        print("Skipping generation/translation (already done for this build)")
    
    # Remove all existing files in site_dir (except .git if exists)
    print(f"Cleaning site directory: {site_dir}")
    for item in site_dir.iterdir():
        if item.name != '.git':
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    # Copy all files from src to site_dir
    print(f"Copying files from {src_dir} to {site_dir}")
    for item in src_dir.iterdir():
        if item.name != '.git' and item.name != 'README.md':
            dest = site_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    
    # Create clean URL structure for GitHub Pages (discovery/, features/, etc.)
    # Each page gets its own folder with index.html inside
    print("Creating clean URL structure for GitHub Pages...")
    clean_url_pages = ['discovery', 'features', 'use-cases', 'download']
    for page in clean_url_pages:
        page_dir = site_dir / page
        page_dir.mkdir(exist_ok=True)
        source_file = site_dir / f"{page}.html"
        if source_file.exists():
            dest_file = page_dir / "index.html"
            shutil.copy2(source_file, dest_file)
            # Update paths in the copied file (css, js, assets should be ../css, ../js, ../assets)
            with open(dest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('href="css/', 'href="../css/')
            content = content.replace('src="js/', 'src="../js/')
            content = content.replace('src="assets/', 'src="../assets/')
            content = content.replace('href="assets/', 'href="../assets/')
            content = content.replace('data-light="assets/', 'data-light="../assets/')
            content = content.replace('data-dark="assets/', 'data-dark="../assets/')
            # Update navigation links to use clean URLs
            content = content.replace(f'href="{page}.html"', f'href="/{page}"')
            content = content.replace(f'href="/{page}.html"', f'href="/{page}"')
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Created {page}/index.html")
    
    # Copy language-specific directories (ru, de, fr, es) to site root
    print("Copying language-specific directories...")
    for lang_dir in ['ru', 'de', 'fr', 'es']:
        lang_src = src_dir / lang_dir
        if lang_src.exists() and lang_src.is_dir():
            lang_dest = site_dir / lang_dir
            if lang_dest.exists():
                shutil.rmtree(lang_dest)
            shutil.copytree(lang_src, lang_dest)
            print(f"  Copied {lang_dir}/ to site root")
    
    # Create clean URL structure for language-specific pages (after copying)
    print("Creating clean URL structure for language-specific pages...")
    for lang_dir in ['ru', 'de', 'fr', 'es']:
        lang_path = site_dir / lang_dir
        if lang_path.exists() and lang_path.is_dir():
            for page in clean_url_pages:
                page_dir = lang_path / page
                page_dir.mkdir(exist_ok=True)
                source_file = lang_path / f"{page}.html"
                if source_file.exists():
                    dest_file = page_dir / "index.html"
                    shutil.copy2(source_file, dest_file)
                    # Update paths in the copied file
                    with open(dest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace('href="../css/', 'href="../../css/')
                    content = content.replace('src="../js/', 'src="../../js/')
                    content = content.replace('src="../assets/', 'src="../../assets/')
                    content = content.replace('href="../assets/', 'href="../../assets/')
                    content = content.replace('data-light="../assets/', 'data-light="../../assets/')
                    content = content.replace('data-dark="../assets/', 'data-dark="../../assets/')
                    # Update navigation links to use clean URLs with language prefix
                    for nav_page in clean_url_pages:
                        if nav_page == 'index':
                            content = content.replace(f'href="index.html"', f'href="/{lang_dir}/"')
                            content = content.replace(f'href="/{lang_dir}/index.html"', f'href="/{lang_dir}/"')
                        else:
                            content = content.replace(f'href="{nav_page}.html"', f'href="/{lang_dir}/{nav_page}"')
                            content = content.replace(f'href="/{lang_dir}/{nav_page}.html"', f'href="/{lang_dir}/{nav_page}"')
                    # Also update root links
                    content = content.replace('href="/"', f'href="/{lang_dir}/"')
                    content = content.replace('href="/discovery"', f'href="/{lang_dir}/discovery"')
                    content = content.replace('href="/features"', f'href="/{lang_dir}/features"')
                    content = content.replace('href="/use-cases"', f'href="/{lang_dir}/use-cases"')
                    content = content.replace('href="/download"', f'href="/{lang_dir}/download"')
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Created {lang_dir}/{page}/index.html")
    
    # Copy static files from static directory
    if static_dir.exists():
        for static_file in static_dir.iterdir():
            if static_file.is_file():
                dest_file = site_dir / static_file.name
                shutil.copy2(static_file, dest_file)
                print(f"Copied {static_file.name} to site root")
    
    # Note: Marker file persists during the build process to prevent multiple script runs
    # It will be automatically removed when mkdocs build starts fresh next time
    
    print(f"Successfully replaced site with src content")
