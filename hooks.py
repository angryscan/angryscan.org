"""MkDocs event hooks used by the AngryScan documentation build."""

from __future__ import annotations
import hashlib
import os
import time

from mkdocs.structure.nav import Navigation


def on_nav(nav: Navigation, config, files):
    """Ensure a homepage exists so downstream plugins (i18n) do not warn."""
    if nav.homepage is None:
        for page in nav.pages:
            nav.homepage = page
            break
    return nav


def on_post_build(config):
    """Add cache-busting to CSS files after build."""
    import os
    import re
    
    # Get the site directory
    site_dir = config['site_dir']
    
    # Define CSS files that need cache-busting
    css_files = [
        'assets/stylesheets/extra.css',
        'assets/stylesheets/language-flags.css'
    ]
    
    # Generate a cache-busting hash based on file modification times
    cache_hash = generate_cache_hash(site_dir, css_files)
    
    # Process all HTML files in the site directory
    for root, dirs, files in os.walk(site_dir):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                add_cache_busting_to_html(html_path, css_files, cache_hash)


def generate_cache_hash(site_dir, css_files):
    """Generate a hash based on CSS file modification times for cache-busting."""
    hash_input = ""
    
    for css_file in css_files:
        css_path = os.path.join(site_dir, css_file)
        if os.path.exists(css_path):
            # Use file modification time and size for hash
            stat = os.stat(css_path)
            hash_input += f"{css_file}:{stat.st_mtime}:{stat.st_size}"
    
    # Add current timestamp to ensure uniqueness
    hash_input += f":{time.time()}"
    
    # Generate a short hash
    return hashlib.md5(hash_input.encode()).hexdigest()[:8]


def add_cache_busting_to_html(html_path, css_files, cache_hash):
    """Add cache-busting parameters to CSS links in HTML files."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add cache-busting to each CSS file
        for css_file in css_files:
            # Pattern to match CSS file references
            patterns = [
                f'href="{css_file}"',
                f"href='{css_file}'",
                f'rel="stylesheet" href="{css_file}"',
                f"rel='stylesheet' href='{css_file}'"
            ]
            
            for pattern in patterns:
                if '?' in pattern:
                    # If already has parameters, replace them
                    new_pattern = pattern.split('?')[0] + f'?v={cache_hash}'
                    content = content.replace(pattern, new_pattern)
                else:
                    # Add cache-busting parameter
                    new_pattern = pattern[:-1] + f'?v={cache_hash}"'
                    content = content.replace(pattern, new_pattern)
        
        # Write back if content changed
        if content != original_content:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    except Exception as e:
        print(f"Warning: Could not process {html_path}: {e}")
