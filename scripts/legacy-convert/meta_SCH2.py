# «Щ-2» (социологический проект, 2000): опубликован как на старом сайте (решение владельца 2026-09-24)
SOC = ('sociology.html', 'Социология')
HUB = ('SCH2/index.html', 'Щ-2')
META = {
 'index': dict(title='«Щ-2»', back=SOC, lastmod='2000-05-20', replace=[('<h2>«Щ-2»</h2>\n\n', '')]),
 '103-e': dict(title='Вопрос 1.3', back=HUB),
 '101-e': dict(title='Вопрос 1.1', back=HUB, params={'monoPre': True}),   # схемы размера выровнены пробелами
 '401-e': dict(title='Вопрос 4.1', back=HUB),
 '401-2': dict(title='Полемика по вопросу 4.1', subtitle='Борис Жуков и Владимир Медведев', back=HUB,
               # первая строка повторяла заголовок и подзаголовок
               replace=[(r're:\A<p><b><i>Полемика по .*?</p>\n\n<hr>\n\n', '')]),
 'gb/index': dict(title='Обсуждение', back=HUB, replace=[('href="../profiles"', 'href="../profiles.html"'), ('<h2>Обсуждение</h2>\n\n', '')]),
 'profiles': dict(title='Личные профили респондентов', back=HUB,
                  replace=[('href="../smirnov/"', 'href="../fans/smirnov/index.html"'), ('href="../smirnov"', 'href="../fans/smirnov/index.html"'), ('href="../index.html"', 'href="index.html"'), ('<h2>Личные профили респондентов</h2>\n\n', '')]),
}

import os
import re
QUESTION = re.compile(r'\d{3}-[e2]$')   # страницы вопросов экспертного обсуждения: 101-e … 705-e, 401-2

META['203-e'] = dict(back=HUB, params={'monoPre': True})   # письмо в виде электронной почты
# 2.5: в исходнике цитаты из песен разбиты <ul>/<br> вперемешку с текстом — собрать вручную (после POST: правки
# по уже оформленному тексту)
POST_REPLACE = {
  # 5.4: «Владимир Смирнов:<br>) А еще…» — смайлик, не знак после имени (владелец 2026-10-17)
  '504-e': [('<b>Владимир Смирнов:</b> ) ', '<b>Владимир Смирнов</b> :) ')],
  # 5.5: периоды у Е. Коротеевой — списком
  '505-e': [('<p class="cont">Ранние песни&nbsp;&mdash; 1979&ndash;1982<br>1982&ndash;1987<br>Речитативы 1987&ndash;1992<br>'
             'Период до 8-ой кассеты&nbsp;&mdash; 1992&ndash;1996<br>То что сейчас</p>',
             '<ul class="dashes">\n<li>ранние песни&nbsp;&mdash; 1979&ndash;1982;</li>\n<li>1982&ndash;1987;</li>\n'
             '<li>речитативы&nbsp;&mdash; 1987&ndash;1992;</li>\n<li>период до 8-й кассеты&nbsp;&mdash; 1992&ndash;1996;</li>\n'
             '<li>то, что сейчас.</li>\n</ul>')],
  '205-e': [
    ('<p class="cont">Да и вообще&nbsp;&mdash;</p>\n\n<p>дам поделом. Нипочем не переплачу.</p>\n\n'
     '<p class="cont">Всем от того витража по осколку.</p>\n\n<p class="cont">Скупо, нелепо. Но я так хочу.</p>\n\n'
     '<p class="cont">Я&nbsp;&mdash; черный волк...</p>\n\n<p>этот переход в Волке от Ты к Я</p>\n\n'
     '<p class="cont">можно продолжать перечислять...</p>',
     '<p class="cont">Да и вообще&nbsp;&mdash;</p>\n\n<blockquote><p>дам поделом. Нипочем не переплачу.<br>'
     'Всем от того витража по осколку.<br>Скупо, нелепо. Но я так хочу.</p>\n<p>Я&nbsp;&mdash; черный волк...</p>'
     '</blockquote>\n\n<p class="cont">этот переход в Волке от Ты к Я можно продолжать перечислять...</p>')]}


def green_src(html):
    # Зелёный текст оригинала — связки и примечания составителей (не реплики экспертов). Блок <ul><font
    # color=#008800>…</font></ul> помечается словами-метками до конвертации (иначе конвертер разваливает его), после —
    # абзацы между метками получают класс editorial (POST); зелёное внутри реплики («(Прим. ред.: …)») — <i>
    # незакрытый якорь (<a name=zhukov> в 1.3) html5lib растягивает на всю страницу — закрыть сразу
    html = re.sub(r'(<a name=[\w"-]+>)(?!\s*[^<\s])', r'\1</a>', html, flags=re.I)
    # блоком бывает и <blockquote><font …> (комментарии Б. Жукова, примечания редакции в 5.3)
    # зелёный блок посреди фразы эксперта (дальше — со строчной: «…составляющая важнее /прим. ред.: …/ в
    # инструментовке…» в 1.4) — вставка в реплику: <i> в строку, не отдельный абзац
    html = re.sub(r'<(ul|blockquote)>\s*<font color=#008800>((?:(?!<(?:ul|blockquote)>).)*?)</font>\s*</\1>(?=\s*[а-яё])',
                  r' <i>\2</i> ', html,
                  flags=re.I | re.S)
    # блок — до своего </ul> (</font> бывает и раньше: «…ответ </font><i>(??? — Ред.)</i></ul>» в 2.2)
    html = re.sub(r'<(ul|blockquote)>\s*<font color=#008800>(.*?)</\1>',
                  lambda m: '<p>EDBEGINX ' + re.sub(r'</font>', '', m.group(2), count=1, flags=re.I) + ' EDENDX<p>',
                  html, flags=re.I | re.S)
    html = re.sub(r'<font color=#008800>(.*?)</font>', r'<i>\1</i>', html, flags=re.I | re.S)
    return html


