#!/usr/bin/env python3
"""
Script to generate language-specific pages for /ru, /de, /fr, /es
"""
import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / 'src'
LANGUAGES = ['ru', 'de', 'fr', 'es']
HTML_FILES = ['index.html', 'discovery.html', 'features.html', 'use-cases.html', 'download.html']

def update_paths(content, lang):
    """Update paths in HTML content for language subdirectory"""
    # Update CSS path
    content = re.sub(r'href="css/', 'href="../css/', content)
    # Update JS paths
    content = re.sub(r'src="js/', 'src="../js/', content)
    # Update assets paths
    content = re.sub(r'src="assets/', 'src="../assets/', content)
    content = re.sub(r'href="assets/', 'href="../assets/', content)
    # Update assets paths in data-light and data-dark attributes
    content = re.sub(r'data-light="assets/', 'data-light="../assets/', content)
    content = re.sub(r'data-dark="assets/', 'data-dark="../assets/', content)
    # Update content attribute with assets
    content = re.sub(r'content="https://angryscan\.org/assets/', 'content="https://angryscan.org/assets/', content)
    
    # Update navigation links to use clean URLs (without .html extension)
    for page in HTML_FILES:
        page_name = page.replace('.html', '')
        
        # Replace href="page.html" with clean URL
        if lang in ['ru', 'de', 'fr', 'es']:
            # For language versions, use /lang/page
            if page_name == 'index':
                content = re.sub(r'href="index\.html"', f'href="/{lang}/"', content)
                content = re.sub(r'href="index"', f'href="/{lang}/"', content)
                content = re.sub(r'href="/"', f'href="/{lang}/"', content)
            else:
                content = re.sub(rf'href="{re.escape(page)}"', f'href="/{lang}/{page_name}"', content)
                content = re.sub(rf'href="{re.escape(page_name)}"', f'href="/{lang}/{page_name}"', content)
        else:
            # For English, use /page
            if page_name == 'index':
                content = re.sub(r'href="index\.html"', 'href="/"', content)
                content = re.sub(r'href="index"', 'href="/"', content)
            else:
                content = re.sub(rf'href="{re.escape(page)}"', f'href="/{page_name}"', content)
                content = re.sub(rf'href="{re.escape(page_name)}"', f'href="/{page_name}"', content)
        
        # Also handle absolute paths
        pattern = rf'href="/{re.escape(page)}"'
        if lang in ['ru', 'de', 'fr', 'es']:
            if page_name == 'index':
                content = re.sub(pattern, f'href="/{lang}/"', content)
            else:
                content = re.sub(pattern, f'href="/{lang}/{page_name}"', content)
            # Also update root links to include language prefix
            if page_name != 'index':
                content = re.sub(r'href="/"', f'href="/{lang}/"', content)
                content = re.sub(rf'href="/{re.escape(page_name)}"', f'href="/{lang}/{page_name}"', content)
        else:
            if page_name == 'index':
                content = re.sub(pattern, 'href="/"', content)
            else:
                content = re.sub(pattern, f'href="/{page_name}"', content)
    
    # Update canonical URL - only if it's a root path
    content = re.sub(
        r'<link rel="canonical" href="https://angryscan\.org/([^/][^"]*)"',
        rf'<link rel="canonical" href="https://angryscan.org/{lang}/\1',
        content
    )
    
    # Update og:url - only if it's a root path
    content = re.sub(
        r'<meta property="og:url" content="https://angryscan\.org/([^/][^"]*)"',
        rf'<meta property="og:url" content="https://angryscan.org/{lang}/\1',
        content
    )
    
    # Update twitter:url - only if it's a root path
    content = re.sub(
        r'<meta property="twitter:url" content="https://angryscan\.org/([^/][^"]*)"',
        rf'<meta property="twitter:url" content="https://angryscan.org/{lang}/\1',
        content
    )
    
    # Update footer structure to new format (add footer-top-row wrapper)
    # Pattern: <div class="footer-content">\n                <p>...\n                <div class="footer-links">
    # Replace with: <div class="footer-content">\n                <div class="footer-top-row">\n                    <p>...\n                    <div class="footer-links">
    old_footer_pattern = r'(<div class="footer-content">)\s*(<p data-i18n="footer\.copyright">[^<]+</p>)\s*(<div class="footer-links">)'
    new_footer_replacement = r'\1\n                <div class="footer-top-row">\n                    \2\n                    \3'
    content = re.sub(old_footer_pattern, new_footer_replacement, content)
    
    # Also handle case where footer-links comes after p tag on same line or different structure
    # Pattern: </p>\n                <div class="footer-links">
    # Need to wrap p and footer-links in footer-top-row
    footer_wrap_pattern = r'(<div class="footer-content">)\s*(<p[^>]*data-i18n="footer\.copyright"[^>]*>[^<]+</p>)\s*(<div class="footer-links">[^<]+</div>)\s*(</div>)\s*(<div class="footer-pages">)'
    footer_wrap_replacement = r'\1\n                <div class="footer-top-row">\n                    \2\n                    \3\n                </div>\n                \5'
    content = re.sub(footer_wrap_pattern, footer_wrap_replacement, content, flags=re.DOTALL)
    
    return content

