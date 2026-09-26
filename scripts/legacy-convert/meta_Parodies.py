# Пародии: имя -> параметры (см. README)
import re
IDX = ('Parodies/index.html', 'Пародии')
FREE = ('Parodies/index.html#free', 'Пародии')
INV = ('Parodies/index.html#inv', 'Пародии')
META = {
 'alter': dict(title='Альтернативный взгляд на ситуацию глазами действующих лиц', drop_first=1, lastmod='2009-06-04'),
 'anon2': dict(title='Ещё один конспект'),
 'antropo': dict(title='И еще нечто', lastmod='2000-04-12'),
 'avdeev': dict(title='Однажды, в год Собаки', author='Сергей Авдеев', lastmod='2007-03-03'),
 'black': dict(title='Descensus ad Inferos', drop_first=1, lastmod='2007-04-16'),
 'bystrov3': dict(title='Быстров — 3. Версия Рыбы', drop_first=1, lastmod='2009-06-25'),
 'doctor': dict(title='Переписываем классику классикой: доктор с Волхонки', drop_first=1, lastmod='2006-02-16'),
 'dubinchik': dict(title='Щербакиана', author='Аркадий Дубинчик', drop_first=2, lastmod='1999-02-27'),
 'eli-kovcheg': dict(title='Ковчег, еще ковчег', lastmod='1998-07-01'),
 'epikriz': dict(title='Эпикриз', author='Александр Барский', drop_first=2, lastmod='2003-05-01'),
 'fbuket2': dict(title='Фиалковый букет / Bouquet of Roses', back=FREE),
 'filatov': dict(title='Породии', author='Александр Филатов', drop_first=1, lastmod='2006-12-09'),
 'gagarin': dict(title='Запоздалое посвящение 37-летию полета Гагарина', lastmod='1998-07-01'),
 'goloboro': dict(title='Пародии Д. Голобородько', back=FREE, drop_first=1),
 'gorchitza': dict(title='Горчица', subtitle='Инверсия на «Вишневое варенье»', author='Александр Доброчаев и Дмитрий Главацкий', drop_first=2, back=INV, lastmod='2003-09-10'),
 'greenland': dict(title='Гренландия', subtitle='Инверсия на «Австралию»', back=INV, lastmod='2005-03-22'),
 'ingwall': dict(title='Пародия на «Ландыш»', author='Вадим Барановский', lastmod='1999-01-30'),
 'isakevich': dict(title='Пародия Евгения Исакевича', lastmod='2004-02-14'),
 'jeka': dict(title='Песенка', author='Евгения Голосовская', lastmod='1999-09-12'),
 'kaketo': dict(title='Как это было на самом деле', author='Александр Вольнов', lastmod='2020-06-20'),
 'kaznacheev': dict(title='Пародии В. Казначеева, В. Фуксмана и А. Штурма'),
 'kolobok': dict(title='Колобок', lastmod='2007-08-31'),
 'kolobok2': dict(title='Колобок', lastmod='2007-08-31'),
 'konglomerat': dict(title='Конгломерат', lastmod='1998-07-01'),
 'kozlik': dict(title='Пародия на песню «Новый гений»', author='Дмитрий Коломенский'),
 'kozlik2': dict(title='«Жил-был у бабушки серый полковник»', author='Александр Данковский', lastmod='2006-02-16'),
 'kuk': dict(title='Почему аборигены съели Кука', subtitle='Посылка к Михаилу Щербакову', author='Андрей Земсков', lastmod='2006-08-09'),
 'lambda2': dict(title='Lambda (Австралия)', back=FREE, lastmod='2009-03-09'),
 'landysh': dict(title='Нечто', lastmod='2013-04-05'),
 'losos': dict(title='Лосось', subtitle='пародия на «Быстрова»', author='Александр Аврутин', lastmod='2013-09-15'),
 'makeeva': dict(title='Пародия Ольги Макеевой', lastmod='1999-02-27'),
 'mapka': dict(title='Пародия от map-ka', lastmod='2007-04-22'),
 'medvedev': dict(title='Пародии Владимира Медведева'),
 'mumu': dict(title='Два слова Муму', author='Михаил Рабинович', lastmod='2007-02-03'),
 'mundial': dict(title='Пародии Евгения Рубашкина', lastmod='2008-06-05'),
 'mundshtuk': dict(title='Мундштук'),
 'myachik': dict(title='Мячик', author='Никита Дорофеев', lastmod='2004-03-17'),
 'nenado': dict(title='Пародии Валентина Евстафьева', lastmod='2006-12-09'),
 'nesterenko': dict(title='Пародии Юрия Нестеренко', lastmod='1999-09-05'),
 'never': dict(title='Никогда', lastmod='2007-04-22'),
 'pesenkar': dict(title='Песенка рыбы', lastmod='2009-06-04'),
 'physics': dict(title='Ещё одна пародия на «Австралию»', author='Лев Козлов'),
 'piglet1': dict(title='Три поросёнка', lastmod='2010-01-25'),
 'piglet2': dict(title='Три поросёнка', lastmod='2010-01-25'),
 'piglet3': dict(title='Три брата', lastmod='2010-12-22'),
 'pingvin': dict(title='ПИнгвин', lastmod='2014-10-19'),
 'pisenka': dict(title='Пiсенька (Песенка)', author='Леон Позен', back=FREE, lastmod='1999-09-05'),
 'polkovn': dict(title='Полковник', author='Александр Воронцов', lastmod='2009-06-25'),
 'proliv2': dict(title='Пролив', back=FREE),
 'ryaba': dict(title='Тема курочки Рябы', lastmod='2012-06-06'),
 'rybakovf': dict(title='A Song of Wall Street Hookers (Песня рыбаков Флориды)', back=FREE, lastmod='2009-09-01'),
 'rybakryb': dict(title='Рыба к «Рыбе»', author='Виктор Филимоненков', lastmod='2009-10-11'),
 'schneider': dict(title='Пародии Виктора Шнейдера', lastmod='1999-11-26'),
 'shtirlic': dict(title='«Штирлиц агент отличный...»', author='Вит. Гуткин, Б. Шкурский', lastmod='1998-07-01'),
 'sobaki': dict(title='Пародия на «Бродяг»', author='Джориан', lastmod='2000-04-12'),
 'tralivali': dict(title='Трали-вали', subtitle='Инверсия на «Аллилуйя»', author='Виктор Филимоненков', back=INV, lastmod='2010-10-07'),
 'transeuro': dict(title='Транс-Европа', author='Алексей Чуев', lastmod='2006-09-04'),
 'tsukanova': dict(title='Пародии Анны Цукановой', lastmod='2000-04-12'),
 'utro': dict(title='Утро в сосновом лесу', author='В. Фуксман'),
 'woman': dict(title='Женское обращение к герою', author='Анна Тикина', lastmod='2008-08-27'),
 'ziplakov': dict(title='Трагическое напутствие', author='Г. Циплаков', lastmod='2004-10-07'),
}