# Сквозная навигация по вопросам (владелец 2026-10-17): порядок чтения — 1.1 … 7.5, «Полемика» сразу после 4.1;
# 8-го блока нет («обсуждения не было»). Подсказка у ссылки — тема блока (из оглавления «Щ-2»).
SERIES = ['101-e', '102-e', '103-e', '104-e', '201-e', '202-e', '203-e', '204-e', '205-e', '301-e', '302-e', '303-e',
          '304-e', '401-e', '401-2', '402-e', '403-e', '501-e', '502-e', '503-e', '504-e', '505-e', '601-e', '701-e',
          '702-e', '703-e', '704-e', '705-e']
BLOCKS = {'1': 'Блок 1. Поэзия и/или музыка?', '2': 'Блок 2. «Мир Щербакова»', '3': 'Блок 3. Интертекстуальность',
          '4': 'Блок 4. Гуманизм или антигуманизм?', '5': 'Блок 5. Поэтика Щербакова', '6': 'Блок 6. Окуджава, Высоцкий, '
          'Щербаков', '7': 'Блок 7. Разговор с автором'}


def q_title(n):
    return 'Полемика по вопросу 4.1' if n == '401-2' else f'Вопрос {n[0]}.{int(n[1:3])}'


def series_params(n):
    i = SERIES.index(n)
    p = {}
    for key, j in (('prev', i - 1), ('next', i + 1)):
        if 0 <= j < len(SERIES):
            t = SERIES[j]
            p[key + 'Url'], p[key + 'Title'], p[key + 'Hint'] = f'SCH2/{t}.html', q_title(t), BLOCKS[t[0]]
    return p


# Тема вопроса (заголовок вкладки «Вопрос 1.1: … — проект «Щ-2»», строка оглавления) и описание для поисковиков
# (2026-10-17, черновик — на согласование владельцу); у 1.3 — свои, правленые вручную в content/
SEO = {
 '101-e': ('стих и музыка, авторское исполнение', 'Как соотносятся стих и музыка в песнях Михаила Щербакова и что привносит авторское исполнение'),
 '102-e': ('близкие Щербакову поэты и писатели', 'Кто из поэтов и писателей русской и мировой культуры ближе всего Михаилу Щербакову и чем'),
 '103-e': ('музыка Михаила Щербакова', ''),
 '104-e': ('Щербаков и жанр авторской песни', 'Вписывается ли творчество Михаила Щербакова в жанр авторской песни и как ещё его можно определить'),
 '201-e': ('«песня про меня» и «моя песня»', 'Песни Михаила Щербакова, к которым у слушателей особое, личное отношение: «песня про меня» и «моя песня»'),
 '202-e': ('мир Щербакова и мир слушателя', 'Как слушатель ощущает себя в мире, созданном песнями Михаила Щербакова, и что в нём вызывает сопротивление'),
 '203-e': ('какие мы, когда слушаем Щербакова', 'Какие чувства и состояния вызывают песни Михаила Щербакова: «эмоциональное заражение» и узнавание себя'),
 '204-e': ('Щербаков как явление времени', 'Можно ли считать Михаила Щербакова феноменом, характерным для нашего времени и состояния культуры'),
 '205-e': ('лирический герой и «дух времени»', 'Что в мироощущении лирического героя Михаила Щербакова созвучно «духу времени» и самому слушателю'),
 '301-e': ('цитаты из Щербакова в разговоре', 'Когда и зачем слушатели цитируют песни Михаила Щербакова и какую роль играют такие цитаты'),
 '302-e': ('скрытые цитаты в песнях', 'Скрытые цитаты в песнях Михаила Щербакова: зачем они автору и что дают слушателю'),
 '303-e': ('сквозные темы и образы', 'Сквозные темы, проблемы и образы в творчестве Михаила Щербакова'),
 '304-e': ('Щербаков и русская классика', 'Темы и образы Михаила Щербакова, идущие от русской классической литературы и национального характера'),
 '401-e': ('камерность, этика, постмодернизм', '«Поэт камерный», «этически амбивалентен», «постмодернист»: эксперты об утверждениях о Михаиле Щербакове'),
 '401-2': ('постмодернизм и этика, Б. Жуков и В. Медведев', 'Полемика Бориса Жукова и Владимира Медведева: постмодернист ли Михаил Щербаков и амбивалентна ли его этика'),
 '402-e': ('почему Щербаков не близок', 'Почему творчество Михаила Щербакова многим не близко: суть позиции тех, кто его не принимает'),
 '403-e': ('холодность и гуманизм', 'Холодна ли поэзия Михаила Щербакова и можно ли говорить о её гуманистическом пафосе'),
 '501-e': ('мозаика или единое целое', 'Творчество Михаила Щербакова — пёстрая мозаика или единое целое, и что его объединяет'),
 '502-e': ('расшифровка аллюзий', 'Нуждаются ли аллюзии Михаила Щербакова в расшифровке и пытаются ли слушатели их раскодировать'),
 '503-e': ('как менялась поэтика', 'Как со временем менялась поэтика Михаила Щербакова: усложнение ритмики, языка и техники'),
 '504-e': ('словарь языка Щербакова', 'Тема «Словарь языка в поэтике Михаила Щербакова»: сквозные слова, образы и что о них можно написать'),
 '505-e': ('творческий путь: этапы и прогноз', 'Этапы творческого пути Михаила Щербакова и прогнозы его дальнейшего развития'),
 '601-e': ('Окуджава, Высоцкий, Щербаков', 'Лирические миры Окуджавы, Высоцкого и Михаила Щербакова: чем они отличаются друг от друга'),
 '701-e': ('концерт и запись', 'Чем впечатление от песен Михаила Щербакова на концерте отличается от записи, квартирник — от большого зала'),
 '702-e': ('концертные или студийные записи', 'Что слушателям предпочтительнее у Михаила Щербакова — записи с концертов или студийные, и почему'),
 '703-e': ('о чём спрашивать Щербакова', 'Записки на концертах Михаила Щербакова: о чём его хотелось бы спросить и о чём спрашивать не стоит'),
 '704-e': ('если бы Щербаков читал лекции', 'Каким лектором был бы Михаил Щербаков и лекции на какие темы хотелось бы от него услышать'),
 '705-e': ('книга Щербакова', 'Какой была бы книга Михаила Щербакова, если бы он её написал: жанр и темы'),
}
SEO_TAIL = ' — эксперты проекта «Щ-2» (1999–2000).'


