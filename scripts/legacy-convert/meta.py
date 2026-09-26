# name: dict(title, author, subtitle, back, lastmod, drop_first, replace=[(a,b)], drop_last)
import re
FAN = ('fans/index.html#articles', 'Фан-клуб')
CREATIVE = ('fans/index.html#creative', 'Фан-клуб')
def kom(anchor):
    a = re.sub(r'\d{4}$', '', anchor)
    a = {'onceinou': 'once'}.get(a, a)
    return ('fans/kom.html#' + a, 'Словарь заморских слов')
META = {
 'andr2': dict(title='Веселый талант мрачного человека', back=FAN, lastmod='1998-12-15', drop_first=1, drop_last=1,
    replace=[('нельзя! »', 'нельзя!»'), ('словно наполнена Ока мышами?“', 'словно наполнена Ока мышами?“»'), ('„Траур воронов', '«Траур воронов'), ('ждалось страшное.“', 'ждалось страшное.»')]),
}
META.update({
 'andrianov': dict(title='Андрей Андрианов', back=FAN, drop_first=1),
 'andr-rusalka': dict(title='М. Щербаков: опыт комментария', author='Андрей Андрианов', back=FAN, drop_first=2, lastmod='1998-12-15'),
 'andr-rusalka-d': dict(title='Обсуждение эссе А.Андрианова о песне «Русалка, цыганка, цикада...» В.Смирновым и Д.Полонским', back=FAN, drop_first=2, drop_last=1, lastmod='1998-12-15'),
 'answer': dict(title='Ответы на кроссворд по песням 1990-1994', author='С. Карина', back=('fans/crossword.html', 'Кроссворд'), drop_first=1),
 'bes': dict(title='Вероятный генезис гостиничных сцен в «Предположим»', back=kom('predpolo1995'), keep_table=True),
})
META.update({
 'bom-bram': dict(title='бом-брам-рей-грот-шкот', back=kom('neznajuk1995'), lastmod='1997-05-08'),
 'brahms': dict(title='Nachtwache (Брамс — Рюккерт)', back=kom('nochnoj1998')),
 'elfy': dict(title='«Эльфийская»', back=kom('jubilejn1985')),
})
META.update({
 'polkovnik': dict(title='«Здравствуйте, полковник...»', back=kom('svidanie1990')),
 'lirika': dict(title='Застольная', back=kom('zastolnaya2001'), fontmap={'#ff0000': 'datum'}),
 'mandlsh2': dict(title='«Прощальный марш» и Мандельштам', back=kom('proschalm2009')),
 'mandlsht': dict(title='«Прощание с Петербургом» и Мандельштам', back=kom('proschanie2006')),
 'eslinado': dict(title='Если надо — объяснят', back=kom('nerazmen1999'), fontmap={'#ff0000': 'datum'}),
})
META.update({
 'metafora': dict(title='Какого века есть метафора сия?', back=kom('drugoe1993'), drop_first=1),
 'sardanapal': dict(title='Аменхотеп, Ассаргадон, Анаксимандр', back=kom('inicialy1996'), drop_first=1),
 'rakety': dict(title='«Мои ракеты» — трактовка', back=kom('moiraket1994'), drop_first=1),
 'shuty': dict(title='Опять о шутах', back=kom('pazh1986')),
 'nikst-glaza': dict(title='Эти глаза напротив', back=kom('etiglaza1992')),
 'oncetran': dict(title='Once — переводы', back=kom('onceinou1995')),
 'mueller': dict(title='Gute Nacht — переводы', back=kom('eccehomo1990')),
 'horatius': dict(title='Ad Leuconoen', back=kom('adleucon1987')),
 'rubcov-doroga': dict(title='Николай Рубцов. Дорога', back=kom('doroga1985')),
 'kogolublu': dict(title='Рифмы и созвучия в «Кого люблю, того не встречу»', back=kom('kogoljub1994'), fontmap={'#000080': 'rhyme'}),
 'szs-intrm4': dict(title='Интермедия — 4', back=kom('interme41998')),
 'zhandarov': dict(back=FAN), 'julia': dict(back=FAN), 'suzy1': dict(back=FAN), 'fedenkova': dict(back=FAN), 'rechisty': dict(back=FAN),
 'potop': dict(back=CREATIVE), 'katrin': dict(back=CREATIVE),
 'izvraty': dict(back=CREATIVE), 'chgk': dict(back=CREATIVE), 'chgkizb': dict(back=CREATIVE), 'bestiar': dict(back=CREATIVE),
 'herbary': dict(back=CREATIVE), 'memory': dict(back=CREATIVE), 'comix/comix': dict(back=CREATIVE),
})
META['chgk'] = dict(title='Вопросы «Что? Где? Когда?»', back=CREATIVE, replace=[('«Тайны мадридского двора опубликован', '«Тайны мадридского двора» опубликован'), ('„Скотный двор“', '«Скотный двор»')], fontmap={'#fffff0': 'spoiler'}, drop_first=1,
    subtitle='Вопросы, связанные с творчеством М. Щербакова, из <a href="http://chgk.zaba.ru/">базы вопросов</a> «Что? Где? Когда?»')
