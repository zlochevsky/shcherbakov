# «Щ-2» (социологический проект, 2000): опубликован как на старом сайте (решение владельца 2026-09-24)
SOC = ('sociology.html', 'Социология')
HUB = ('SCH2/index.html', 'Щ-2')
META = {
 'index': dict(title='«Щ-2»', back=SOC, lastmod='2000-05-20', replace=[('<h2>«Щ-2»</h2>\n\n', '')]),
 '103-e': dict(title='Вопрос 1.3', back=HUB,
               replace=[('<p><a id="zhukov"><p> <u>Борис Жуков</u>', '<p><a id="zhukov"></a><u>Борис Жуков</u>'),
                        ('<p><a id="zhukov"><u>Владимир Смирнов</u>', '<p><u>Владимир Смирнов</u>')]),
 'gb/index': dict(title='Обсуждение', back=HUB, replace=[('href="../profiles"', 'href="../profiles.html"'), ('<h2>Обсуждение</h2>\n\n', '')]),
 'profiles': dict(title='Личные профили респондентов', back=HUB,
                  replace=[('href="../smirnov/"', 'href="../fans/smirnov/index.html"'), ('href="../smirnov"', 'href="../fans/smirnov/index.html"'), ('href="../index.html"', 'href="index.html"'), ('<h2>Личные профили респондентов</h2>\n\n', '')]),
}
