#!/usr/bin/env python3
"""Внутренние ссылки собранного сайта (public/), которые ведут на несуществующие страницы.

Нужен для отслеживания прогресса переноса legacy-разделов: пока страница-цель не
перенесена, ссылки на неё «битые». Показывает, сколько таких целей и какие страницы
на них ссылаются. Якоря (#...) не проверяются, только существование файла.

    python3 scripts/check-links.py                 # сводка по каталогам верхнего уровня
    python3 scripts/check-links.py --section fans  # подробный список целей раздела и их источников
    python3 scripts/check-links.py --all           # подробно по всем разделам

Только стандартная библиотека; запускать после `hugo` (или при работающем `hugo server`
с --renderToDisk, он сам обновляет public/).
"""
import argparse, collections, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, unquote

ASSET = re.compile(r'\.(jpe?g|gif|png|svg|webp|pdf|zip|xls|gz|txt|css|js|ico|mp3|doc|xml|swf|wav|ttf|woff2?)$', re.I)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.hrefs.append(a['href'])

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('--public', default=os.path.join(root, 'public'))
    ap.add_argument('--section', help='каталог верхнего уровня (например fans, Parodies, Images)')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    try:
        base = json.load(open(os.path.join(root, 'hugo.json')))['baseURL']
    except Exception:
        base = 'https://example.org/'
    prefix = urlparse(base).path.rstrip('/')

    existing = set()
    for dp, dn, fn in os.walk(args.public):
        for f in fn:
            existing.add('/' + os.path.relpath(os.path.join(dp, f), args.public).replace(os.sep, '/'))

    missing = collections.defaultdict(set)   # цель -> источники
    for dp, dn, fn in os.walk(args.public):
        for f in fn:
            if not f.endswith('.html'):
                continue
            src = '/' + os.path.relpath(os.path.join(dp, f), args.public).replace(os.sep, '/')
            if src.startswith('/pagefind/'):
                continue
            p = Links(); p.feed(open(os.path.join(dp, f), encoding='utf-8', errors='replace').read())
            for h in p.hrefs:
                if not h or h.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
                    continue
                u = urlparse(h)
                if u.scheme in ('http', 'https'):
                    if u.netloc != urlparse(base).netloc:
                        continue
                    path = u.path
                elif u.scheme:
                    continue
                else:
                    path = urljoin(src, u.path or src)
                path = unquote(path)
                if prefix and path.startswith(prefix + '/'):
                    path = path[len(prefix):]
                if path.endswith('/'):
                    path += 'index.html'
                if ASSET.search(path) or not path.endswith('.html'):
                    continue
                if path not in existing:
                    missing[path].add(src)

    def top(path):
        parts = path.lstrip('/').split('/')
        return parts[0] if len(parts) > 1 else '(корень)'

    groups = collections.defaultdict(list)
    for t, srcs in missing.items():
        groups[top(t)].append((t, sorted(srcs)))
    print('Битых внутренних целей: %d (ссылок-источников всего %d)' % (
        len(missing), sum(len(s) for s in missing.values())))
    for sec, lst in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print('  %-12s целей %3d, страниц-источников %3d' % (sec, len(lst), sum(len(s) for _, s in lst)))
    show = [args.section] if args.section else (list(groups) if args.all else [])
    for sec in show:
        print('\n== %s ==' % sec)
        for t, srcs in sorted(groups.get(sec, []), key=lambda x: (-len(x[1]), x[0])):
            print('  %-34s <- %s' % (t, ', '.join(srcs[:4]) + (' …' if len(srcs) > 4 else '')))
    return 0

if __name__ == '__main__':
    sys.exit(main())