META['index'] = dict(title='Пародии', back=('fans/index.html', 'Фан-клуб'), fontmap={'ff0000': 'datum'}, lastmod='2020-06-20')
def _upd(n, **kw):
    META.setdefault(n, {}).update(kw)
for n in ('kolobok', 'kolobok2', 'kozlik2', 'losos', 'makeeva', 'nesterenko', 'pesenkar', 'piglet1', 'piglet3', 'pingvin', 'rybakryb', 'ryaba', 'woman', 'mundial', 'nenado', 'isakevich', 'jeka', 'kozlik'):
    _upd(n, drop_first=1)
_upd('kolobok2', title='Колобок 2')
_upd('piglet2', title='Люпус и свинтус', drop_first=1)
_upd('myachik', drop_first=2)
_upd('kuk', drop_first=3)
_upd('greenland', drop_first=2)
_upd('tralivali', drop_first=2)
_upd('isakevich', author='Евгений Исакевич, Апатиты')
_upd('jeka', title='Песенка')
_upd('kozlik', author='Дмитрий Коломенский')
_upd('kaketo', replace=[('<h3>Как это было на самом деле</h3>\n\n', '')])
_upd('ziplakov', replace=[('<h2>Трагическое напутствие</h2>\n\n', '')])
_upd('never', replace=[('<h1>И правильно!</h1>', '<p>И правильно!</p>')])
_upd('proliv2', title='The straits of Bab el-Mandeb (Баб-эль-Мандебский пролив)')
_upd('fbuket2', title='Bouquet of Roses (Фиалковый букет)')
_upd('index', replace=[('<h2>Пародии</h2>\n\n', '')])
