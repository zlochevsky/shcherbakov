[English version](frontmatter.md)

# Справочник параметров front matter

Поля front matter (JSON-блок в начале `content/**/*.md`), которые реально читают шаблоны из `layouts/`. Сверено с `layouts/` и всеми файлами контента 2026-10-02; разделы о переводах, языковых страницах и `Disks/other.md` добавлены 2026-10-07. Поля, которые есть в контенте, но не читаются ни одним шаблоном, помечены **не используется**.

Не входит: коллекции Directus (works, events, perfs, sets, books, comments, announces…) — см. [docs/directus.md](directus.md); `params` пунктов меню в `config/_default/menus.json` (`isDateToPrint`, `dynamicLastmod`, `collapsible`, `toggleChild`, `mobileOnly`, `shortName`, `dropdown`, `lang`) — в шаблонах они выглядят как `.Params.*`, но относятся к настройкам меню, а не к файлам `.md`.

## Стандартные поля Hugo

См. [документацию Hugo](https://gohugo.io/content-management/front-matter/).

- `title` — `<h1>` и запасной `<title>` страницы.
- `type`, `layout` — выбор шаблона. В контенте — `"type": "miscellaneous"` и явный `"layout"` (имя файла шаблона в `layouts/miscellaneous/`); страницам песен (`songpage`) и страницам языковых папок (`translation`) оба задают правила `cascade` в `hugo.json`, поэтому языковая страница, которая не перевод, задаёт свой `layout` сама.
- `url` — адрес страницы; стоит почти у всех страниц, чтобы сохранить адреса старого сайта (`"/Disks/minsk3.html"`).
- `aliases` — старые адреса, которые должны вести на эту страницу.
- `date`, `lastmod` — даты; `lastmod` даёт дату «обновлено» у некоторых пунктов меню.
- `"sitemap": {"disable": true}` — не включать страницу в `sitemap.xml` (страницы-редиректы, `fans/kom2`). Для страниц песен — свои правила, см. ниже.
- `"build": {"render": "never", "list": "never"}` — страница не выводится сама: её вставляет другой шаблон (`Books/other-publications.md` на странице «Книги»; `_footer.md` — подвал главной) или из неё только читают настройки (раздел языка, у главной страницы которого ещё нет текста; на 2026-10-09 таких нет: главные страницы есть у всех шести языков).
- `draft`, `publishDate`, `expiryDate` — сейчас в контенте не используются (ручные `content/announces/` и их заготовка удалены 2026-10-02: анонсы берутся из Directus).

## Общее оформление (большинство страниц)

- `params.subtitle` — подзаголовок `<h2>` под `<h1>`. Не путать с общим `site.Params.Subtitle` из `hugo.json`.
- `params.name` — короткое имя страницы независимо от `<h1>` (меню, основа `<title>` по умолчанию); по умолчанию — `title`.

## Поисковики и превью ссылок — все страницы, кроме редиректов

`<title>`, description, `noindex`, canonical и Open Graph выводит один партиал — `layouts/partials/seo.html` (добавлен 2026-10-13).

- `description` (стандартное поле Hugo) — `<meta name="description">` и `og:description`. Задано у основных статических страниц; песни, переводы, диски, кассеты, книги, циклы и статьи из Praises получают сгенерированное, если поле пустое.
- `params.seoTitle` — полный `<title>` (и `og:title`), выводится как есть. Без него заголовок собирается: по типу страницы у песен, переводов, дисков, книг, циклов и статей из Praises; иначе `params.name`/`title` плюс суффикс раздела: « — Михаил Щербаков» (витрина), « — фан-клуб Михаила Щербакова» (`fans`, `Parodies`, `FOM`, `SCH2`, `Images`), имя автора на языке раздела (языковые папки); без суффикса, если в имени уже есть «Щербаков» или «Shcherbakov».
- `params.noindex` (bool) — `noindex, follow` и без canonical (например, `search.md`, `Cycles/monologi.md`).
- `params.author` (статьи Praises) — ещё и в сгенерированном заголовке (до первой запятой) и описании.

canonical и `og:url` указывают на саму страницу, а если в `hugo.json` задан `params.canonicalBase` (сейчас пуст) — на тот же путь по этому адресу: на случай, когда копия сайта публикуется под другим доменом.

## Анонсы — только `content/news.md`

Читаются `header.html` (главная) и `news.html` через `site.GetPage "news"`. Сами анонсы — из коллекции `announces` в Directus (`partials/announces.html`).

- `params.showAnnounce` (bool) — показывать ли список анонсов вообще (шапка главной и страница новостей).
- `params.announceTitle` — заголовок над списком на странице новостей.
- `params.announce` (массив строк Markdown) — старые вручную написанные строки, добавляются после анонсов из Directus. Сейчас пусто.
- `params.showAnnounceTitle`, `params.showAnnounceOnHome` — **не используются**.

## Страницы песен — `content/texts/<год>/<id>.md`

Один файл на песню: короткий front matter, текст песни — тело файла (читается как есть, `.RawContent`, без Markdown; пустые строки перед текстом пропускаются, так что пустая строка после front matter, которую ставит редактор в браузере, ничего не меняет). Имя файла — id песни (`works.id`), папка — год актуальной редакции. `<h1>`, `<title>`, description и видимость берутся из Directus (`works.fname`/`name`/`fincipit`/`incipit`, `works.noindex`, `works.hidden`), см. [docs/directus.md](directus.md).

- `params.tonality` (напр. `"Hm"`) — исходная тональность для транспонирования. Если пусто, `song.html` угадывает её по аккордам; явное значение надёжнее.
- `params.chordsStartAt` (число, столбец с 1) — где начинаются аккорды; по нему строки делятся на текст и аккорды. Для стихов без аккордов не задаётся.
- `params.textFinishAtLine` (число, строка тела с 0) — с этой строки идёт не текст песни, а то, что выводится как есть в блоке `<pre>` (табулатуры, примечания). По умолчанию — последняя строка. То же самое число — номер последней строки текста песни, считая с 1; его показывает плашка редактора на этой строке.
- `params.editionOf` — id актуальной редакции; помечает раннюю редакцию: noindex, не в sitemap, заголовок и год — от актуальной редакции, плашка-ссылка на неё.
- `title` (в корне, необязательно) — только для ранней редакции с другим названием (`pazh0`); `"* * *"` — ранняя редакция без названия (`japomnju`), тогда `<title>` и description берутся из её первой строки.
- `aliases` — старые адреса переименованной страницы.

## Альбомы и кассеты — `content/Disks/*.md` (`diskpage`), `content/Tapes/*.md` (`tapepage`)

- `params.id` — `sets.id` в Directus; название, год, формат, картинки и список песен берутся из набора.
- `params.year`, `params.image`, `params.images` — запасные значения, только если у набора пусто `year` / `album_img` / `extra_images`; сейчас ни у одной страницы не заданы.
- Полноразмерные версии картинок задаются не во front matter, а именем файла: см. «Полноразмерные изображения» у `sets` в [docs/directus.md](directus.md).

## Книги — `content/Books/*.md` (`bookpage`)

- `params.id` — `books.id` в Directus. Обложка: `books.photo`, иначе `Images/bkp/<id>.jpg`.
- `params.buyUrl` — ссылка «купить», выводится кнопкой, если задана.

## Циклы песен — `content/Cycles/*.md` (`cycle`)

- `params.id` — id цикла в Directus (`cycles`).

## Статьи, фан-клуб, пародии — `praises-article` (Praises, FOM, fans, Parodies, SCH2 и др.)

- `title`, `params.subtitle`, `params.author` — заголовочный блок.
- `params.backUrl`, `params.backTitle` — ссылка «назад» в угловой навигации. Без них страница из `content/fans/` получает «Фан-клуб → fans/index.html»; в остальных разделах задаются явно.
- `params.bgColor` — фон страницы (хаб клуба `fans/fans-index.md`).
- `params.monoPre` (bool) — `<pre>` моноширинным шрифтом (`<body>` страницы получает `class="mono-pre"`). По умолчанию `<pre>` набирается шрифтом страницы: в фан-клубе и пародиях там в основном стихи и цитаты. Ставится там, где текст выровнен пробелами: `tab.md` (табулатуры), `statistics.md` (таблицы), письма разделов из приватного слоя (2026-10-14). Кроссворды (`<pre class="crossword">`) моноширинные и без него.
- `params.palette` (строка) — своя цветовая гамма страницы: `<body>` получает `class="palette-<имя>"`, который переопределяет переменные палитры (`assets/css/palette.css`, раздел «гаммы отдельных страниц»). Есть: `olive` — тёмно-оливковая гамма старого сайта (фон `#666656`, светло-жёлтый текст, жёлтые ссылки), у оглавления раздела из приватного слоя (2026-10-15). Новая гамма — новый блок `body.palette-<имя>` в `palette.css`.

## Другие проекты — `content/Disks/other.md` (`other-projects`)

Сами издания берутся из коллекции `releases` в Directus (см. [docs/directus.md](directus.md)).

- `params.epigraph` (HTML) — эпиграф в начале страницы.
- `params.sections` (список `{id, kind, title}`) — разделы страницы по порядку: `id` — якорь, `kind` — какой `releases.kind` показывает раздел (`cover`, `reissue`, `participation`), `title` — заголовок.
- `params.credits` (HTML) — примечание об источниках внизу страницы.

## Переводы и языковые разделы — `content/<язык>/` (`en`, `de`, `eo`, `he`, `uk`, `fr`)

Страницы переводов:

- Один файл на перевод, `content/<язык>/<id>.md`; имя файла — `translations.id` в Directus. `type` и `layout` (`translation`) задаёт правило `cascade`. Заголовок, оригинал, переводчик, год и исполнения берутся из Directus (`translations`, `translators`, `works`, `recordings`). Тело — текст перевода, читается как есть, как текст песни.
- `params.htmlComment` — HTML-комментарий со старой страницы (благодарности, копирайт), выводится комментарием в коде страницы.

Страницы языкового раздела; каждая задаёт свой `layout`:

- `<язык>-index.md` (`language-index`) — главная страница раздела и настройки всего раздела, остальные страницы читают их через `site.GetPage`:
  - `params.lang` — код языка;
  - `params.heading` — самоназвание языка: `<h1>` и шаг «хлебных крошек»;
  - `params.nav` (список `{label, href}`) — верхнее меню раздела на этом языке. Первые три пункта — ещё и шаги крошек: русская главная, главная языка, список переводов. Пункт с пустым `href` — неактивная ячейка (страницы ещё нет);
  - `params.labels` (словарь) — строки интерфейса на этом языке: названия меню и крошек (`menu`, `breadcrumbs`, `language`, `translations`, `top`, `page`), подписи страницы перевода (`original`, `translatedBy`, `showOriginal`, `hideOriginal`, `performances`, `recordedIn`, `inRussian`), переключатели вида (`text`, `chords`, `above`, `side`, `source`, `transpose`, `stress`), заголовок списка и кнопки сортировки (`translationsTitle`, `sortTranslation`, `sortOriginal`, `sortTranslator`, `sortSongYear`; необязательные `sortAscending`, `sortDescending` — подсказка у активной кнопки сортировки, по умолчанию по-английски);
  - `params.sortable` (bool) — кнопки сортировки в списке переводов;
  - новый язык может начаться с одной этой страницы настроек, с `"build": {"render": "never", "list": "never"}` и пустыми `href` в `nav`, пока у главной страницы нет текста; потом `build` убирается и `href` заполняются (так было у `eo` и `he` до 2026-10-09).
- `<язык>-translations.md` (`language-translations`) — список переводов: `params.lang`.
- Статья раздела (`language-article`, `fr/ostromoukhov-2000.md`): `params.lang`, `params.crumb` (последний шаг крошек, по умолчанию `title`). `params.description` — **не используется**.

## Картинки — `content/Images/*.md` (`images-page`)

- `params.subtitle`, `params.bgColor`.
- `params.centerText` (bool) — текст по центру (для страниц, которые на старом сайте были выровнены по центру).
- `params.parentUrl`, `params.parentTitle` — дополнительная ссылка «вверх» в угловой навигации (подпись по умолчанию — «Выше»).

## Архив — `content/Archive/*.md` (`archive-page`)

- `params.isIndex` (bool) — главная страница архива: в угловой навигации нет ссылки «Архив» на саму себя.
- `params.lang` — язык страницы, если не русский (`america97`: `"en"`).
- `params.subtitle`.

## Страницы-редиректы — `redirect`, `redirect-hub`

Маленькие страницы, которые сохраняют адреса старого сайта (`content/Images/redirects/`, `content/redirects/`, `content/Tapes/tapes-index.md` и др.). Обычно с `"sitemap": {"disable": true}`.

- `params.target` (`redirect`) — куда вести; **относительный** адрес (`"photos2000-2004.html#agolyanov"`, `"../Disks/index.html#tapes"`), чтобы страница пережила перенос сайта в другую папку или на другой домен без пересборки.
- `params.map`, `params.default` (`redirect-hub`) — для старой страницы с несколькими якорями: `map` — старый якорь → новый адрес, `default` — куда вести без якоря.
- `params.noindex` (bool) — добавить `noindex` странице-редиректу.
