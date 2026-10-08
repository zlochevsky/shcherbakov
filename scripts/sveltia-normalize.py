#!/usr/bin/env python3
"""Привести файлы коллекции Sveltia CMS (static/admin/config.yml) к виду, в котором их сохраняет сама Sveltia,
чтобы первая правка в редакторе не давала в diff перестановку всего заголовка.

Как пишет Sveltia (json-frontmatter, проверено по исходникам 2026-10-07, serialize.js / format.js):
- ключи заголовка: aliases (у коллекций-папок) → поля из config.yml в их порядке → остальные по алфавиту
  (Intl.Collator: без учёта регистра, числа по значению); вложенные объекты собираются в порядке первого ключа;
- необязательные поля из config.yml с пустым значением не пишутся (output.omit_empty_optional_fields);
- отступ JSON — output.json.indent_size;
- после заголовка пустая строка, затем тело; в конце файла один перевод строки.

Использование: scripts/sveltia-normalize.py <коллекция> [...] [--check]
  --check — только показать, какие файлы изменились бы (код выхода 1, если такие есть).
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'static/admin/config.yml'


def natural_key(s):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)', s)]


def flatten(value, prefix, out):
    if isinstance(value, dict) and value:
        for k, v in value.items():
            flatten(v, f'{prefix}{k}.', out)
    elif isinstance(value, list) and value:
        for i, v in enumerate(value):
            flatten(v, f'{prefix}{i}.', out)
    else:
        out[prefix[:-1]] = value
    return out


def unflatten(items):
    root = {}
    for key, value in items:
        parts = key.split('.')
        cur = root
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = value

    def lists(node):
        if isinstance(node, dict):
            node = {k: lists(v) for k, v in node.items()}
            if node and all(k.isdigit() for k in node):
                return [node[k] for k in sorted(node, key=int)]
        return node
    return lists(root)


def field_paths(fields, prefix=''):
    """Пути полей из config.yml по порядку: (путь, обязательное ли)."""
    for f in fields:
        path = prefix + f['name']
        if f.get('widget') == 'object':
            yield from field_paths(f.get('fields', []), path + '.')
        elif f['name'] != 'body' or prefix:
            yield path, f.get('required', True)


def is_empty(v):
    return v is None or v == '' or v == [] or v == {}


def normalize(text, fields, indent, entry_collection):
    t = text.strip().replace('\r\n', '\n')
    m = re.match(r'^\{\n(?:(?P<head>[\s\S]*?)\n)?\}(?:\n(?P<body>[\s\S]*))?$', t)
    if not m:
        return None
    head = json.loads('{' + (m.group('head') or '') + '}')
    body = m.group('body') or ''
    if body.startswith('\n'):
        body = body[1:]
    flat = flatten(head, '', {})
    items = []
    if entry_collection:
        for k in [k for k in flat if k == 'aliases' or k.startswith('aliases.')]:
            items.append((k, flat.pop(k)))
    for path, required in field_paths(fields):
        if path in flat:
            v = flat.pop(path)
            if required or not is_empty(v):
                items.append((path, v))
    items += sorted(flat.items(), key=lambda kv: natural_key(kv[0]))
    content = unflatten(items)
    if not content:
        return body + '\n'
    h = json.dumps(content, ensure_ascii=False, indent=indent)[1:-1].strip('\n')
    return '{\n' + h + '\n}\n' + ('\n' + body + '\n' if body else '')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    cfg = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    indent = cfg.get('output', {}).get('json', {}).get('indent_size', 2)
    cols = {c['name']: c for c in cfg['collections'] if not c.get('divider')}
    changed = 0
    for name in args:
        col = cols[name]
        folder = ROOT / col['folder']
        depth = (col.get('nested') or {}).get('depth', 1)
        files = [p for p in folder.rglob('*.md') if len(p.relative_to(folder).parts) <= depth]
        flt = col.get('filter')
        for p in sorted(files):
            text = p.read_text(encoding='utf-8')
            if flt:
                hm = re.match(r'^\{\n(?:(?P<head>[\s\S]*?)\n)?\}', text.strip())
                head = json.loads('{' + (hm.group('head') or '') + '}') if hm else {}
                if head.get(flt['field']) != flt['value']:
                    continue
            new = normalize(text, col['fields'], indent, 'folder' in col)
            if new is not None and new != text:
                changed += 1
                if check:
                    print(p.relative_to(ROOT))
                else:
                    p.write_text(new, encoding='utf-8')
    print(f'{"изменились бы" if check else "изменено"}: {changed}', file=sys.stderr)
    sys.exit(1 if check and changed else 0)


if __name__ == '__main__':
    main()
