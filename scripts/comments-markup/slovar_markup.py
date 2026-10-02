"""Приведение тела заметки «Словаря» к единой разметке (используется импортом и разовыми правками БД).

Правила (решения владельца 2026-09-26):
 1. Кавычки — «ёлочки» → „лапки“ → ‘одиночные’ (slovar_quotes.normalize_quotes).
 2. Старые <em> (цитаты из песни) → <i>; <b>/<strong> (смысловое выделение, эмфаза) → <em> (тело заметки; заголовок статьи в body не входит).
    Курсив <i> — слова самого автора: цитаты из этой песни И её варианты («вариант: <i>«…»</i>», «ранняя концовка»); чужие цитаты и названия произведений без выделения (это решает человек:
    скрипт курсив не расставляет и не снимает).
 3. Объясняемое слово в начале абзаца («Слово — пояснение», «Слово (этимология) — пояснение», «"Слово" (…) — …») → <dfn>…</dfn>.
    Кавычки вокруг такого слова снимаются (их заменяет выделение). Регистр CAPS у объясняемого слова сбрасывается:
    первое слово с заглавной, остальные строчные (собственные имена внутри — через CAPS_FIX или вручную по отчёту).
 4. Разделитель строк «/» внутри строки стиха: «слово&nbsp;// слово» (адреса, даты, «и/или» не трогаются, сомнительное — в отчёт).
 5. Тире: « - », « &ndash; » → «&nbsp;&mdash; »; <blockquote> внутри <p> выносится из абзаца.
 6. Прочие слова капсом (≥5 букв) — только в отчёт.
"""
import re
from slovar_quotes import normalize_quotes

CAPS_FIX = {  # готовые написания для заголовочных слов, где простое «первая заглавная» неверно
    'БАБ-ЭЛЬ-МАНДЕБСКИЙ ПРОЛИВ': 'Баб-эль-Мандебский пролив',
}

DASH = r'(?:&ndash;|&mdash;|–|—|-)'
QOPEN = r'(?:&laquo;|&quot;|"|«)'
QCLOSE = r'(?:&raquo;|&quot;|"|»)'
# начало абзаца: <p ...> и пробелы, затем термин, необязательные скобки, тире
HEAD = re.compile(
    r'(?P<lead>(?:^|<p\b[^>]*>)\s*)'
    r'(?P<term>(?:' + QOPEN + r'(?P<qterm>[^<>"«»]{1,60}?)' + QCLOSE + r'|(?P<pterm>[^<>()"«»&;]{1,60}?)))'
    r'(?P<paren>\s*\([^<>]{0,160}\))?'
    r'(?P<sep>(?:\s|&nbsp;)+' + DASH + r'(?:\s|&nbsp;)+)',
    re.S)


NOT_TERMS = {'мелодия', 'размер', 'размер и тема', 'метр', 'ритм', 'тема', 'рифма', 'музыка', 'текст', 'стихи', 'неофициальное название', 'название', 'вариант', 'другое название', 'название песни', 'эпиграф', 'похожий сюжет', 'история любви', 'другое название песни', 'автор наблюдения', 'в подтексте'}


def decap(term, report):
    letters = re.findall(r'[A-Za-zА-Яа-яЁё]+', term)
    if not any(len(w) >= 5 for w in letters) or term != term.upper():
        return term
    if term in CAPS_FIX:
        return CAPS_FIX[term]
    new = term.lower()
    new = new[:1].upper() + new[1:]
    report.append('CAPS-заголовок: %r → %r (проверить имена собственные)' % (term, new))
    return new


def add_dfn(body, report):
    def rep(m):
        term = m.group('qterm') if m.group('qterm') is not None else m.group('pterm')
        term = term.strip()
        # слишком похоже на обычную фразу — не трогаем: длинный термин или заканчивается на знак препинания/предлог
        if len(term.split()) > 4 or re.search(r'[.,:;!?]$', term) or not re.match(r'[«"\'A-Za-zА-ЯЁа-яё0-9]', term):
            return m.group(0)
        if re.match(r'(?i)(см|ср|напр|т\.\s?е)\b', term) or term.lower() in NOT_TERMS:
            return m.group(0)
        term = decap(term, report)
        return m.group('lead') + '<dfn>' + term + '</dfn>' + (m.group('paren') or '') + m.group('sep')
    # применяем только к началу каждого абзаца (finditer с якорем в lead)
    return HEAD.sub(rep, body)