def generate_language_pages():
    """Generate language-specific pages"""
    # Languages that use Python API translation (will be translated separately)
    TRANSLATED_LANGS = {'de', 'fr', 'es'}
    
    for lang in LANGUAGES:
        lang_dir = BASE_DIR / lang
        lang_dir.mkdir(exist_ok=True)
        
        if lang in TRANSLATED_LANGS:
            print(f"Generating pages for {lang} (will be translated via Python API)...")
        else:
            print(f"Generating pages for {lang}...")
        
        for html_file in HTML_FILES:
            source_file = BASE_DIR / html_file
            if not source_file.exists():
                print(f"  Warning: {html_file} not found, skipping...")
                continue
            
            dest_file = lang_dir / html_file
            
            # For translated languages, only update paths if file doesn't exist
            # (translation script will create translated versions)
            if lang in TRANSLATED_LANGS and dest_file.exists():
                print(f"  Skipping {lang}/{html_file} (already translated)")
                continue
            
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update paths
            content = update_paths(content, lang)
            
            # Add inline script to apply theme immediately before page render (for all languages)
            if '</head>' in content and 'data-theme' not in content[:content.find('</head>')]:
                theme_script = '''    <!-- Inline script to apply theme immediately before page render to avoid flash -->
    <script>
        // Apply theme synchronously before page renders to avoid flash
        (function() {
            try {
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme) {
                    document.documentElement.setAttribute('data-theme', savedTheme);
                    
                    // Update screenshot src immediately if dark theme (before image loads)
                    if (savedTheme === 'dark') {
                        // Function to update screenshot src
                        const updateScreenshotSrc = function() {
                            const screenshot = document.getElementById('heroScreenshot');
                            if (screenshot) {
                                const darkSrc = screenshot.getAttribute('data-dark');
                                if (darkSrc) {
                                    screenshot.src = darkSrc;
                                    // Show image after it loads
                                    screenshot.onload = function() {
                                        screenshot.style.opacity = '1';
                                    };
                                    // If already loaded, show immediately
                                    if (screenshot.complete) {
                                        screenshot.style.opacity = '1';
                                    }
                                }
                            }
                        };
                        
                        // Try immediately if DOM is ready, otherwise wait for DOMContentLoaded
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', updateScreenshotSrc);
                        } else {
                            updateScreenshotSrc();
                        }
                    } else {
                        // For light theme, show image immediately
                        const showScreenshot = function() {
                            const screenshot = document.getElementById('heroScreenshot');
                            if (screenshot) {
                                if (screenshot.complete) {
                                    screenshot.style.opacity = '1';
                                } else {
                                    screenshot.onload = function() {
                                        screenshot.style.opacity = '1';
                                    };
                                }
                            }
                        };
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', showScreenshot);
                        } else {
                            showScreenshot();
                        }
                    }
                }
            } catch (e) {
                // Ignore errors if localStorage is not available
            }
        })();
    </script>
'''
                head_end = content.find('</head>')
                if head_end != -1:
                    content = content[:head_end] + theme_script + content[head_end:]
            
            # Add inline script to hide page until translations are applied (for all languages)
            # Check if script already exists to avoid duplication
            if 'data-lang-loading' not in content:
                # Find </body> tag and add inline script before it
                body_end = content.find('</body>')
                if body_end != -1:
                    inline_script = '''    <!-- Inline script to apply translations immediately before page render -->
    <script>
        // Apply translations synchronously before page renders to avoid flicker
        (function() {
            // Detect language from URL or localStorage
            const path = window.location.pathname;
            const pathMatch = path.match(/^\\/(ru|de|fr|es)\\//);
            let lang = pathMatch ? pathMatch[1] : null;
            
            if (!lang) {
                const savedLang = localStorage.getItem('language');
                if (savedLang && (savedLang === 'ru' || savedLang === 'es' || savedLang === 'de' || savedLang === 'fr')) {
                    lang = savedLang;
                } else {
                    const browserLang = navigator.language || navigator.userLanguage;
                    if (browserLang.startsWith('ru')) lang = 'ru';
                    else if (browserLang.startsWith('es')) lang = 'es';
                    else if (browserLang.startsWith('de')) lang = 'de';
                    else if (browserLang.startsWith('fr')) lang = 'fr';
                    else lang = 'en';
                }
            }
            
            // Hide body until translations are applied (for all languages to prevent flicker on mobile)
            // This helps with mobile rendering and prevents content flash
            document.documentElement.style.visibility = 'hidden';
            document.documentElement.setAttribute('data-lang-loading', lang || 'en');
        })();
    </script>
    
'''
                    content = content[:body_end] + inline_script + content[body_end:]
            
            # Write to language directory
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if lang in TRANSLATED_LANGS:
                print(f"  Created base {lang}/{html_file} (will be translated)")
            else:
                print(f"  Created {lang}/{html_file}")
    
    print("Language pages generated successfully!")

if __name__ == '__main__':
    generate_language_pages()

