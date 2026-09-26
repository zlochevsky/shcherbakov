#!/usr/bin/env python3
"""Конвертер legacy fans/*.html -> тело Hugo-страницы (praises-article)."""
import re, sys, os, json
from bs4 import BeautifulSoup, Comment, NavigableString, Doctype

SRC = '/mnt/nas/diskh/sch/sch.com.ru/www/' + os.environ.get('SECTION', 'fans') + '/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/out/'
CONTENT = '/home/sergius/schugo/content/'

INLINE = {'a','b','i','em','strong','span','sup','sub','u','small','big','br','img','s','tt','cite','code','abbr','font','nobr','strike'}
BLOCKS = {'p','div','blockquote','ul','ol','li','h1','h2','h3','h4','h5','h6','pre','hr','table','tr','td','th','tbody','thead','dl','dt','dd','center','address'}
VOID = {'br','img','hr'}
KEEP_ATTR = {'a': {'href','id','title'}, 'img': {'src','alt','width','height','title'},
             'td': {'colspan','rowspan'}, 'th': {'colspan','rowspan'}, 'ol': {'start'}, 'li': {'value'}}

NAV_TEXT = re.compile(r'^\s*[\[(].*[\])]\s*$', re.S)
DEBUG = []
KEEP_TABLES = [False]
FONTMAP = {}
SRC_REPLACE = []
SRC_OVERRIDE = {'utf/covers': '/tmp/claude-1000/-home-sergius-schugo/74d79cb2-aaf8-4949-b57e-25f68181bde6/scratchpad/covers.html'}   # имя -> локальный файл, если исходника нет на NAS
SRC_FN = [None]
SPLIT_BR2 = [False]
RAW_QUOTES = [False]
NO_TYPO = [False]

def decode(b, enc):
    return b.decode(enc, 'replace')

def is_nav_link(a, self_name):
    txt = a.get_text()
    if not NAV_TEXT.match(txt):
        return False
    href = a.get('href', '')
    if href.split('#')[0] in ('index.html', '../index.html', 'kom.html', 'kom2.html', '../../index.html', '../fans/index.html', '../Parodies/index.html', '../praises.html', '../news.html',
                              '../index.html', 'crossword.html', '../praises.html') or re.search(r'#top$', href):
        return True
    if href.startswith(self_name + '.html#top'):
        return True
    return False

def strip_nav(soup, self_name):
    for a in list(soup.find_all('a')):
        if a.parent is None:
            continue
        if not is_nav_link(a, self_name):
            continue
        href = a.get('href', '')
        if href.endswith('#top'):      # «Наверх» внутри текста оставляем
            continue
        DEBUG.append('nav removed: %s %s' % (href, a.get_text().strip()))
        parent = a.parent
        a.decompose()
        # следующий <br>
        # удалить li/ul, если стали пустыми
        while parent is not None and parent.name in ('li', 'ul') and not parent.get_text(strip=True) \
                and not parent.find(['img', 'a']):
            p2 = parent.parent
            parent.decompose()
            parent = p2

def rewrite_href(h, self_name, subdir):
    if not h:
        return h
    h0 = h
    h = re.sub(r'^https?://(?:www\.)?blackalpinist\.com/scherbakov/', '/', h)
    h = re.sub(r'^https?://(?:www\.)?lambda\.mkshch\.com/', '/', h)
    if h.startswith('/'):
        # корень старого сайта -> относительно текущего файла
        target = h[1:]
        up = '../' * (1 + (1 if subdir else 0) - 0)
        depth = 1 if not subdir else 2
        # fans/x.html лежит на глубине 1 (fans), memo/x — 2
        h = '../' * depth + target
    h = h.replace('htmtexts/', 'texts/')
    h = re.sub(r'^((?:\.\./)+)fans/Praises/', r'\1Praises/', h)
    h = re.sub(r'(^|/)kom2\.html', r'\1kom.html', h)
    h = re.sub(r'^%s\.html#' % re.escape(self_name), '#', h)
    return h

def fix_text(s):
    s = s.replace('\r', '')
    return s

