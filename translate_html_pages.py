#!/usr/bin/env python3
"""
Script to translate HTML pages using Google Translate API (deep_translator)
Translates pages for /de, /fr, /es languages
"""
import re
import time
from pathlib import Path
from deep_translator import GoogleTranslator
from html.parser import HTMLParser
from html import unescape

# Base directory
BASE_DIR = Path(__file__).parent / 'src'
LANGUAGES = {
    'de': 'German',
    'fr': 'French', 
    'es': 'Spanish'
}
HTML_FILES = ['index.html', 'discovery.html', 'features.html', 'use-cases.html', 'download.html']

# Elements that should NOT be translated
SKIP_TAGS = {'script', 'style', 'noscript', 'code', 'pre', 'svg', 'path', 'circle', 'rect', 'polyline', 'ellipse'}

def translate_text_with_protection(text, translator, protected_terms):
    """Translate text while protecting URLs, emails, and special terms"""
    if not text or not text.strip():
        return text
    
    # Check if text contains letters
    if not re.search(r'[a-zA-ZА-Яа-я]', text):
        return text
    
    protected_counter = len(protected_terms)
    
    # Protect URLs
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, text)
    protected_text = text
    for url in urls:
        placeholder = f'__PROTECTED_URL_{protected_counter}__'
        protected_terms[placeholder] = url
        protected_text = protected_text.replace(url, placeholder)
        protected_counter += 1
    
    # Protect email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, protected_text)
    for email in emails:
        placeholder = f'__PROTECTED_EMAIL_{protected_counter}__'
        protected_terms[placeholder] = email
        protected_text = protected_text.replace(email, placeholder)
        protected_counter += 1
    
    # Protect GitHub URLs
    github_pattern = r'github\.com/[^\s<>"]+'
    github_urls = re.findall(github_pattern, protected_text)
    for url in github_urls:
        placeholder = f'__PROTECTED_GITHUB_{protected_counter}__'
        protected_terms[placeholder] = url
        protected_text = protected_text.replace(url, placeholder)
        protected_counter += 1
    
    # Translate
    try:
        translated = translator.translate(protected_text)
        # Restore protected terms
        for placeholder, original in protected_terms.items():
            translated = translated.replace(placeholder, original)
        return translated
    except Exception as e:
        print(f"    Translation error: {e}, keeping original")
        return text

