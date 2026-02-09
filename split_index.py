#!/usr/bin/env python3
"""
Script to split the monolithic index.html into modular components
"""
import re
import os

def extract_between(content, start_pattern, end_pattern, include_markers=False):
    """Extract content between two patterns"""
    start_match = re.search(start_pattern, content, re.DOTALL)
    if not start_match:
        return None, content
    
    start_pos = start_match.start() if include_markers else start_match.end()
    
    # Search for end pattern after start
    end_match = re.search(end_pattern, content[start_match.end():], re.DOTALL)
    if not end_match:
        return None, content
    
    end_pos = start_match.end() + (end_match.end() if include_markers else end_match.start())
    
    extracted = content[start_pos:end_pos]
    remaining = content[:start_match.start()] + content[end_pos:]
    
    return extracted, remaining

def main():
    # Read the original index.html
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("[*] Reading index.html...")
    print(f"    Total size: {len(content)} characters, {content.count(chr(10))} lines")
    
    # Extract CSS
    print("\n[*] Extracting CSS...")
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if css_match:
        css_content = css_match.group(1)
        with open('static/css/app.css', 'w', encoding='utf-8') as f:
            f.write(css_content.strip())
        print(f"    [OK] Saved to static/css/app.css ({len(css_content)} chars)")
    
    # Extract main JavaScript (everything in the last <script> tag before </body>)
    print("\n[*] Extracting JavaScript...")
    # Find all script tags
    script_pattern = r'<script>(.*?)</script>'
    scripts = list(re.finditer(script_pattern, content, re.DOTALL))
    
    if scripts:
        # The main app script is usually the largest one
        main_script = max(scripts, key=lambda m: len(m.group(1)))
        js_content = main_script.group(1)
        
        with open('static/js/app.js', 'w', encoding='utf-8') as f:
            f.write(js_content.strip())
        print(f"    [OK] Saved to static/js/app.js ({len(js_content)} chars)")
    
    # Extract header
    print("\n[*] Extracting components...")
    header_match = re.search(r'(<header>.*?</header>)', content, re.DOTALL)
    if header_match:
        with open('templates/components/header.html', 'w', encoding='utf-8') as f:
            f.write(header_match.group(1))
        print("    [OK] header.html")
    
    # Extract side navigation
    side_nav_match = re.search(r'(<nav class="side-nav".*?</nav>)', content, re.DOTALL)
    if side_nav_match:
        with open('templates/components/side_nav.html', 'w', encoding='utf-8') as f:
            f.write(side_nav_match.group(1))
        print("    [OK] side_nav.html")
    
    # Extract bottom navigation
    bottom_nav_match = re.search(r'(<nav class="bottom-nav".*?</nav>)', content, re.DOTALL)
    if bottom_nav_match:
        with open('templates/components/bottom_nav.html', 'w', encoding='utf-8') as f:
            f.write(bottom_nav_match.group(1))
        print("    [OK] bottom_nav.html")
    
    # Extract FAB
    fab_match = re.search(r'(<button class="fab".*?</button>)', content, re.DOTALL)
    if fab_match:
        with open('templates/components/fab.html', 'w', encoding='utf-8') as f:
            f.write(fab_match.group(1))
        print("    [OK] fab.html")
    
    # Extract sheet overlay
    sheet_match = re.search(r'(<div id="sheet-overlay".*?</div>\s*</div>\s*</div>)', content, re.DOTALL)
    if sheet_match:
        with open('templates/components/sheets.html', 'w', encoding='utf-8') as f:
            f.write(sheet_match.group(1))
        print("    [OK] sheets.html")
    
    print("\n[*] Extraction complete!")
    print("\n[*] Next steps:")
    print("    1. Review extracted files")
    print("    2. Create new index.html with includes")
    print("    3. Test the application")

if __name__ == '__main__':
    main()