LAT2CYR = dict(zip('AaBCcEeHKMOoPpTXxy', 'АаВСсЕеНКМОоРрТХху'))
HOMO_COUNT = [0]
def fix_homoglyphs(s):
    def tok(m):
        w = m.group(0)
        if not re.search('[а-яёА-ЯЁ]', w) or not re.search('[A-Za-z]', w):
            return w
        if all(ch in LAT2CYR or not re.match('[A-Za-z]', ch) for ch in w):
            HOMO_COUNT[0] += 1
            return ''.join(LAT2CYR.get(ch, ch) for ch in w)
        return w
    return re.sub(r'[A-Za-zА-Яа-яЁё]+', tok, s)

def dash(s, pre=False):
    sp = r'[ \t]' if pre else r'\s'
    return re.sub(sp + r'(?:-|--|&ndash;|\u2013|\u2014)(' + sp + r'|(?=\n)|$)', lambda m: '\u00a0\u2014' + (m.group(1) or ''), s)

OPEN_Q = ['\u00ab', '\u201e', '\u2018']
CLOSE_Q = ['\u00bb', '\u201c', '\u2019']

def process_quotes(block):
    """Расставляет «ёлочки» вместо прямых кавычек в пределах блока (по всему тексту блока)."""
    items = [n for n in block.descendants if (isinstance(n, NavigableString) and not isinstance(n, Comment)) or getattr(n, 'name', None) == 'br']
    nodes = items
    full = ''.join('\n' if getattr(n, 'name', None) == 'br' else str(n) for n in items)
    res = list(full)
    depth = 0
    for i, ch in enumerate(full):
        if ch in '\u00ab\u201e':
            res[i] = OPEN_Q[min(depth, 2)]
            depth += 1
            continue
        if ch in '\u00bb\u201c':
            depth = max(depth - 1, 0)
            res[i] = CLOSE_Q[min(depth, 2)]
            continue
        if ch != '"':
            continue
        p = full[i-1] if i else ' '
        nx = full[i+1] if i + 1 < len(full) else ' '
        ws = ' \n\t\u00a0'
        if p in ws + '([{\u2014\u2013-/>' :
            opening = not (p in ws and nx in ws + '.,;:!?)' and depth > 0)
        elif p in ':;,.!?)' and nx.isalnum() and depth == 0:
            opening = True
        elif p.isalnum() and nx.isalnum() and depth == 0:
            opening = True
        else:
            opening = False
        if opening:
            res[i] = OPEN_Q[min(depth, 2)]
            depth += 1
        else:
            depth = max(depth - 1, 0)
            res[i] = CLOSE_Q[min(depth, 2)]
    if depth and RAW_QUOTES[0]:
        return depth
    pos = 0
    for n in nodes:
        if getattr(n, 'name', None) == 'br':
            pos += 1
            continue
        L = len(str(n))
        seg = ''.join(res[pos:pos+L])
        if seg != str(n):
            n.replace_with(seg)
        pos += L
    return depth

