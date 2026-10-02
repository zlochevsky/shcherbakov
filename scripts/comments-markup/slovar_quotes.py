"""Расстановка кавычек в теле заметки «Словаря»: «ёлочки» → „лапки“ → ‘одиночные’ по глубине.
Обрабатывает только текст (не атрибуты тегов): прямые ", &quot;, а также уже стоящие &laquo; &raquo; &bdquo; &ldquo;.
Результат — с HTML-сущностями (как в остальном исходнике). Глубина сбрасывается на границах блоков (<p>, </p>, <blockquote>, <br> не сбрасывает)."""
import re

OPEN = ['&laquo;', '&bdquo;', '&lsquo;']
CLOSE = ['&raquo;', '&ldquo;', '&rsquo;']
BLOCK = re.compile(r'</?(?:p|blockquote|ul|li|div)\b', re.I)
TOKEN = re.compile(r'(<[^>]+>)')
ENT = re.compile(r'&(laquo|raquo|bdquo|ldquo|quot);|["«»„“]')


def normalize_quotes(body, report=None):
    parts = TOKEN.split(body)
    depth = 0
    prev = ' '
    # предварительно найдём следующий символ текста для каждой кавычки: упрощённо — по тексту после
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:  # тег
            if BLOCK.match(p):
                if depth and report is not None:
                    report.append('глубина %d на границе блока' % depth)
                depth = 0
                prev = ' '
            elif re.match(r'<br\b', p, re.I):
                prev = ' '
            out.append(p)
            continue
        res = []
        pos = 0
        for m in ENT.finditer(p):
            res.append(p[pos:m.start()])
            pos = m.end()
            tok = m.group(0)
            prevc = (p[m.start()-1] if m.start() else prev)
            nxt = p[m.end()] if m.end() < len(p) else ' '
            if tok in ('&laquo;', '«', '&bdquo;', '„'):
                opening = True
            elif tok in ('&raquo;', '»', '&ldquo;', '“'):
                opening = False
            else:  # прямая
                ws = ' \n\t '
                if prevc in ws + '([{—–-/':
                    opening = not (prevc in ws and nxt in ws + '.,;:!?)' and depth > 0)
                elif prevc in ':;,.!?)' and nxt.isalnum() and depth == 0:
                    opening = True
                elif prevc.isalnum() and nxt.isalnum() and depth == 0:
                    opening = True
                else:
                    opening = False
            if opening:
                res.append(OPEN[min(depth, 2)])
                depth += 1
            else:
                depth = max(depth - 1, 0)
                res.append(CLOSE[min(depth, 2)])
            prev = res[-1][-1]
        res.append(p[pos:])
        s = ''.join(res)
        out.append(s)
        tail = re.sub(r'&\w+;', 'x', p)
        if tail:
            prev = tail[-1]
    if depth and report is not None:
        report.append('глубина %d в конце' % depth)
    return ''.join(out)
