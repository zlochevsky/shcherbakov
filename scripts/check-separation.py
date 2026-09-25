#!/usr/bin/env python3
"""Проверка границы «витрина / фан-клуб» по собранному сайту (public/).

Идея: сайт — «два сайта в одном». ВИТРИНА (песни, каталоги, диски, книги,
концерты, био, новости, лог, магазин ...) не должна ссылаться в текстах и
навигации страниц на КЛУБ (Отзывы, Социология, Комментарии, Картинки,
Фан-клуб, Пародии, Баннеры ...). Обратное направление (клуб -> витрина)
разрешено: статья о песне должна вести к песне.

Что считается «дверью» и разрешено всегда: ссылки в меню/подвале, то есть
вне <main> и вне <ul class="cornernav">. Контекстные ссылки (в тексте страницы
и в cornernav) из витрины в клуб — нарушение, кроме явных исключений ниже.

Запуск (после `hugo`):
    python3 scripts/check-separation.py              # отчёт, код возврата 0
    python3 scripts/check-separation.py --strict     # код 1, если есть нарушения
    python3 scripts/check-separation.py --github     # ещё и ::warning:: для Actions

Только стандартная библиотека.
"""
import argparse, collections, fnmatch, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, unquote

# ─── Разметка сайта ──────────────────────────────────────────────────────────
# КЛУБ: всё, что по решению владельца относится к «фан-клубу и материалам».
# Картинки целиком (включая афиши и «Вокруг дисков») — в клубе (2026-09-23).
CLUB = [
    '/praises.html', '/Praises/*',                 # Отзывы
    '/sociology.html', '/FOM/*', '/SCH2/*',        # Социология
    '/fans/*',                                     # Фан-клуб, Комментарии (fans/kom.html), Смирнов, ...
    '/Images/*',                                   # Картинки
    '/Parodies/*', '/Banners/*',                   # Пародии, Баннеры
    '/kniga_pamyati.html',                         # Память
]
# НЕЙТРАЛЬНЫЕ: пока не отнесены ни к витрине, ни к клубу — не проверяются
# ни как источник, ни как цель. Переводы (English/, fans/utf/{esperanto,german,
# hebrew,ukrain,francais}) — слой ОСНОВНОГО сайта (решение 2026-09-24), не клуб;
# пока не перенесены, URL-схема не выбрана. При переносе под fans/ они попадут в
# CLUB по префиксу — поэтому сначала выбрать URL, см. docs/site-structure-analysis.md §6.
NEUTRAL = [
    '/no.html',        # «Нужно!» — что хотелось бы заполучить в коллекцию
    '/English/*',      # английские страницы (там же переводы) — решить отдельно
]
# Всё остальное — ВИТРИНА.

# ─── Исключения: (страница-источник, цель, причина). '*' — любая цель. ───────
ALLOW = [
    ('/log.html',   '*', 'хроника обновлений: ссылки на материалы допустимы (решение владельца 2026-09-23)'),
    ('/about.html', '*', 'перечень разделов сайта'),
    ('/index.html', '*', 'двери главной страницы (меню подвала, строка «Отзывы и критика»); политика меню — отдельное решение'),
    # Новости: три ссылки внизу страницы, их немного и они сосредоточены в одном
    # месте — оставлены сознательно (решение владельца 2026-09-24, «субъективно, пусть»).
    ('/news.html', '/Images/afish.html',   'афиши в Новостях (внизу страницы, немного)'),
    ('/news.html', '/Images/banners.html', 'баннеры в Новостях (внизу страницы, немного)'),
    # Архив концертов (витрина): три ссылки в тексте индекса оставлены сознательно
    # (решение владельца 2026-09-25). Шапка Архива на афиши/баннеры не ссылается.
    ('/Archive/index.html', '/Praises/annin.html',    'отзыв А. Аннинского (диск «Российские барды»)'),
    ('/Archive/index.html', '/Praises/xazagpre.html', 'предисловие Г. Хазагерова к «Тринадцати дискам»'),
    ('/Archive/index.html', '/kniga_pamyati.html',    'обращение о «Книге памяти»'),
    # Био оставлено как есть (решение владельца 2026-09-23), кроме афиш и баннеров.
    ('/bio.html', '/praises.html',           'навигация страницы Био'),
    ('/bio.html', '/Praises/bo.html',        'высказывание Б. Окуджавы о Щербакове'),
    ('/bio.html', '/Praises/kim140303.html', 'вступительное слово Ю. Кима'),
    ('/bio.html', '/FOM/xran.html',          'экспертный опрос ФОМ'),
    ('/bio.html', '/Images/VV_pic.html',     'иллюстрации к сборнику «Вишнёвое варенье»'),
]