def esc(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = s.replace(' ', '&nbsp;').replace('—', '&mdash;')
    return s

def attrs(el, name, self_name, subdir):
    out = []
    a = dict(el.attrs)
    if name == 'a' and 'name' in a and 'id' not in a:
        a['id'] = a['name']
    cls = []
    al = str(a.get('align', '')).lower()
    if name == 'span' and a.get('class') in ('spoiler', 'rhyme', 'datum', 'hl'):
        cls.append(a['class'])
    if name in ('p', 'div', 'h1', 'h2', 'h3', 'h4') and al in ('right', 'center'):
        cls.append(al)
    c = a.get('class')
    if c:
        cs = c if isinstance(c, list) else [c]
        for x in cs:
            x = x.lower()
            if x in ('right', 'center') and x not in cls:
                cls.append(x)
    if cls:
        out.append(('class', ' '.join(cls)))
    for k in KEEP_ATTR.get(name, ()):
        if k in a:
            v = a[k]
            if isinstance(v, list): v = ' '.join(v)
            if k == 'href':
                v = rewrite_href(v, self_name, subdir)
            if k == 'src':
                v = re.sub(r'^https?://[^/]+/', '', v) if False else v
            out.append((k, v))
    if name == 'img' and not any(k == 'alt' for k, _ in out):
        out.append(('alt', ''))
    return ''.join(' %s="%s"' % (k, v.replace('&', '&amp;').replace('"', '&quot;')) for k, v in out)

def ser_inline(node, self_name, subdir, in_pre=False):
    if isinstance(node, Comment):
        return '<!--%s-->' % node
    if isinstance(node, Doctype):
        return ''
    if isinstance(node, NavigableString):
        s = str(node)
        if not in_pre:
            s = re.sub(r'[ \t\r\n]+', ' ', s)
        return esc(s)
    n = node.name
    if n in ('font', 'nobr'):
        return ''.join(ser_inline(c, self_name, subdir, in_pre) for c in node.children)
    if n == 'br':
        return '<br>'
    if n == 'img':
        return '<img%s>' % attrs(node, n, self_name, subdir)
    inner = ''.join(ser_inline(c, self_name, subdir, in_pre) for c in node.children)
    if n == 'strike': n = 's'
    if n == 'subj':
        return '&lt;subj&gt;' + inner
    if n in ('span',) and not attrs(node, n, self_name, subdir):
        return inner
    return '<%s%s>%s</%s>' % (n, attrs(node, n, self_name, subdir), inner, n)

def has_block_child(el):
    return any(getattr(c, 'name', None) in BLOCKS for c in el.children)

def tidy_inline(s):
    s = re.sub(r'(<(?:a|b|i|em|strong)(?: [^>]*)?>)[ \t\n]+', r'\1', s)
    s = re.sub(r'([ \t\n]+)(</(?:a|b|i|em|strong)>)', r'\2\1', s)
    s = re.sub(r'(<br>)\s+', r'\1', s)
    s = re.sub(r'\s+(<br>)', r'\1', s)
    s = re.sub(r'^\s+|\s+$', '', s)
    s = re.sub(r'^(?:<br>)+|(?:<br>)+$', '', s)
    s = re.sub(r'^\s+|\s+$', '', s)
    return s

def ser_container(el, self_name, subdir):
    out = []
    buf = []
    def flush():
        t = tidy_inline(''.join(buf))
        if t:
            out.append(t if re.fullmatch(r'(?:<!--.*?-->\s*)+', t, re.S) else '<p>%s</p>' % t)
        buf.clear()
    for c in el.children:
        if getattr(c, 'name', None) in BLOCKS:
            flush()
            out += ser_block(c, self_name, subdir)
        elif isinstance(c, Comment) and not tidy_inline(''.join(buf)):
            flush()
            out.append('<!--%s-->' % c)
        else:
            buf.append(ser_inline(c, self_name, subdir))
    flush()
    return out

def ser_block(el, self_name, subdir, level=0):
    """Возвращает список строк (блоков верхнего уровня)."""
    lines = []
    if isinstance(el, Comment):
        return ['<!--%s-->' % el]
    if isinstance(el, Doctype):
        return []
    if isinstance(el, NavigableString):
        s = re.sub(r'[ \t\r\n]+', ' ', str(el)).strip()
        return [esc(s)] if s else []
    n = el.name
    if n in ('center',):
        if has_block_child(el):
            return ser_container(el, self_name, subdir)
        inner = tidy_inline(''.join(ser_inline(c, self_name, subdir) for c in el.children))
        return ['<p class="center">%s</p>' % inner] if inner else []
    if n == 'pre':
        inner = ''.join(ser_inline(c, self_name, subdir, True) for c in el.children)
        inner = inner.strip('\n')
        import textwrap
        inner = textwrap.dedent(inner.replace('\t', '        ')).rstrip()
        inner = re.sub(r'\n\s*\n+', '\n', inner) if False else inner
        return ['<pre>%s</pre>' % inner]
    if n in ('li', 'dd', 'dt', 'dl') and level == 0:
        return ser_container(el, self_name, subdir)
    if n in ('ul', 'ol') and not any(getattr(c, 'name', None) == 'li' for c in el.children):
        return ser_container(el, self_name, subdir)
    if n in ('ul', 'ol'):
        items = []
        for c in el.children:
            if getattr(c, 'name', None) == 'li':
                items += ser_li(c, self_name, subdir)
            elif isinstance(c, Comment):
                items.append('<!--%s-->' % c)
            elif isinstance(c, NavigableString) and not str(c).strip():
                pass
            else:
                items += ser_block(c, self_name, subdir)
        return ['<%s%s>' % (n, attrs(el, n, self_name, subdir))] + items + ['</%s>' % n]
    if n == 'hr':
        return ['<hr>']
    if n == 'table' and KEEP_TABLES[0]:
        rows = []
        for tr in el.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th'], recursive=False):
                for hr in td.find_all('hr'):
                    hr.decompose()
                inner = tidy_inline(''.join(ser_inline(c, self_name, subdir) for c in td.children)).replace('&nbsp;', '').strip()
                if inner:
                    cells.append((td.name, tidy_inline(''.join(ser_inline(c, self_name, subdir) for c in td.children))))
            if cells:
                rows.append(cells)
        out = ['<table>']
        for cells in rows:
            out.append('<tr>' + ''.join('<%s>%s</%s>' % (t, c, t) for t, c in cells) + '</tr>')
        out.append('</table>')
        return out
    if n in ('table', 'tbody', 'thead', 'tr', 'td', 'th'):
        # тривиально: разворачиваем таблицу-обёртку (проверяется вручную)
        if n == 'table':
            DEBUG.append('TABLE unwrapped')
        return ser_container(el, self_name, subdir)
    if n in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'div', 'li', 'dd', 'dt', 'address'):
        if n in ('blockquote', 'div', 'li', 'dd') and has_block_child(el):
            # смешанное: собираем «висячий» инлайн в <p>
            out = []
            buf = []
            def flush():
                s = tidy_inline(''.join(buf))
                if s:
                    out.append('<p>%s</p>' % s if n != 'div' else '<p>%s</p>' % s)
                buf.clear()
            for c in el.children:
                if getattr(c, 'name', None) in BLOCKS:
                    flush()
                    out += ser_block(c, self_name, subdir)
                else:
                    buf.append(ser_inline(c, self_name, subdir))
            flush()
            if n == 'div':
                return out
            return ['<%s%s>' % (n, attrs(el, n, self_name, subdir))] + out + ['</%s>' % n]
        inner = tidy_inline(''.join(ser_inline(c, self_name, subdir) for c in el.children))
        if not inner:
            return []
        if n == 'div':
            return ['<p%s>%s</p>' % (attrs(el, 'p', self_name, subdir), inner)]
        return ['<%s%s>%s</%s>' % (n, attrs(el, n, self_name, subdir), inner, n)]
    # инлайн-элемент на верхнем уровне
    s = ser_inline(el, self_name, subdir)
    return [s] if s.strip() else []