CAPSHEAD = re.compile(
    r'(?P<lead>(?:^|<p\b[^>]*>)\s*)(?P<term>[А-ЯЁA-Z][А-ЯЁA-Z\- ]{3,60}[А-ЯЁA-Z])(?=,|\s+\(|(?:\s|&nbsp;)+' + DASH + r')')


def add_caps_head(body, report):
    def rep(m):
        term = m.group('term')
        if not any(len(w) >= 5 for w in re.findall(r'[А-ЯЁA-Z]+', term)):
            return m.group(0)
        return m.group('lead') + '<dfn>' + decap(term, report) + '</dfn>'
    return CAPSHEAD.sub(rep, body)


def verse_slashes(body, report):
    """Разделитель строк «/» в стихотворной цитате внутри строки: неразрывный пробел перед знаком, обычный после; всегда двойной «//»."""
    SP = r'(?:\s|&nbsp;)'
    parts = re.split(r'(<[^>]+>)', body)
    for i in range(0, len(parts), 2):
        t = parts[i]
        if '/' not in t:
            continue
        out = []
        pos = 0
        for m in re.finditer(SP + '*/{1,2}' + SP + '*', t):
            a, b = m.start(), m.end()
            ltok = re.search(r'\S*$', t[:a]).group(0)
            rtok = re.match(r'\S*', t[b:]).group(0)
            ws = bool(re.search(r'\S', m.group(0).replace('/', ''))) or m.group(0) != '/'
            if '://' in ltok + rtok or re.search(r'\w\.\w', ltok) or re.search(r'\w\.\w', rtok) or 'www' in ltok:
                continue                                       # адреса, домены, «т.е./т.п.»
            if re.search(r'\d$', ltok) and re.match(r'\d', rtok):
                continue                                       # 1/2, 12/06
            if not t[:a] or not t[b:]:
                continue
            if set(m.group(0)) == {'/'}:                              # без пробелов с обеих сторон
                nx = t[b:b + 1]
                if not (nx.isupper() or nx in '«„[\u2018\u2026' or re.search(r'[.,!?;:\u2026)»\u201c]$', ltok)):
                    report.append('«/» без пробелов не тронут: %s/%s' % (ltok[-15:], rtok[:15]))
                    continue
            out.append(t[pos:a])
            out.append('&nbsp;// ')                            # одинарный и двойной слэш → двойной (решение владельца)
            pos = b
        out.append(t[pos:])
        parts[i] = ''.join(out)
    return ''.join(parts)


def dashes(body):
    """« - », « &ndash; », « – » между словами → неразрывный пробел + длинное тире (правило типографики сайта); числовые диапазоны без пробелов не трогаем.
    Отдельно: тире (одно, двойное «--» или короткое), слипшееся с предыдущим знаком препинания без пробела («Сфинкса.- Зачем», «(joker)-- это»)
    — вставляем обычный пробел перед ним, заменяем на длинное тире (это граница фразы, не середина слова — неразрывный пробел тут не нужен)."""
    parts = re.split(r'(<[^>]+>)', body)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'([.)!?])[ \t]*(?:-{1,2}|\u2012|\u2013|\u2014)[ \t]+(?=\S)', r'\1 &mdash; ', parts[i])
        parts[i] = re.sub(r'(?:\s|&nbsp;)+(?:-|&ndash;|\u2013|--)(?=\s|&nbsp;|$)(?:\s|&nbsp;)*', '&nbsp;&mdash; ', parts[i])
        parts[i] = re.sub(r'&mdash;[ \t]*-[ \t]*(?=\S)', '&mdash; ', parts[i])   # слипшийся лишний «-» сразу после &mdash; (опечатка источника)
        parts[i] = re.sub(r'\u2014', '&mdash;', parts[i])   # юникодное тире → сущность (для единообразия)
        parts[i] = re.sub(r'\u2013(?![0-9])', '&ndash;', parts[i])
    return ''.join(parts)


def block_out_of_p(body):
    """<p>…<blockquote>…</blockquote>…</p> → <p>…</p><blockquote>…</blockquote><p>…</p> (блок внутри абзаца невалиден)."""
    pat = re.compile(r'<p\b([^>]*)>((?:(?!</p>|<p\b).)*?)<blockquote>(.*?)</blockquote>((?:(?!</p>).)*)</p>', re.S)
    def rep(m):
        head, quote, tail = m.group(2).strip(), m.group(3), m.group(4).strip()
        out = ''
        if head: out += '<p%s>%s</p>\n' % (m.group(1), head)
        out += '<blockquote>%s</blockquote>' % quote
        if tail: out += '\n<p>%s</p>' % tail
        return out
    prev = None
    while prev != body:
        prev = body
        body = pat.sub(rep, body, count=1)
    return body