# ─── Разбор HTML ─────────────────────────────────────────────────────────────
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main = 0; self.nav = 0; self.stack = []; self.has_main = False
        self.links = []     # (слой, href)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main':
            self.main += 1; self.has_main = True
        if tag == 'ul' and 'cornernav' in (a.get('class') or ''):
            self.nav += 1; self.stack.append('nav')
        elif tag == 'ul' and self.nav:
            self.stack.append('ul')
        if tag == 'a' and a.get('href'):
            layer = 'nav' if self.nav else ('content' if self.main else 'menu')
            self.links.append((layer, a['href']))
    def handle_endtag(self, tag):
        if tag == 'main':
            self.main -= 1
        if tag == 'ul' and self.stack:
            if self.stack.pop() == 'nav':
                self.nav -= 1

ASSET = re.compile(r'\.(jpe?g|gif|png|svg|webp|pdf|zip|xls|gz|txt|css|js|ico|mp3|doc|xml|swf|wav)$', re.I)

def matches(path, patterns):
    return any(fnmatch.fnmatch(path, p) for p in patterns)

def kind(path):
    if matches(path, NEUTRAL): return 'neutral'
    if matches(path, CLUB): return 'club'
    return 'show'

def resolve(page_url, href, base):
    if not href or href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
        return None
    u = urlparse(href)
    if u.scheme in ('http', 'https'):
        b = urlparse(base)
        if u.netloc != b.netloc:
            return None
        path = u.path
    elif u.scheme:
        return None
    else:
        path = urljoin(page_url, u.path or page_url)
    path = unquote(path)
    prefix = urlparse(base).path.rstrip('/')
    if prefix and path.startswith(prefix + '/'):
        path = path[len(prefix):]
    if path.endswith('/'):
        path += 'index.html'
    if ASSET.search(path):
        return None
    return path

def allowed(src, dst):
    for s, d, why in ALLOW:
        if fnmatch.fnmatch(src, s) and (d == '*' or fnmatch.fnmatch(dst, d)):
            return why
    return None

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('--public', default=os.path.join(root, 'public'))
    ap.add_argument('--strict', action='store_true', help='код возврата 1 при нарушениях')
    ap.add_argument('--github', action='store_true', help='печатать ::warning:: для GitHub Actions')
    ap.add_argument('--list-allowed', action='store_true', help='подробно показать разрешённые исключения')
    args = ap.parse_args()

    try:
        base = json.load(open(os.path.join(root, 'hugo.json')))['baseURL']
    except Exception:
        base = 'https://example.org/'

    counts = collections.Counter()
    violations = collections.OrderedDict()   # (src, layer, dst) -> n
    excepted = collections.Counter()         # (src, причина) -> n
    doors = collections.Counter()            # src -> n (меню/подвал)
    for dp, dn, fn in os.walk(args.public):
        for f in sorted(fn):
            if not f.endswith('.html'):
                continue
            full = os.path.join(dp, f)
            src = '/' + os.path.relpath(full, args.public).replace(os.sep, '/')
            k = kind(src)
            counts[k] += 1
            if k != 'show':
                continue
            p = Page()
            p.feed(open(full, encoding='utf-8', errors='replace').read())
            for layer, href in p.links:
                dst = resolve(src, href, base)
                if not dst or dst == src or kind(dst) != 'club':
                    continue
                if layer == 'menu':
                    doors[src] += 1
                    continue
                why = allowed(src, dst)
                if why:
                    excepted[(src, why)] += 1
                else:
                    violations[(src, layer, dst)] = violations.get((src, layer, dst), 0) + 1

    print('Граница «витрина / фан-клуб» — проверка %s' % args.public)
    print('Страниц: витрина %d, клуб %d, нейтральные %d' % (counts['show'], counts['club'], counts['neutral']))
    print('Двери (меню/подвал, вне <main> и cornernav): %d ссылок на %d страницах' % (sum(doors.values()), len(doors)))
    print('Разрешено по списку исключений: %d ссылок' % sum(excepted.values()))
    if args.list_allowed:
        for (src, why), n in sorted(excepted.items()):
            print('   %-16s ×%-3d %s' % (src, n, why))
    print('НАРУШЕНИЙ (витрина → клуб вне исключений): %d' % sum(violations.values()))
    for (src, layer, dst), n in violations.items():
        print('   %-28s [%s] → %s%s' % (src, layer, dst, ' ×%d' % n if n > 1 else ''))
        if args.github:
            print('::warning title=Граница витрина/клуб::%s [%s] ссылается на %s' % (src, layer, dst))
    if violations and args.strict:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