class _Meta(dict):
    # у каждой страницы вопроса — green_src, заголовок «Вопрос 1.1» и ссылки «предыдущая/следующая» (страниц без
    # своей записи в META тоже)
    def get(self, k, d=None):
        v = dict(super().get(k, {}))
        if QUESTION.match(k):
            v.setdefault('src_fn', green_src)
            v.setdefault('title', q_title(k))
            v.setdefault('back', HUB)
            if k in SERIES:
                v['params'] = {**v.get('params', {}), **series_params(k)}
            if k in SEO and k != '103-e':
                v['params'] = {**v.get('params', {}),
                               'seoTitle': f'{q_title(k)}: {SEO[k][0]} — проект «Щ-2»'}
                v['description'] = SEO[k][1] + SEO_TAIL
            return v
        return super().get(k, d)


META = _Meta(META)


# вопрос: <p><b><i>Вопрос 1.1. …</i></b></p> — первый абзац страницы; в конце некоторых страниц — он же в новой
# («уточнённой») формулировке и «Дополнительный вопрос:»
QPARA = re.compile(r'<p(?: class="cont")?><b><i>((?:Вопрос \d\.\d|Дополнительный вопрос).*?)</i>\s*</b>\s*</p>', re.S)
QLABEL = re.compile(r'(Вопрос \d\.\d|Дополнительный вопрос)\.?\s*:?\s*(\(\s*[^)]*?\))?\s*:?\s*\.?\s*')


def question(m):
    # Вопрос — полужирным без курсива. Номер «Вопрос 1.1» не повторяем — он в заголовке страницы; пометка о формулировке
    # («(первоначальная формулировка)», «(новая формулировка)», «Дополнительный вопрос») — отдельной строкой над
    # вопросом, с заглавной, курсивом, с двоеточием («…остаётся в своём первоначальном варианте» — с точкой). Каждый
    # подвопрос (после «?», после двоеточия перед новой фразой) — с новой строки, пункты а) б) в) — списком
    # (правила владельца 2026-10-17)
    text = m.group(1).strip()
    lm = QLABEL.match(text)
    note = (lm.group(2) or '').strip('() ').strip()
    if lm.group(1) == 'Дополнительный вопрос':
        note = 'Дополнительный вопрос'
    if note:
        note = note[0].upper() + note[1:] + ('.' if 'остаётся' in note or 'остается' in note else ':')
    rest = text[lm.end():]
    rest = re.sub(r'\?\s+(?=\S)', '?<br>', rest)
    rest = re.sub(r':\s+(?=[А-ЯЁ])', ':<br>', rest)    # «…все-таки: О чем бы…» (не «мысль: когда…»)
    rest = re.sub(r'(\s*<br>\s*)+', '<br>', rest)
    # пункты а) б) в) — нумерованным списком ol.subq (маркеры «а)» — стилем), с отступом слева
    items = re.split(r'\s*(?:<br>)?\s*[абвгд]\)\s+', rest)
    sub = ''
    if len(items) > 1:
        rest = items[0]
        sub = '\n\n<ol class="subq">\n' + ''.join(f'<li><b>{x.strip()}</b></li>\n' for x in items[1:]) + '</ol>'
    head = f'<i>{note}</i><br>' if note else ''
    return f'<p class="question">{head}<b>{rest}</b></p>{sub}'


# «Design © Vladimir Smirnov» — оформление старого сайта; у страниц теперь общее оформление сайта — строку убираем
# (владелец 2026-10-17); авторская подпись Блехеров остаётся
DESIGN = re.compile(r'(<br>)?\s*Design( and CGI)? © <a href="mailto:smirnov@[\w.-]+">Vladimir Smirnov</a>')