def anchors(body):
    """Внутренние ссылки-якоря старого словаря (#avtoparo1993) → якорь новой страницы: id песни без года (#avtoparo)."""
    return re.sub(r"(href=['\"])#([a-z]+\d?[a-z]*?)(?:19|20)\d\d(['\"])", r'\1#\2\3', body)


def links(body):
    """Ссылки на зеркала старого сайта → внутренние (страница kom.html лежит в fans/); пустой target=''; пустые абзацы."""
    b = re.sub(r"(href=['\"])https?://(?:lambda\.mkshch\.com|(?:www\.)?blackalpinist\.com/scherbakov)/fans/", r'\1', body)
    b = re.sub(r"(href=['\"])https?://(?:lambda\.mkshch\.com|(?:www\.)?blackalpinist\.com/scherbakov)/htmtexts/", r'\1../texts/', b)
    b = re.sub(r"(href=['\"])https?://(?:lambda\.mkshch\.com|(?:www\.)?blackalpinist\.com/scherbakov)/(?!fans/)", r'\1../', b)
    b = re.sub(r"\s+target=(['\"])\1", '', b)
    b = re.sub(r"(href=['\"]mailto:)\s+", r'\1', b)
    b = re.sub(r'<p>\s*</p>', '', b)
    return b.strip('\n') if b.strip() else b


LAT2CYR = dict(zip('AaBCcEeHKMOoPpTXxy', 'АаВСсЕеНКМОоРрТХху'))


def homoglyphs(body, report):
    """Латинские двойники букв внутри русских слов («Hо» с латинской H) → кириллица."""
    parts = re.split(r'(<[^>]+>)', body)
    n = 0
    def tok(m):
        nonlocal n
        w = m.group(0)
        if re.search('[а-яёА-ЯЁ]', w) and re.search('[A-Za-z]', w) and all(c in LAT2CYR or not re.match('[A-Za-z]', c) for c in w):
            n += 1
            return ''.join(LAT2CYR.get(c, c) for c in w)
        return w
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'[A-Za-zА-Яа-яЁё]+', tok, parts[i])
    if n:
        report.append('латинские двойники исправлены: %d' % n)
    return ''.join(parts)


VARIANT = re.compile(
    r'((?:в\s+(?:первом|раннем|более\s+раннем|первоначальном|одном\s+из)\s+вариант\w*|вариант(?:\s+с\s+диска[^:&<]{0,40})?|изначально)\s*:\s*)'
    r'(?!<i>)(&laquo;.*?&raquo;)', re.S)


def variants(body):
    """Варианты строк песни («в первом варианте: «…»», «вариант: «…»») — слова автора → курсив."""
    return VARIANT.sub(lambda m: m.group(1) + '<i>' + m.group(2) + '</i>', body)


def reader_quotes(body):
    """<blockquote><span class='reader-quote'>…</span></blockquote> → <blockquote>…</blockquote>; <ul><p>…</p></ul> (отступ) → <blockquote>."""
    b = re.sub(r"<blockquote>\s*<span class=['\"]reader-quote['\"]>(.*?)</span>\s*</blockquote>", r'<blockquote>\1</blockquote>', body, flags=re.S)
    b = re.sub(r'<ul>\s*<p>(.*?)</p>\s*</ul>', r'<blockquote>\1</blockquote>', b, flags=re.S)
    return b


def ranges(body):
    """Числовые диапазоны (годы, страницы) 1810-1857, 690-630 → короткое тире (&ndash;). Даты через дефис (2004-02-03), телефоны, «3-ударным» не трогаем."""
    parts = re.split(r'(<[^>]+>)', body)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'(?<![\w\-])(\d{1,4})[ \t]?-[ \t]?(\d{1,4})(?![\w\-])', r'\1&ndash;\2', parts[i])
        # годы через длинное тире с пробелами: «1837 — 1902» → «1837–1902»
        parts[i] = re.sub(r'(?<![\w\-])(1[0-9]{3}|20[0-9]{2})(?:\s|&nbsp;)*(?:&mdash;|&ndash;)(?:\s|&nbsp;)*(1[0-9]{3}|20[0-9]{2})(?![\w\-])', r'\1&ndash;\2', parts[i])
    return ''.join(parts)