def ser_li(li, self_name, subdir):
    if has_block_child(li):
        out = []
        buf = []
        def flush():
            s = tidy_inline(''.join(buf))
            if s: out.append(s)
            buf.clear()
        for c in li.children:
            if getattr(c, 'name', None) in BLOCKS:
                flush()
                out += ser_block(c, self_name, subdir)
            else:
                buf.append(ser_inline(c, self_name, subdir))
        flush()
        # первая строка — текст li
        if out and not out[0].startswith('<'):
            head = out[0]
            return ['<li>' + head] + out[1:] + ['</li>']
        return ['<li>'] + out + ['</li>']
    inner = tidy_inline(''.join(ser_inline(c, self_name, subdir) for c in li.children))
    return ['<li%s>%s</li>' % (attrs(li, 'li', self_name, subdir), inner)]

def wrap_paragraphs(body):
    """Голый текст/инлайны верхнего уровня, разделённые <p> (в источнике <P> без закрытия) — html5lib уже закрыл.
    Оставшийся висячий инлайн между блоками оборачиваем в <p>."""
    pass

def wrap_loose(body):
    for el in [body] + body.find_all(['div', 'td', 'blockquote', 'center', 'dd']):
        if not has_block_child(el) and el is not body:
            continue
        run = []
        def flush():
            if run and any((isinstance(x, NavigableString) and not isinstance(x, Comment) and str(x).strip()) or getattr(x, 'name', None) in ('img', 'a', 'b', 'i', 'em', 'strong', 'u') for x in run):
                p = BeautifulSoup('', 'html5lib').new_tag('p')
                run[0].insert_before(p)
                for x in run:
                    p.append(x.extract())
            run.clear()
        for c in list(el.children):
            if getattr(c, 'name', None) in BLOCKS:
                flush()
            else:
                run.append(c)
        flush()