META['chgkizb'] = dict(title='Избранные вопросы «Что? Где? Когда?»', back=CREATIVE, replace=[('<h3>Это не все', '<p><i>Это не все'), ('в базе.</h3>', 'в базе.</i></p>')], fontmap={'#fffff0': 'spoiler'}, drop_first=1,
    subtitle='Избранные вопросы, связанные с творчеством М. Щербакова, из <a href="http://chgk.zaba.ru/">базы вопросов</a> «Что? Где? Когда?»')
META['discussion'] = dict(title='Обсуждения', src_replace=[('"Чумки"<font color="magenta">', '"Чумки"</a> <font color="magenta">'), ('плеоназме <font color="magenta">', 'плеоназме </a><font color="magenta">')], replace=[('формулировке „Нарцисс-пессимист“...', 'формулировке „Нарцисс-пессимист“...»')], back=('fans/index.html', 'Фан-клуб'), fontmap={'magenta': 'datum'}, lastmod='2022-08-07', drop_first=1)
META['izvraty'] = dict(title='Щербаковинки — ослышки, оговорки, изврат', back=CREATIVE, lastmod='2020-05-18',
    replace=[('«Свежо дышал „Зенит“...</i>', '«Свежо дышал „Зенит“...»</i>')])
META['potop'] = dict(title='Комментарий к песням Михаила Щербакова', author='Дмитрий Вильмс', back=CREATIVE)

def _herb_letters(html):
    def rep(m):
        cells = re.findall(r'<b>(?:<a href="herbary\.html#(\w+)">)?(\w)', m.group(0))
        return '<p align=center>' + ' '.join('<a href="#%s">%s</a>' % (a, l) if a else l for a, l in cells) + '</p>'
    return re.sub(r'<table border=1.*?</table>', rep, html, flags=re.S)
import re
META['herbary'] = dict(title='Гербарий, составленный по песням М. Щербакова', back=CREATIVE, lastmod='2012-12-06', split_br2=True, src_fn=_herb_letters, drop_first=2,
    replace=[('<p>…вот и будет мне полный гербарий,<br>вот и сложится пышный букет!</p>\n\n<p><em>М.&nbsp;Щербаков , «Тоска по родине»</em></p>',
              '<blockquote class="epigraph">\n<p>…вот и будет мне полный гербарий,<br>вот и сложится пышный букет!</p>\n<p><em>М.&nbsp;Щербаков, «Тоска по родине»</em></p>\n</blockquote>')])