def POST(body, n):
    body = DESIGN.sub('', body).replace('\n\n<p></p>', '')
    if not QUESTION.match(n):
        return body
    # номер вопроса вёл на CGI-форму ответа (sch2q.pl) — её давно нет: ссылку снять, текст оставить
    body = re.sub(r'<a href="http:/cgi-bin/sch2q\.pl[^"]*">(.*?)\s*</a>\s*', r'\1 ', body)
    body = body.replace('вопросу 4.1. :', 'вопросу 4.1:')
    body = body.replace('href="../FOM"', 'href="../FOM/index.html"')
    # ссылки на текст песни в .txt старого сайта — на страницу песни
    body = body.replace('href="../texts/1995/onceinou.txt"', 'href="../texts/1995/once.html"')
    # перенос строки внутри слова в исходнике; «┘» — многоточие, потерянное при перекодировке
    body = body.replace('ра скодировать', 'раскодировать').replace('┘', '…')
    body = editorial(body)
    # пустая подпись эксперта (в исходнике <u></u>)
    body = body.replace('<p><u></u></p>\n\n', '')
    # имена экспертов в оригинале подчёркнуты — на сайте подчёркнутое не отличить от посещённой ссылки:
    # имена жирным, как в стенограмме (правило владельца 2026-10-17)
    body = re.sub(r'<u>\s*(.*?)\s*</u>', r'<b>\1</b>', body, flags=re.S)
    # <ul> оригинала (конвертер делает из него <blockquote>) — не цитаты, а комментарии Б. Жукова и примечания
    # редакции: обычными абзацами; <blockquote> — только для цитат стихов (ниже, split_para)
    body = re.sub(r'<blockquote>\s*(<p>.*?</p>)\s*</blockquote>', r'\1', body, flags=re.S)
    body = re.sub(r'<blockquote>(.*?)</blockquote>', r'<p>\1</p>', body, flags=re.S)
    body = re.sub(r'<p( class="verse")?>(.*?)</p>', split_para, body, flags=re.S)
    body = QPARA.sub(question, body)    # после split_para: уточнённая формулировка бывает строкой внутри абзаца
    body = merge_solo(body)
    # абзац, который начинается с полужирной подписи («Комментарий Бориса Жукова: …»), — тоже начало реплики
    body = re.sub(r'<p>((?:<a id="[^"]*"></a>)?<b>)', r'<p class="speaker">\1', body)
    body = subquestions(body)
    # «полностью ответ Б.Жукова — Здесь.» — со строчной
    body = body.replace('&nbsp;&mdash; Здесь.</a>', '&nbsp;&mdash; здесь.</a>')
    # примечание редакции в слешах «/прим. ред.: …/» — в круглых скобках, как остальные (владелец 2026-10-17)
    body = re.sub(r'/\s*([Пп]рим\.\s*ред\.:[^/<]*?)\s*/', r'(\1)', body)
    # 3.3: «/Эта тема прозвучит и в конце обсуждения./» в ответе Анеты — пометка составителей; 7.4: реплика
    # В. Шнейдера в слешах — его собственная, прямым шрифтом в скобках (владелец 2026-10-17)
    body = body.replace('/Эта тема прозвучит и в конце обсуждения./',
                        '<i>(прим. ред.: Эта тема прозвучит и в конце обсуждения.)</i>')
    body = re.sub(r'/(Обсуждение данного вопроса напоминает мне[^/<]*)/', r'(\1)', body)
    # пробел после открывающей кавычки «« О Боже»
    body = re.sub(r'«(?:\s|&nbsp;)+(?=\S)', '«', body)
    # пробелы внутри квадратных скобок: «[ Все эти размышления … ]» (6.1)
    body = re.sub(r'\[(?:\s|&nbsp;)+', '[', body)
    body = re.sub(r'(?:\s|&nbsp;)+\]', ']', body)
    # пробел после открывающей скобки: «( фр. genre», «( ну, скажем»
    body = re.sub(r'\((?:\s|&nbsp;)+(?=[^\s)])', '(', body)
    body = unstick(body)
    # «…о частных своих проблемах..»» — обрезанная цитата: многоточие
    body = re.sub(r'(?<=[А-Яа-яЁё])\.\.(?=»)', '...', body)
    # диапазоны «1989-1991», «6-7-й» — короткое тире; «ВЕЩЬ-ЧЕЛОВЕК-СЛОВО» — тоже
    # (только в тексте, не в адресах ссылок вроде 401-2.html)
    # «1979 — 1982» (в исходнике дефис с пробелами) — тоже диапазон годов
    body = re.sub(r'(?<=\d{4})(?:&nbsp;|\s)*&mdash;\s*(?=\d{4})', '&ndash;', body)
    body = re.sub(r'(?<=>)([^<]+)(?=<)', lambda m: re.sub(r'(?<=[А-ЯЁ]{2})-(?=[А-ЯЁ]{2})', '&ndash;',
                  re.sub(r'(?<=\d)-(?=\d)', '&ndash;', m.group(1))), body)
    # «(C)» — знак ©; в подписи цитаты «(© Ю. Ким)» знак не нужен (владелец 2026-10-17)
    body = body.replace('(C)', '&nbsp;©')
    body = re.sub(r'\(©\s*', '(', body)
    # двоеточие после полужирной подписи — внутрь неё: «<b>Комментарий Бориса Жукова</b>:» → «…Жукова:</b>»
    body = re.sub(r'</b>\s*:', ':</b>', body)
    # пробел перед запятой («Щербакову , я»)
    body = re.sub(r'(?<=[А-Яа-яЁё»)])\s+,', ',', body)
    # «1.. Не совсем», «Самоповторы..» — повтор точки (не многоточие) — одна точка (владелец 2026-10-17)
    body = re.sub(r'(?<=[\dА-Яа-яЁё])\.\.(?!\.)', '.', body)
    # лишняя точка в начале абзаца («. Третья группа» в 4.2 — так в исходнике)
    body = re.sub(r'(<p[^>]*>)\s*\.\s+', r'\1', body)
    # «Комментарий Бориса Жукова:» курсивом целиком (<i> вокруг всего блока) — имя тоже в строку
    body = re.sub(r'<p><i><b>([^<]*?)</b>\s*<br>\s*', r'<p class="speaker"><i><b>\1</b> ', body)
    body = readers_link(body, n)
    for a, b in POST_REPLACE.get(n, []):
        if a not in body:
            print('  ! POST_REPLACE not found:', a[:60])
        body = body.replace(a, b)
    body = polish(body)
    body = continuations(body)
    body = dash_lists(body)
    body = quote_sources(body)
    return body


VERSE_LINE = 60   # строка цитаты стихов короче этого (в видимых знаках)


def visible(s):
    return re.sub(r'<[^>]+>', '', s).replace('&nbsp;', ' ').replace('&mdash;', '—').strip()


def top_level_br(s):
    # <br> вне строчных тегов: <b>…<br>…</b> (подзаголовок «Дополнительный ответ…:<br>Об этике…») не режем
    parts, depth, last = [], 0, 0
    for m in re.finditer(r'<(/?)(\w+)[^>]*>', s):
        tag = m.group(2).lower()
        if tag == 'br':
            if depth == 0:
                parts.append(s[last:m.start()])
                last = m.end()
        elif tag in ('b', 'i', 'u', 'a', 'span', 'em', 'strong', 'font'):
            depth += -1 if m.group(1) else 1
    parts.append(s[last:])
    return parts