def translate_html_content(content, target_lang):
    """Translate HTML content while preserving structure and formatting"""
    translator = GoogleTranslator(source='en', target=target_lang)
    protected_terms = {}
    
    # Protect viewport meta tag from translation (must stay in English)
    viewport_pattern = r'<meta\s+name="viewport"\s+content="([^"]*)"\s*>'
    viewport_matches = list(re.finditer(viewport_pattern, content, re.IGNORECASE))
    viewport_placeholders = {}
    for i, match in enumerate(viewport_matches):
        placeholder = f'__PROTECTED_VIEWPORT_{i}__'
        viewport_placeholders[placeholder] = match.group(0)
        content = content[:match.start()] + placeholder + content[match.end():]
    
    # Translate content attributes in meta tags and title
    # Pattern: content="..." or >text</
    def translate_attr_content(match):
        attr_name = match.group(1)  # e.g., "content", "title"
        attr_value = match.group(2)  # The value inside quotes
        
        # Don't translate viewport meta tag attributes
        if attr_name == 'name' and attr_value.lower() == 'viewport':
            return match.group(0)
        if attr_name == 'content' and 'width=device-width' in attr_value:
            return match.group(0)
        
        # Only translate if it's a translatable attribute
        if attr_name in ['content', 'title', 'description', 'name'] and attr_value:
            # Check if value contains translatable text (has letters)
            if re.search(r'[a-zA-Z]', attr_value):
                try:
                    translated = translate_text_with_protection(attr_value, translator, protected_terms)
                    return f'{attr_name}="{translated}"'
                except:
                    return match.group(0)
        return match.group(0)
    
    # Translate content attributes in tags like <meta content="...">
    content = re.sub(r'(\w+)="([^"]*)"', translate_attr_content, content)
    
    # Restore viewport meta tags
    for placeholder, original in viewport_placeholders.items():
        content = content.replace(placeholder, original)
    
    # Use regex to find text nodes (content between tags)
    result = []
    i = 0
    in_script = False
    in_style = False
    in_language_name = False  # Track if we're inside language-name element
    in_language_option = False  # Track if we're inside language-option element
    
    while i < len(content):
        if content[i] == '<':
            # Find the end of the tag
            tag_end = content.find('>', i)
            if tag_end == -1:
                result.append(content[i:])
                break
            
            tag_content = content[i:tag_end + 1]
            tag_lower = tag_content.lower()
            
            # Check if it's a script or style tag
            if '<script' in tag_lower:
                in_script = True
            elif '</script>' in tag_lower:
                in_script = False
            elif '<style' in tag_lower:
                in_style = True
            elif '</style>' in tag_lower:
                in_style = False
            # Check if it's a language-name or language-option element
            elif 'class="language-name"' in tag_lower or "class='language-name'" in tag_lower:
                in_language_name = True
            elif '</span>' in tag_lower and in_language_name:
                # Check if this is closing the language-name span
                # Look back to see if we opened a language-name
                in_language_name = False
            elif 'class="language-option"' in tag_lower or "class='language-option'" in tag_lower:
                in_language_option = True
            elif '</div>' in tag_lower and in_language_option:
                # Check if this is closing the language-option div
                in_language_option = False
            
            # Always preserve tags as-is
            result.append(tag_content)
            i = tag_end + 1
        else:
            # Find the start of the next tag
            next_tag = content.find('<', i)
            if next_tag == -1:
                text = content[i:]
                if text.strip() and not in_script and not in_style and not in_language_name and not in_language_option:
                    # Translate text
                    translated = translate_text_with_protection(text, translator, protected_terms)
                    result.append(translated)
                else:
                    result.append(text)
                break
            
            text = content[i:next_tag]
            if in_script or in_style or in_language_name or in_language_option:
                # Don't translate script/style/language menu content
                result.append(text)
            elif text.strip():
                # Translate text
                translated = translate_text_with_protection(text, translator, protected_terms)
                result.append(translated)
            else:
                # Preserve whitespace
                result.append(text)
            i = next_tag
    
    return ''.join(result)