META['bestiar'] = dict(title='Бестиарий, составленный по песням М. Щербакова', back=CREATIVE, lastmod='2012-12-06', split_br2=True, drop_first=2,
    replace=[('<p class="verse">Животные делятся на:', '<blockquote class="epigraph">\n<p>Животные делятся на:'),
             ('на мух.</p>\n\n<p><em>Х.-Л.Борхес, «Аналитический язык Джона Уилкинса»</em></p>', 'на мух.</p>\n<p><em>Х.-Л.Борхес, «Аналитический язык Джона Уилкинса»</em></p>\n</blockquote>')])

META['katrin'] = dict(title='Витамин Щ, или Под псевдонимом Фортуны', subtitle='Пьеса', author='Catherine', back=CREATIVE, lastmod='2021-08-14', drop_first=3,
    replace=[('<h3><b><a id="s7">*** Сцена седьмая ***</a></b></h3>', '<h3><a id="s7">*** Сцена седьмая ***</a></h3>'),
             ('<p><b><h4>Чаепитие первое, оно же второе</h4> <p>Комната Дена.', '<h4>Чаепитие первое, оно же второе</h4>\n\n<p>Комната Дена.'),
             ('не вставая с дивана. </p></b></p>', 'не вставая с дивана.</p>')])
META['comix/comix'] = dict(title='Комикс по песне «Десять первых лет...»', back=CREATIVE, lastmod='2009-02-13', drop_first=1,
    subtitle='Работа <a href="mailto:elenamariu@mail.ru">Лены Мариупольской</a>. Оригинал <a href="http://www.diary.ru/~scherbakov/p61113898.htm">здесь</a>.')

def _comix(html):
    return html.replace('<BR><BR>\n  <img', '</p><p align=center><img').replace('<td align="left">\n  <img', '<td align="left"><p align=center><img').replace('<BR><BR>\n  Десять', '</p><p>Десять').replace('<br><BR>\n  <img', '</p><p align=center><img').replace('height="500">\n  </td>', 'height="500"></p></td>')
META['comix/comix']['src_fn'] = _comix
META['memo/schneider'] = dict(title='Памяти Виктора Шнейдера', back=('fans/index.html', 'Фан-клуб'), lastmod='2003-10-11')
META['memo/podborka'] = dict(title='Виктор Шнейдер. Из последних и найденных стихов', back=('fans/memo/schneider.html', 'Памяти Вити Шнейдера'), lastmod='2002-06-17')

META['memo/podborka'].update(drop_first=1, replace=[
  (r're:^<blockquote>\n<p>(<img [^>]*>) <b>(<a [^>]*>ВИКТОР ШНЕЙДЕР</a>)</b><br><b>\(([^)]*)\)</b></p>\n\n<p><b><i>Из последних и найденых стихов</i></b></p>\n',
   r'<p class="center">\1</p>\n\n<p class="center"><b>\2</b><br>(\3)</p>\n\n<h2>Из последних и найденых стихов</h2>\n'),
  (r're:\n</blockquote>\s*$', '\n')])
META['kogolublu'].update(replace=[('<pre>\n\n</pre></pre>', '</pre>'), ('"шутишь!"', '«шутишь!»')])

META['utf/covers'] = dict(title='Каверы в исполнении Михаила Щербакова', author='Алексей Тугарев', back=('fans/index.html#creative', 'Фан-клуб'), lastmod='2024-04-01',
    replace=[('href="concerts.html"', 'href="../../concerts.html"')])
META['parabola'] = dict(title='Парабола Лобачевского', back=kom('pesenkao1990'), drop_first=1)

META['utf/crocodile'] = dict(title='Крокодилиада', back=('fans/index.html#creative', 'Фан-клуб'), drop_first=2, drop_last=1)
META['answer'].update(replace=[('<b>ФРАНЦИЯ»</b>, ария французов:«Ведь', '<b>ФРАНЦИЯ</b>», ария французов: «Ведь')])

META['katrin'].pop('no_typo', None)
META['eslinado'].update(replace=[('кто тЫ»»', 'кто тЫ“»')])