def spacing(body, report):
    """Пробелы вокруг скобок и подписей:
    1) знак препинания, слипшийся с последующей подписью/датой/ссылкой/скобкой: «,<span class='entry-date'>» → «, <span…»; «Крым.(Алексей» → «Крым. (Алексей»;
    2) пробел после «(» перед подписью, датой или ссылкой (в т.ч. внутри ссылки и внутри даты), пробел перед «)»;
    3) в отчёт (без правки): слипшиеся «слово.Слово» — возможно, пропущен пробел."""
    n = 0
    def sub(pat, rep, s, flags=0):
        nonlocal n
        s2, c = re.subn(pat, rep, s, flags=flags)
        n += c
        return s2
    b = body
    # 2а) пробелы внутри <a …> и <span class='entry-date'> с обеих сторон
    b = sub(r"(<a\b[^>]*>)\s+", r'\1', b)
    b = sub(r"(<span class=['\"]entry-date['\"]>)\s+", r'\1', b)
    def trail(m):
        # хвостовой пробел внутри ссылки/даты убираем; снаружи оставляем один, только если дальше идёт слово, «(» или открывающая кавычка
        rest = m.group(3)
        need = bool(re.match(r"[\w(<«„]|&laquo;|&bdquo;", rest)) and not rest[:1].isspace()
        return m.group(1) + m.group(2) + (' ' if need else '')
    b = sub(r"(\S)[ \t\n]+(</a>|</span>)(.{0,8})", lambda m: trail(m) + m.group(3), b, flags=re.S)
    b = sub(r"(</a>|</span>|[\w.])[ \t]+,(?=\s|<|$)", r'\1,', b)
    # 2б) пробелы после «(» и перед «)»
    b = sub(r"\([ \t\n]+(?=<a\b|<span|[\w&«„‘])", '(', b)
    b = sub(r"(?<=[\w>.\d])[ \t]+\)", ')', b)
    # 1) слипшиеся подписи и даты
    b = sub(r"(&raquo;|&ldquo;|&rsquo;)(?=\(<a\b|\(<span)", r'\1 ', b)
    b = sub(r"(?<![&\w])([,:])(?=<span class=['\"]entry-date|<a\b)", r'\1 ', b)
    b = sub(r"([а-яёА-ЯЁa-z]{2,})([,:])(?=<span class=['\"]entry-date|<a\b)", r'\1\2 ', b)
    b = sub(r"([а-яёА-ЯЁa-zA-Z]{3,}\.)(?=\(|<span class=['\"]entry-date)", r'\1 ', b)
    b = sub(r"(</a>|</span>)(?=\()", r'\1 ', b) if False else b
    if n:
        report.append('пробелы вокруг скобок/подписей исправлены: %d' % n)
    # 3) только отчёт
    text = re.sub(r'<[^>]+>|&\w+;', ' ', b)
    glued = sorted(set(re.findall(r'\b[а-яё]{3,}[.,;][А-ЯЁ][а-яё]{2,}', text)))
    if glued:
        report.append('слипшееся «слово.Слово» (проверить): ' + ', '.join(glued[:6]))
    return b


def normalize_body(body, report=None, source=False):
    if report is None:
        report = []
    b = body
    if source:  # только для текста из исходника (не идемпотентно!): старые <em> — цитаты из песни → <i>; <b> → <em>
        b = re.sub(r'<(/?)em>', r'<\1i>', b)
        b = re.sub(r'<(/?)(?:b|strong)>', r'<\1em>', b)
    b = homoglyphs(b, report)
    b = spacing(b, report)
    b = reader_quotes(b)
    b = links(b)
    b = anchors(b)
    b = dashes(b)
    b = ranges(b)
    b = block_out_of_p(b)
    b = normalize_quotes(b, report)
    b = verse_slashes(b, report)
    b = add_caps_head(b, report)
    b = add_dfn(b, report)
    b = variants(b)
    for cls in ('editor-aside', 'reader-quote'):
        if cls in b:
            report.append('СТИЛЬ %s: %d — решить вручную (реплику редактора выносим в отдельный <p>, оформление снимаем)' % (cls, b.count(cls)))
    text = re.sub(r'<[^>]+>|&\w+;', ' ', b)
    caps = sorted(set(w for w in re.findall(r'\b[А-ЯЁ]{5,}\b', text)))
    if caps:
        report.append('слова капсом: ' + ', '.join(caps))
    return b