def convert(name, enc='koi8-r', subdir=None):
    raw = open(SRC_OVERRIDE.get(name) or (SRC + name + '.html'), 'rb').read()
    html = decode(raw, enc)
    if SRC_FN[0]:
        html = SRC_FN[0](html)
    for a, b in SRC_REPLACE:
        if a not in html:
            DEBUG.append('src_replace not found: ' + a[:40])
        html = html.replace(a, b)
    html = re.sub(r'<a\s+name=["\']?([\w-]+)["\']?\s*/>', r'<a name="\1"></a>', html, flags=re.I)
    soup = BeautifulSoup(html, 'html5lib')
    self_name = os.path.basename(name)
    subdir = '/' in name
    title = soup.title.get_text().strip() if soup.title else ''
    body = soup.body
    for f in body.find_all('font'):
        cls = FONTMAP.get((f.get('color') or '').lower())
        if cls:
            f.name = 'span'; f.attrs = {'class': cls}
        else:
            f.unwrap()
    for f in body.find_all('nobr'):
        f.unwrap()
    for f in body.find_all('span'):
        if f.get('class') and has_block_child(f):
            for c in list(f.children):
                if getattr(c, 'name', None) in BLOCKS:
                    inner = BeautifulSoup('', 'html5lib').new_tag('span')
                    inner.attrs = dict(f.attrs)
                    for x in list(c.children):
                        inner.append(x.extract())
                    c.append(inner)
            f.unwrap()
    for f in body.find_all('span'):
        cl = f.get('class') or []
        if 'GreenText' in cl:
            f.name = 'b'; f.attrs = {}
        elif not f.attrs:
            f.unwrap()
        else:
            f.attrs = {k: v for k, v in f.attrs.items()}
    known = INLINE | BLOCKS | {'tbody', 'thead', 'tfoot', 'colgroup', 'col', 'caption', 'body', 'html', 'head'}
    for tag in list(body.find_all(True)):
        if tag.name not in known:
            tag.insert_before('<%s>' % tag.name)
            tag.unwrap()
    for p in body.find_all('p'):
        if has_block_child(p):
            p.name = 'div'
    for p in body.find_all(['ul', 'ol']):
        if not any(getattr(c, 'name', None) == 'li' for c in p.children):
            p.name = 'div'
    strip_nav(body, self_name)
    wrap_loose(body)
    # кавычки в блоках
    for el in body.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'pre', 'div', 'td', 'center', 'dd', 'dt']):
        pass
    # тире и кавычки на уровне текстовых узлов
    for t in list(body.descendants):
        if isinstance(t, NavigableString) and not isinstance(t, (Comment, Doctype)):
            if t.find_parent('pre'):
                s = str(t)
            else:
                s = re.sub(r'[ \t\r\n]+', ' ', str(t))
            s2 = s if NO_TYPO[0] else fix_homoglyphs(dash(s, bool(t.find_parent('pre'))))
            if not NO_TYPO[0]:
                prev = t.previous_sibling
                if re.match(r'^(?:-|--|\u2013)\s', s2) and (prev is None or getattr(prev, 'name', None) == 'br' or (isinstance(prev, NavigableString) and not str(prev).strip())):
                    s2 = re.sub(r'^(?:-|--|\u2013)\s', '\u2014 ', s2)
            if s2 != str(t):
                t.replace_with(s2)
    # кавычки: по «листовым» блокам
    leafs = []
    for el in body.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'pre', 'div', 'td', 'th', 'dd', 'dt', 'center']):
        if not has_block_child(el):
            leafs.append(el)
    # текст вне блоков (напрямую в body) — как один блок
    for el in ([] if NO_TYPO[0] else leafs):
        d = process_quotes(el)
        if d != 0:
            DEBUG.append('quote imbalance (%d) in: %s' % (d, el.get_text()[:70].replace('\n', ' ')))
    blocks = []
    buf = []
    def flush():
        s = tidy_inline(''.join(buf))
        if s:
            blocks.append(s if re.fullmatch(r'(?:<!--.*?-->\s*)+', s, re.S) else '<p>%s</p>' % s)
        buf.clear()
    for c in body.children:
        if getattr(c, 'name', None) in BLOCKS:
            flush()
            blocks += ser_block(c, self_name, subdir)
        elif isinstance(c, Comment):
            if tidy_inline(''.join(buf)):
                buf.append('<!--%s-->' % c)
            else:
                blocks.append('<!--%s-->' % c)
        elif isinstance(c, Doctype):
            pass
        else:
            buf.append(ser_inline(c, self_name, subdir))
    flush()
    return title, blocks