def is_verse_run(run):
    # строки стихов: не меньше трёх коротких подряд, и хотя бы половина кончается не точкой/вопросом/кавычкой
    # (запятая, буква, тире: «скажет / он, — вокруг тебя не ляжет / мгла…»)
    if len(run) < 3:
        return False
    open_end = sum(1 for x in run if not re.search(r'[.!?»:;)]$', visible(x)))
    return open_end * 2 >= len(run)


NAME = re.compile(r'((?:<a id="[^"]*"></a>)?)<b>(?!<i>)(.*?)</b>(.*)', re.S)


def name_inline(ln):
    # «<b>Имя</b>» → «<b>Имя.</b>»: точка, если в конце нет знака препинания (имя и знак — полужирным);
    # «<b>Имя</b> (пояснение)» → «… (пояснение).»; перевод строки внутри подписи — пробелом
    m = NAME.fullmatch(ln)
    anchor, name, rest = m.group(1), re.sub(r'\s*<br>\s*', ' ', m.group(2)).strip(), m.group(3).strip()
    if rest:
        return f'{anchor}<b>{name}</b> {rest}' + ('' if re.search(r'[.:!?]$', visible(rest)) else '.')
    return f'{anchor}<b>{name}' + ('' if re.search(r'[.:!?]$', visible(name)) else '.') + '</b>'


def is_name(ln):
    m = NAME.fullmatch(ln)
    return bool(m) and len(visible(m.group(3))) < VERSE_LINE and not re.search(r'</?b>', m.group(3))


def quoted_run(lines, i):
    # цитата в кавычках на несколько коротких строк: «Следующий гость уже стучится в дом: / встречу на сегодня…»
    # (и подпись в скобках следом — «(В. Высоцкий)»); возвращает конец цитаты или 0
    if not lines[i] or not visible(lines[i]).startswith('«') or len(visible(lines[i])) >= VERSE_LINE:
        return 0
    j = i
    while j < len(lines) and lines[j] and len(visible(lines[j])) < VERSE_LINE:
        if j > i and re.search(r'»[.,!?…]*$', visible(lines[j])):
            j += 1
            if j < len(lines) and lines[j] and re.fullmatch(r'\(.{1,40}\)', visible(lines[j])):
                # подпись — внутри цитаты отдельным абзацем, прямым шрифтом, без скобок (quote_sources)
                lines[j] = 'QSRC' + visible(lines[j]).strip('()') 
                j += 1
            return j
        if j == i and re.search(r'»[.,!?…]*$', visible(lines[j])):
            return 0
        j += 1
    return 0


def split_para(m):
    # Реплика (в оригинале — блок между <p>, внутри — переводы строк <br>): имя эксперта полужирным с точкой — в начале
    # первого абзаца реплики («Елена Коротеева. Бред :)»), переводы строк внутри реплики — абзацы p.cont (красная строка,
    # без отступа сверху); вертикальный отступ — только между репликами. Имя посреди блока (после <br>) начинает новую
    # реплику. Цитата стихов (is_verse_run) — p.verse с переводами строк (правила владельца 2026-10-17).
    # Подпись «© …» не трогаем.
    cls0, inner = m.group(1), m.group(2)
    if inner.lstrip().startswith('©'):
        return m.group(0)
    lines = [ln.strip() for ln in top_level_br(inner)]
    # строка из одной закрывающей кавычки — к предыдущей
    joined = []
    for ln in lines:
        if joined and re.fullmatch(r'[»"”.…]+', visible(ln) or 'x'):
            joined[-1] += ln
        else:
            joined.append(ln)
    # пустая строка (<br><br>) — граница стихов: остаётся в списке как '' и прерывает их
    lines = [ln if visible(ln) else '' for ln in joined]
    while lines and not lines[0]:
        lines.pop(0)
    if len(lines) == 1 and not is_name(lines[0]):
        return m.group(0)
    out, i = [], 0          # out: (класс, html); класс: speaker — начало реплики, cont — продолжение, '' — прочее
    while i < len(lines):
        ln = lines[i]
        if not ln:
            i += 1
            continue
        if is_name(ln):
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if nxt.startswith(':') and ln.endswith('</b>'):
                # «<b>Комментарий Наталии Семёновой</b><br>: свое мнение…» — двоеточие к подписи
                ln, nxt = ln[:-4] + ':</b>', nxt[1:].lstrip()
                lines[i + 1] = nxt
            head = name_inline(ln)
            j = i + 1
            while j < len(lines) and lines[j] and len(visible(lines[j])) < VERSE_LINE:
                j += 1
            # стихи под именем — только цитата в «» (список периодов у Е. Коротеевой в 5.5 — нет: имя в строку)
            run = lines[i + 1:j]
            verse = is_verse_run(run) and '«' in ''.join(visible(x) for x in run)
            if nxt and not is_name(nxt) and not verse:
                out.append(('speaker', f'{head} {nxt}'))
                i += 2
            else:
                # одно имя (дальше стихи, пустая строка или конец блока — тогда реплика в следующих блоках)
                out.append(('speaker solo' if not nxt and i + 1 >= len(lines) else 'speaker', head))
                i += 1
            continue
        j = i
        while j < len(lines) and lines[j] and len(visible(lines[j])) < VERSE_LINE and not is_name(lines[j]):
            j += 1
        first = not out
        k = quoted_run(lines, i)
        if k:
            j = k
        if k or is_verse_run(lines[i:j]):
            # стихи — только цитаты (с «»); короткие строки без кавычек (список периодов в 5.5) — один абзац с <br>
            quote = k or '«' in ''.join(visible(x) for x in lines[i:j])
            out.append(('verse' if quote else ('' if first else 'cont'), '<br>'.join(lines[i:j])))
            i = j
            continue
        out.append(('' if first else 'cont', re.sub(r'^(&nbsp;)+', '', ln)))
        i += 1
    # цитаты стихов — <blockquote> (курсив, отступ слева, отбивка сверху и снизу), как в «Словаре заморских слов»
    return '\n\n'.join(f'<blockquote><p>{h}</p></blockquote>' if c == 'verse' else
                       f'<p class="{c}">{h}</p>' if c else f'<p>{h}</p>' for c, h in out)


