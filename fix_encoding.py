# fix_encoding.py
#!/usr/bin/env python3
import glob
import re

def fix_unicode_escapes(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Если есть \uXXXX - декодировать
    if '\\u' in content:
        # Декодировать через encode/decode
        try:
            fixed = content.encode('utf-8').decode('unicode-escape')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            print(f"✓ Fixed: {filepath}")
        except Exception as e:
            print(f"✗ Error in {filepath}: {e}")

# Исправить все .md файлы
for md_file in glob.glob('content/**/*.md', recursive=True):
    fix_unicode_escapes(md_file)