def post(blocks):
    out=[]
    for b in blocks:
        if re.fullmatch(r'<p><a id="top">\s*</a></p>|<li><a id="top"></a></li>', b):
            continue
        if re.fullmatch(r'<li><a href="#top">\[?Наверх\]?</a></li>', b):
            continue
        if re.fullmatch(r'<p>(?:&nbsp;|<br>|\s)*</p>', b):
            continue
        if b in ('<ul>', '</ul>', '<ol>', '</ol>'):
            out.append(b); continue
        ml = re.fullmatch(r'<li>(.*)</li>', b, re.S)
        if ml and not any(x in ('<ul>', '<ol>') for x in out[-1:]) and out.count('<ul>') + out.count('<ol>') == out.count('</ul>') + out.count('</ol>'):
            b = '<p>%s</p>' % ml.group(1)
        b = re.sub(r'<b>((?:<br>)+)', r'\1<b>', b)
        if SPLIT_BR2[0]:
            mm = re.fullmatch(r'<p(?: class="verse")?>(.*)</p>', b, re.S)
            if mm and '<br><br>' in mm.group(1):
                for piece in mm.group(1).split('<br><br>'):
                    piece = re.sub(r'^(?:<br>)+|(?:<br>)+$', '', piece)
                    if not piece.strip():
                        continue
                    h = re.fullmatch(r'<a id="([^"]+)"><b>(.*?)</b></a>', piece)
                    out.append('<h2 id="%s">%s</h2>' % h.groups() if h else '<p class="verse">%s</p>' % piece)
                continue
        m = re.fullmatch(r'<p>(.*)</p>', b, re.S)
        if m and b.count('<br>') >= 3:
            lines = m.group(1).split('<br>')
            if sum(len(re.sub(r'<[^>]+>', '', l)) for l in lines) / len(lines) < 70:
                b = '<p class="verse">%s</p>' % m.group(1)
        out.append(b)
    txt = '\n'.join(out)
    txt = re.sub(r'<a id="top">\s*</a>', '', txt)
    for _ in range(3):
        txt = re.sub(r'<(i|b|em)>\s*<\1>((?:(?!</?\1>).)*?)</\1>\s*</\1>', r'<\1>\2</\1>', txt, flags=re.S)
    txt = re.sub(r'\n*<p>(?:<i>)?<a href="#top">\[?(?:Top\s*\u2022\s*)?(?:Наверх|К началу)\]?</a>(?:</i>)?</p>\s*$', '', txt)
    txt = re.sub(r'<ul>\s*</ul>', '', txt)
    txt = re.sub(r'<p>\s*</p>', '', txt)
    txt = re.sub(r'<p>(?:<(?:b|i)>\s*</(?:b|i)>)+</p>', '', txt)
    txt = txt.strip('\n')
    txt = re.sub(r'^(?:<hr>\n+)+|(?:\n+<hr>)+$', '', txt)
    txt = re.sub(r'^\s+|\s+$', '', txt)
    return [x for x in txt.split('\n') if x.strip()] if False else txt.split('\n')

def render(blocks):
    """Склейка: блок-элементы разделяются пустой строкой, внутри — без пустых строк."""
    out = []
    for b in blocks:
        out.append(b)
    text = '\n'.join(out)
    # пустая строка между «плоскими» блоками
    text = re.sub(r'(</(?:p|h[1-6]|blockquote|ul|ol|pre|div)>|<hr>|-->)\n(?=<(?:p|h[1-6]|blockquote|ul|ol|pre|hr|!--|div)\b|<!--)', r'\1\n\n', text)
    parts = re.split(r'(<pre>.*?</pre>)', text, flags=re.S)
    parts = [x if x.startswith('<pre>') else re.sub(r' +&nbsp;&mdash;', '&nbsp;&mdash;', x) for x in parts]
    return ''.join(parts) + '\n'

if __name__ == '__main__':
    name = sys.argv[1]
    enc = sys.argv[2] if len(sys.argv) > 2 else 'koi8-r'
    title, blocks = convert(name, enc)
    os.makedirs(OUT + os.path.dirname(name), exist_ok=True)
    body = render(post(blocks))
    open(OUT + name + '.body', 'w').write(body)
    print('TITLE:', title)
    for d in DEBUG:
        print('  !', d)