def merge_solo(body):
    # блок из одного имени («Первый ответ Бориса Жукова:» в «Полемике»): имя — в начало следующего абзаца, а абзацы
    # дальше, до следующего имени, вопроса, линии или заголовка, — продолжение той же реплики (p.cont)
    parts = body.split('\n\n')
    out, i = [], 0
    while i < len(parts):
        p = parts[i]
        m = re.fullmatch(r'<p class="speaker solo">(.*)</p>', p, re.S)
        if m and i + 1 < len(parts) and parts[i + 1].startswith('<p>'):
            out.append('<p class="speaker">' + m.group(1) + ' ' + parts[i + 1][3:])
            i += 2
            while i < len(parts) and (parts[i].startswith('<p>') or parts[i].startswith('<p class="cont">')
                                      or parts[i].startswith('<blockquote>')):
                q = parts[i]
                if q.startswith('<p>'):
                    q = '<p class="cont">' + q[3:]
                out.append(q)
                i += 1
            continue
        out.append(p.replace('<p class="speaker solo">', '<p class="speaker">'))
        i += 1
    return '\n\n'.join(out)


def stems(text):
    return {w[:6] for w in re.findall(r'[а-яё]{5,}', visible(text).lower())}


def subquestions(body):
    # Утверждения из пунктов вопроса (а) «Щербаков — поэт камерный» …), которые эксперты цитируют перед ответом, —
    # курсивом, с точкой после, если нет своего знака; ответ — в том же абзаце: «Карина Симочкина. «Щ. — камерный
    # поэт». В смысле…» (правило владельца 2026-10-17). Цитата узнаётся по общим словам с пунктами вопроса.
    q = re.search(r'<ol class="subq">(.*?)</ol>', body, re.S)
    items = re.findall(r'<li><b>(«[^»]*»)', q.group(1)) if q else []
    if not items:
        return body
    keys = [stems(x) for x in items]
    QUOTE = r'«[^»<]{3,60}»'

    def is_sub(quote):
        st = stems(quote)
        return any(st & k for k in keys)

    parts = body.split('\n\n')
    # цитата в конце абзаца, а ответ — в следующем (в исходнике не хватало перевода строки) — к следующему абзацу
    for i in range(len(parts) - 1):
        m = re.search(r'\s*(' + QUOTE + r')</p>$', parts[i])
        if m and is_sub(m.group(1)) and parts[i + 1].startswith('<p class="cont">') and not re.match(
                r'<p[^>]*>(<b>[^<]*</b>\s*)?$', parts[i][:m.start()] + ''):
            parts[i] = parts[i][:m.start()] + '</p>'
            parts[i + 1] = '<p class="cont">' + m.group(1) + ' ' + parts[i + 1][len('<p class="cont">'):]
    out = []
    for p in parts:
        m = re.match(r'(<p class="(?:speaker|cont)">(?:<b>[^<]*</b> )?)(' + QUOTE + r')(.*)</p>$', p, re.S)
        if not m or not is_sub(m.group(2)):
            out.append(p)
            continue
        head, quote, rest = m.groups()
        quote = f'<i>{quote}</i>'
        if not rest.strip() and out is not None:
            out.append(('MERGE', head + quote))
            continue
        if re.match(r'\s*[^\s.,:;!?…&(—-]', rest) and not rest.lstrip().startswith('&nbsp;&mdash;'):
            quote += '.'
        out.append(head + quote + rest + '</p>')
    # одна цитата в абзаце — ответ из следующего абзаца в тот же
    res = []
    for i, p in enumerate(out):
        if isinstance(p, tuple):
            res.append(('MERGE', p[1]))
            continue
        if res and isinstance(res[-1], tuple) and p.startswith('<p class="cont">'):
            res[-1] = res[-1][1] + '. ' + p[len('<p class="cont">'):]
            continue
        if res and isinstance(res[-1], tuple):
            res[-1] = res[-1][1] + '</p>'
        res.append(p)
    if res and isinstance(res[-1], tuple):
        res[-1] = res[-1][1] + '</p>'
    return '\n\n'.join(res)


def editorial(body):
    # абзацы между метками EDBEGINX … EDENDX (green_src) — p.editorial (курсив, владелец 2026-10-17)
    parts = body.split('\n\n')
    inside = False
    out = []
    for p in parts:
        start = 'EDBEGINX' in p
        end = 'EDENDX' in p
        p = re.sub(r'\s*EDBEGINX\s*', '', p)
        p = re.sub(r'\s*EDENDX\s*', '', p)
        if re.fullmatch(r'<p>\s*</p>', p):
            inside = (inside or start) and not end
            continue
        if (inside or start) and re.match(r'<p( class="verse")?>', p):
            # абзац с переводами строк конвертер помечает как verse — здесь это список составителей («три подхода:»)
            p = re.sub(r'^<p( class="verse")?>', '<p class="editorial">', p)
        inside = (inside or start) and not end
        out.append(p)
    return '\n\n'.join(out)


ABBR = re.compile(r'(?:^|(?<=[\s(«„"—;]))([А-ЯЁA-Z]|[а-яё]{1,2}|Арс|Дм|Прим|прим|напр|ред)\.$')