def translate_html_file(source_file, target_file, target_lang):
    """Translate an HTML file"""
    print(f"  Translating {source_file.name} to {target_lang}...")
    
    # Read source file
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Save original language menu block to restore after translation
    # Find the language selector wrapper block
    language_menu_start = content.find('<div class="language-selector-wrapper">')
    language_menu_end = content.find('</div>', language_menu_start) if language_menu_start != -1 else -1
    # Find the closing tag more precisely - look for the closing div after all nested divs
    if language_menu_start != -1:
        # Find all nested divs and count them to find the correct closing tag
        temp_content = content[language_menu_start:]
        open_divs = 0
        language_menu_end = -1
        for i, char in enumerate(temp_content):
            if temp_content[i:i+4] == '<div':
                open_divs += 1
            elif temp_content[i:i+6] == '</div>':
                open_divs -= 1
                if open_divs == 0:
                    language_menu_end = language_menu_start + i + 6
                    break
        if language_menu_end != -1:
            original_language_menu = content[language_menu_start:language_menu_end]
        else:
            original_language_menu = None
    else:
        original_language_menu = None
    
    # First, update paths (like generate_lang_pages.py does)
    # Update CSS path
    content = re.sub(r'href="css/', 'href="../css/', content)
    # Update JS paths
    content = re.sub(r'src="js/', 'src="../js/', content)
    # Update assets paths in src and href attributes
    content = re.sub(r'src="assets/', 'src="../assets/', content)
    content = re.sub(r'href="assets/', 'href="../assets/', content)
    # Update assets paths in data-light and data-dark attributes
    content = re.sub(r'data-light="assets/', 'data-light="../assets/', content)
    content = re.sub(r'data-dark="assets/', 'data-dark="../assets/', content)
    
    # Update navigation links to use relative paths with .html extension
    html_files = ['index.html', 'discovery.html', 'features.html', 'use-cases.html', 'download.html']
    for page in html_files:
        # Match absolute paths like href="/page.html" or href="/page" and make them relative
        content = re.sub(rf'href="/{re.escape(page)}"', f'href="{page}"', content)
        page_name = page.replace('.html', '')
        content = re.sub(rf'href="/{re.escape(page_name)}"', f'href="{page}"', content)
        # Also handle language-specific absolute paths
        content = re.sub(rf'href="/{target_lang}/{re.escape(page)}"', f'href="{page}"', content)
        content = re.sub(rf'href="/{target_lang}/{re.escape(page_name)}"', f'href="{page}"', content)
    
    # Update lang attribute
    content = re.sub(r'<html lang="[^"]*"', f'<html lang="{target_lang}"', content)
    
    # Add inline script to apply theme immediately before page render (if not already present)
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
    
    # Update canonical URL
    content = re.sub(
        r'<link rel="canonical" href="https://angryscan\.org/([^/][^"]*)"',
        rf'<link rel="canonical" href="https://angryscan.org/{target_lang}/\1',
        content
    )
    
    # Update og:url
    content = re.sub(
        r'<meta property="og:url" content="https://angryscan\.org/([^/][^"]*)"',
        rf'<meta property="og:url" content="https://angryscan.org/{target_lang}/\1',
        content
    )
    
    # Update twitter:url
    content = re.sub(
        r'<meta property="twitter:url" content="https://angryscan\.org/([^/][^"]*)"',
        rf'<meta property="twitter:url" content="https://angryscan.org/{target_lang}/\1',
        content
    )
    
    # Update footer structure to new format (add footer-top-row wrapper if not present)
    # Check if footer-top-row doesn't exist, then add it
    if 'footer-top-row' not in content:
        # Pattern: <div class="footer-content"> followed by <p> and <div class="footer-links">
        footer_pattern = r'(<div class="footer-content">)\s*(<p[^>]*data-i18n="footer\.copyright"[^>]*>[^<]+</p>)\s*(<div class="footer-links">)'
        footer_replacement = r'\1\n                <div class="footer-top-row">\n                    \2\n                    \3'
        content = re.sub(footer_pattern, footer_replacement, content)
        
        # Also need to close footer-top-row before footer-pages
        # Pattern: </div>\s*</div>\s*<div class="footer-pages">
        footer_close_pattern = r'(</div>\s*</div>)\s*(<div class="footer-pages">)'
        footer_close_replacement = r'\1\n                </div>\n                \2'
        content = re.sub(footer_close_pattern, footer_close_replacement, content)
    
    # Find the FIRST occurrence of <body> and LAST occurrence of </body> to handle cases correctly
    body_start = content.find('<body>')
    body_end = content.rfind('</body>')  # Use rfind to get the LAST </body>
    head_start = content.find('<head>')
    head_end = content.find('</head>')
    html_end_tag = content.rfind('</html>')  # Find the LAST </html> tag
    
    if body_start == -1 or body_end == -1:
        print(f"  Warning: Could not find <body> tag in {source_file.name}")
        return
    
    # Split content into parts
    # First, ensure we only work with content up to the first </html> to avoid duplicates
    if html_end_tag != -1:
        content = content[:html_end_tag + 7]  # Only work with content up to first </html>
        # Re-find positions after truncation
        body_start = content.find('<body>')
        body_end = content.rfind('</body>')
        head_start = content.find('<head>')
        head_end = content.find('</head>')
        html_end_tag = content.rfind('</html>')
    
    before_head = content[:head_start] if head_start != -1 else content[:body_start]
    head_content = content[head_start + 6:head_end] if head_start != -1 and head_end != -1 else ""
    between_head_body = content[head_end + 7:body_start] if head_start != -1 and head_end != -1 else content[:body_start]
    body_content = content[body_start + 6:body_end]  # Content between <body> and </body>
    after_body = content[body_end + 7:html_end_tag] if html_end_tag != -1 else ""
    
    # Translate head section (title, meta descriptions, etc.)
    translated_head_content = head_content
    if head_start != -1 and head_end != -1 and head_content.strip():
        try:
            translated_head_content = translate_html_content(head_content, target_lang)
        except Exception as e:
            print(f"    Warning: Could not translate head section: {e}")
            translated_head_content = head_content
    
    # Translate body content
    try:
        translated_body = translate_html_content(body_content, target_lang)
        
        # Reconstruct HTML properly - no duplicates
        # Structure: before_head + <head> + translated_head_content + </head> + between_head_body + <body> + translated_body + </body> + after_body + </html>
        new_content = before_head
        if head_start != -1:
            new_content += '<head>' + translated_head_content + '</head>'
        new_content += between_head_body
        new_content += '<body>' + translated_body + '</body>'
        new_content += after_body
        if html_end_tag != -1:
            new_content += '</html>'
        
        # CRITICAL: Remove any duplicate content after </html>
        # Find the FIRST occurrence of </html> and remove everything after it
        html_end = new_content.find('</html>')
        if html_end != -1:
            # Keep only up to and including </html>
            new_content = new_content[:html_end + 7]
            # Add newline at the end for clean file
            new_content += '\n'
        else:
            # If </html> not found, try to find </body></html>
            html_end = new_content.find('</body></html>')
            if html_end != -1:
                new_content = new_content[:html_end + 14] + '\n'
            else:
                # Last resort: find last </body>
                body_end_pos = new_content.rfind('</body>')
                if body_end_pos != -1:
                    new_content = new_content[:body_end_pos + 7] + '\n'
        
        # Restore original language menu block (don't translate language names)
        if original_language_menu:
            # Find the translated language menu block in new_content
            new_language_menu_start = new_content.find('<div class="language-selector-wrapper">')
            if new_language_menu_start != -1:
                # Find the closing tag
                temp_content = new_content[new_language_menu_start:]
                open_divs = 0
                new_language_menu_end = -1
                for i, char in enumerate(temp_content):
                    if temp_content[i:i+4] == '<div':
                        open_divs += 1
                    elif temp_content[i:i+6] == '</div>':
                        open_divs -= 1
                        if open_divs == 0:
                            new_language_menu_end = new_language_menu_start + i + 6
                            break
                if new_language_menu_end != -1:
                    # Replace translated menu with original
                    new_content = new_content[:new_language_menu_start] + original_language_menu + new_content[new_language_menu_end:]
        
        # Write translated file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✓ Translated {source_file.name} to {target_lang}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    except Exception as e:
        print(f"  ✗ Error translating {source_file.name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main translation function"""
    print("Starting HTML page translation using Google Translate API...")
    print("Note: This may take a few minutes depending on page size...")
    
    for lang_code, lang_name in LANGUAGES.items():
        print(f"\nTranslating pages to {lang_name} ({lang_code})...")
        
        lang_dir = BASE_DIR / lang_code
        lang_dir.mkdir(exist_ok=True)
        
        for html_file in HTML_FILES:
            source_file = BASE_DIR / html_file
            if not source_file.exists():
                print(f"  Warning: {html_file} not found, skipping...")
                continue
            
            target_file = lang_dir / html_file
            translate_html_file(source_file, target_file, lang_code)
    
    print("\n✓ HTML page translation completed!")
    print("Note: Translated pages are now in src/de/, src/fr/, src/es/ directories")

if __name__ == '__main__':
    main()