def unstick_text(t):
    # знак препинания, прилипший к следующей (русской) букве, — с пробелом: «же,что» → «же, что», «да...А» → «да... А»;
    # после инициала и сокращения — неразрывный: «М.Щербаков» → «М.&nbsp;Щербаков», «т.д.» → «т.&nbsp;д.».
    # Многоточие в начале цитаты или реплики («...Конечно», «(«...Я») не трогаем (правило владельца 2026-10-17)
    out, i = [], 0
    for m in re.finditer(r'([.,;:!?…])(?=[А-Яа-яЁё])', t):
        j = m.start()
        if m.group(1) == ';' and re.search(r'&[a-zA-Z]+$|&#\d+$', t[:j]):
            continue                                          # «&laquo;Слово» — конец HTML-сущности, не знак
        before = t[:j + 1]
        # многоточие сразу после пробела, скобки, кавычки или в начале — начало цитаты
        if re.search(r'(?:^|[\s(«„"—;])(?:\.{2,}|…)$', before):
            continue
        sep = '&nbsp;' if m.group(1) == '.' and ABBR.search(t[max(0, j - 6):j + 1]) else ' '
        out.append(t[i:j + 1] + sep)
        i = j + 1
    out.append(t[i:])
    t = ''.join(out)
    # дефис вместо тире, прилипший к одному из слов: «Бунина- кольцо», «Минус- принижение», «» -песни» →
    # неразрывный пробел + длинное тире + пробел (владелец 2026-10-17)
    t = re.sub(r'(?<=[А-Яа-яЁё»).!?,])-\s+', '&nbsp;&mdash; ', t)
    t = re.sub(r'\s+-(?=[А-Яа-яЁё«(])', '&nbsp;&mdash; ', t)
    # после слова со знаком перед цифрой — тоже пробел: «(см.2.3.)» → «(см. 2.3.)» (сокращение — неразрывный);
    # «1.4» (цифра.цифра) не трогаем
    t = re.sub(r'(?<=[А-Яа-яЁё])([.,:;])(?=\d)', lambda m: m.group(1) + ('&nbsp;' if m.group(1) == '.' else ' '), t)
    t = re.sub(r'(т\.(?:&nbsp;)?[дпе])\.\.(?!\.)', r'\1.', t)    # «т.д..» → «т. д.»
    return initials(t)


def initials(t):
    # инициалы не отрываются ни друг от друга, ни от фамилии: «Л. И. Блехер», «М. Щербаков» — неразрывные
    # пробелы (владелец 2026-10-17)
    return re.sub(r'(?<![А-Яа-яЁёA-Za-z])((?:[А-ЯЁ]\.(?:\s|&nbsp;)*){1,2}?)(?:\s|&nbsp;)*(?=[А-ЯЁ](?:[а-яё]|\.))',
                  lambda m: re.sub(r'\.(?:\s|&nbsp;)*', '.&nbsp;', m.group(1)), t)


def unstick(body):
    # только текст между тегами (не адреса в href, не имена файлов)
    body = re.sub(r'(?<=>)([^<]+)(?=<)', lambda m: unstick_text(m.group(1)), body)
    # знак, прилипший к открывающей кавычке или к букве через границу тегов: «Жуков пишет:</a><i>«Это» →
    # «пишет:</a> <i>«Это» (пробел — после закрывающих тегов, перед открывающими)
    body = re.sub(r'([,;:!?])(?=«)', r'\1 ', body)
    return re.sub(r'([,;:!?])((?:</[a-z]+>)+)((?:<[a-z][^>]*>)*)(?=«|[А-Яа-яЁё])', r'\1\2 \3', body)


def continuations(body):
    # абзацы без имени после реплики (в исходнике реплика шла несколькими <p>) — её продолжение (p.cont), пока не
    # начнётся следующая реплика, связка составителей, вопрос, линия или заголовок (владелец 2026-10-17)
    parts = body.split('\n\n')
    in_reply = False
    for i, p in enumerate(parts):
        if p.startswith('<p class="speaker">'):
            in_reply = True
        elif p.startswith('<p>') and in_reply and not p.lstrip('<p>').startswith('©'):
            parts[i] = '<p class="cont">' + p[3:]
        elif p.startswith(('<p class="cont">', '<blockquote>')):
            pass
        else:
            in_reply = False
    return '\n\n'.join(parts)


DASH = r'(?:&nbsp;)?&mdash;\s*'


def dash_lists(body):
    # перечни с тире в начале строки («— излишняя мрачность…») — список ul.dashes (маркер — короткое тире);
    # «…высказывания:&nbsp;&mdash; первый пункт» — пункт отделяется от вводной фразы (владелец 2026-10-17)
    def from_br(m):
        cls, head, items = m.group(1) or '', m.group(2), re.split(r'<br>\s*' + DASH, m.group(3))
        ul = 'dashes editorial' if 'editorial' in cls else 'dashes'
        return (f'<p{cls}>{head}:</p>\n\n<ul class="{ul}">\n' +
                ''.join(f'<li>{x.strip()}</li>\n' for x in items if x.strip()) + '</ul>')
    body = re.sub(r'<p( class="[^"]*")?>([^\n]*?):\s*<br>\s*' + DASH + r'((?:(?!</p>).)*?)(?:<br>\s*)?</p>',
                  from_br, body)
    parts = body.split('\n\n')
    out, i = [], 0
    item = re.compile(r'<p(?: class="cont")?>' + DASH + r'(.*)</p>$', re.S)
    while i < len(parts):
        j = i
        while j < len(parts) and item.match(parts[j]):
            j += 1
        if j - i >= 2 or (j - i == 1 and out and re.search(r':' + DASH + r'.+</p>$', out[-1], re.S)):
            items = [item.match(x).group(1) for x in parts[i:j]]
            if out:
                m = re.match(r'(.*?:)' + DASH + r'(.+)</p>$', out[-1], re.S)
                if m:
                    out[-1] = m.group(1) + '</p>'
                    items.insert(0, m.group(2))
            out.append('<ul class="dashes">\n' + ''.join(f'<li>{x.strip()}</li>\n' for x in items) + '</ul>')
            i = j
            continue
        out.append(parts[i])
        i += 1
    return '\n\n'.join(out)


def quote_sources(body):
    # подпись под цитатой — отдельным абзацем внутри цитаты, прямым шрифтом, без скобок, с отбивкой, как у авторов
    # («И. Бродский.» в 4.3); короткая строка-подпись сразу после цитаты переносится в неё (владелец 2026-10-17)
    body = re.sub(r'<br>QSRC([^<]*)</p></blockquote>',
                  lambda m: f'</p>\n<p class="quote-source">{initials(m.group(1))}</p></blockquote>', body)
    return re.sub(r'</blockquote>\n\n<p(?: class="cont")?>([А-ЯЁ]\.(?:&nbsp;|\s)?[А-ЯЁ][а-яё]+\.?)</p>',
                  r'\n<p class="quote-source">\1</p></blockquote>', body)


SMILEY = r'[:;]-?[()]+'


def wrap_comments(t):
    # «(Комментарий Бориса Жукова: …)» внутри реплики, набранный прямым, — курсивом; скобки — по вложенности,
    # смайлики «:-)» не считаются
    out, i = [], 0
    for m in re.finditer(r'(?<!<i>)\((?=Коммент[а-я]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+:)', t):
        if m.start() < i:
            continue
        j, depth = m.end(), 1
        while j < len(t) and depth:
            sm = re.match(SMILEY, t[j:])
            if sm and t[j] in ':;':
                j += sm.end()
                continue
            if t.startswith('</p>', j):
                break
            depth += {'(': 1, ')': -1}.get(t[j], 0)
            j += 1
        if depth:
            continue
        out.append(t[i:m.start()] + '<i>' + t[m.start():j] + '</i>')
        i = j
    out.append(t[i:])
    return ''.join(out)


def unbold_inner(p):
    # полужирное внутри текста (не подпись в начале абзаца): в курсиве — прямым начертанием курсива, иначе — курсивом
    # («Прим. ред.:», «Комментарий Бориса Жукова:» внутри скобок, выделенные слова) (владелец 2026-10-17)
    m = re.match(r'(<p[^>]*>(?:<a id="[^"]*"></a>)?(?:<i>)?<b>[^<]*</b>)?', p)
    head, rest = (m.group(1) or ''), p[len(m.group(1) or ''):]
    italic_ctx = 'editorial' in p[:30] or (head.endswith('</b>') and '<i><b>' in head)
    out, depth, pos = [], 0, 0
    for t in re.finditer(r'<(/?)(i|b)>', rest):
        out.append(rest[pos:t.start()])
        tag, close = t.group(2), t.group(1)
        if tag == 'i':
            depth += -1 if close else 1
            out.append(t.group(0))
        else:
            out.append('' if (italic_ctx or depth > 0) else ('</i>' if close else '<i>'))
        pos = t.end()
    out.append(rest[pos:])
    return head + ''.join(out)


def polish(body):
    # имя, прилипшее к концу чужой реплики («…к частному. <b>Дмитрий</b>» + продолжение) — новая реплика
    body = re.sub(r'\s*<b>([А-ЯЁ«][^<:.]{1,30})</b></p>\n\n<p class="cont">',
                  r'</p>\n\n<p class="speaker"><b>\1.</b> ', body)
    body = wrap_comments(body)
    # (вопрос — полужирный целиком, его не трогаем)
    body = '\n\n'.join(unbold_inner(p) if p.startswith('<p') and not p.startswith('<p class="question">') else p
                         for p in body.split('\n\n'))
    # комментарий-реплика с переводом строки внутри курсива — второй абзац красной строкой
    body = re.sub(r'(<p class="speaker"><i>.*?)</p>', lambda m: m.group(1).replace('<br>', '</i></p>\n\n<p class="cont"><i>')
                  + '</p>', body)
    body = re.sub(r'(<p class="editorial"><b>.*?)</p>',
                  lambda m: m.group(1).replace('<br>', '</p>\n\n<p class="editorial cont">') + '</p>', body)
    # «J» — смайлик Wingdings из Word: «сосну? J Кстати» → «сосну? :) Кстати»
    body = re.sub(r'(?<=[?!.]) J (?=[А-ЯЁ])', ' :) ', body)
    # смайлик — через пробел от знака препинания: «намотана...:-)» → «намотана... :-)»
    body = re.sub(r'(?<=[.!?…,])(?=[:;]-?\)+)', ' ', body)
    return body


# ответы читателей по вопросам — в гостевой книге «Обсуждение» (content/SCH2/gb/gb-index.md), пометка «Вопрос 1.3»
_GB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../content/SCH2/gb/gb-index.md')
GB_COUNT = {}
if os.path.exists(_GB):
    for k in re.findall(r'class="gb-entry q(\d+)"', open(_GB).read()):   # записи помечены вопросом
        GB_COUNT[k] = GB_COUNT.get(k, 0) + 1


def readers_link(body, n):
    # после ответов экспертов — строка со ссылкой-якорем на ответы читателей в обсуждении (владелец 2026-10-17)
    k = n[:3]
    cnt = GB_COUNT.get(k)
    if not cnt or n == '401-2':
        return body
    line = (f'<p class="readers">Ответы читателей на этот вопрос ({cnt})&nbsp;&mdash; '
            f'<a href="gb/index.html#q{k}">в обсуждении</a>.</p>\n\n')
    i = body.rfind('<hr>')
    return body[:i] + line + body[i:] if i >= 0 else body + '\n\n' + line
