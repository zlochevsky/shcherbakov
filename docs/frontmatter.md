# Content front matter reference

Reference for the front matter fields (JSON block at the top of `content/**/*.md` files) actually read by the Hugo templates in `layouts/`. Compiled by grepping `layouts/` for `.Params.*` / `.Param "..."` usages and cross-checking against real content files (2026-08-21). Where a field exists in content but no template reads it, it is marked **unused**.

Not covered here: the Directus-backed collections (events/works/perfs/announces/…) — see [docs/directus.md](directus.md). Also not covered: `hugo.json`'s own `menu` entries, which carry their own `params` (`isDateToPrint`, `dynamicLastmod`) — these look identical in template code (`.Params.isDateToPrint`) but belong to the menu config in `hugo.json`, not to any content `.md` file's front matter; don't confuse the two.

## Standard Hugo fields (not custom)

These are native Hugo front matter keys, not project-specific — see the [Hugo front matter docs](https://gohugo.io/content-management/front-matter/) for full semantics.

- `title` — page `<h1>`/`<title>` fallback text.
- `date`, `lastmod` — creation/modification dates; `lastmod` also drives the "updated" badge in the menu (see `params.isDateToPrint` note above — that's a menu-config concern, not this field).
- `draft` — excludes the page from the build when `true`.
- `type`, `layout` — select which template in `layouts/` renders the page (this project's content almost always uses `"type": "miscellaneous"` plus an explicit `"layout"` naming the template file, e.g. `"layout": "songpage"`).
- `publishDate`, `expiryDate` — Hugo's built-in scheduling: page is excluded from the build outside this window. Used in the `archetypes/announces.md` scaffold; note actual concert announces are Directus-driven now (see docs/directus.md), so this archetype is vestigial.
- `url` — overrides the page's output path. Used on `content/Disks/*.md` (e.g. `"url": "/Disks/minsk3.html"`).
- `"sitemap": {"disable": true}` — removes the page from `sitemap.xml`. Used for archived song-edition pages (see docs/directus.md, "Редакции песен").

## Site chrome overrides (most page types)

- `params.subtitle` (string) — per-page `<h2>` subtitle, rendered right under `<h1>` (e.g. `catalogue.html:21`, `concerts.html:21`). Distinct from the *site-wide* subtitle (`site.Params.Subtitle`, set once in `hugo.json`) — this one is per page and currently empty on most pages.
- `params.name` (string) — overrides the browser-tab `<title>` text independently of the visible `.Title`/`<h1>` (`head.html:4`, `headbasic.html:4`, and duplicated inline in `catalogue.html`/`concerts.html`). Falls back to `.Title` when empty. Currently set but empty on `catalogue.md`/`concerts.md`/etc., so has no visible effect yet.

## Homepage announce banner — `content/news.md` only

Actual concert announces are Directus-driven now. The section is vestigial.

Read from both `news.html` (the news page itself) and `header.html` (the homepage banner), both via `site.GetPage "news"` — i.e. these fields live **only** in `content/news.md`, not per-page.

- `params.showAnnounce` (bool) — master switch: show the announce banner (homepage header) / announce block (news page) at all.
- `params.announceTitle` (string) — heading text shown above the announce list, if `showAnnounce` is on.
- `params.announce` (array of markdown strings) — **legacy** hand-written announce lines, still merged in alongside the Directus-driven announces by `announces.html`. Currently empty (`[]`) — live announces now come from Directus's `announces` collection.
- `params.showAnnounceTitle`, `params.showAnnounceOnHome` — present in `content/news.md` but **unused**: no template reads either. Don't rely on them; if you want to gate the title or the homepage banner separately, that logic needs to be added first.

## Song text pages — `content/texts/<year>/<id>.md`

Since 2026-10-01 a song page is **one file: minimal JSON front matter + the song text as the body** (the former `assets/texts/<id>.txt` files were merged in and deleted). `type`/`layout` come from the `cascade` rule in `hugo.json`; the **file name is the song id** (`works.id` in Directus), the folder is the year of the current edition (`works.edit`, else `works.date`). The body is read raw (`.RawContent`, never rendered as Markdown) and starts right with the song — the heading line is not part of the text: `<h1>`, `<title>` and `<meta name="description">` come from Directus (`song-page-info.html`, `song-meta.html`): `<h1>` = `fname` or `name` capitalised, or «* * *» with the `fincipit` hidden for screen readers; `<title>` = the same or `fincipit`; description = `incipit`. Visibility: `noindex` and exclusion from `sitemap.xml` (own `layouts/sitemap.xml`) = `works.noindex` or an early edition; the song catalogue = `works.hidden`.

- `params.tonality` (string, e.g. `"Hm"`) — chord transposition base key. If omitted, `song.html` tries to auto-detect it by regex-matching chord tokens in the text — an explicit value is more reliable.
- `params.chordsStartAt` (int, 1-based column) — column where chords begin, used to split each line into lyrics/chords for the "above"/"side" views. Optional: if omitted, there is no chord column (poems).
- `params.textFinishAtLine` (int, 0-based line index of the body) — lines from this one onward are not "main lyrics" and go verbatim into a trailing `<pre>` block (tablature, notes). Optional: defaults to the last line.
- `params.editionOf` (string, id of the current edition) — marks the page as an early edition: noindex, not in the sitemap, title and year taken from the current edition, banner link to it.
- `title` (top level, optional) — overrides the title from Directus; only for an early edition that had a different name (`pazh0`); `"* * *"` = untitled early edition (`japomnju`): `<title>` and description then come from the first line of the page's own text.
- `aliases` (top level) — old URLs of a renamed page (redirect pages).

## Disc pages — `content/Disks/*.md` (`"layout": "diskpage"`)

- `params.id` (string) — must match a `sets.id` in Directus (the album/collection record); used to fetch the set's title/track list via `directus-sets.html` (`diskpage.html:21-23`).
- `params.image` (string, filename only) — cover image, resolved as `Images/<value>` (`disks-index.html:54`; also used directly as `Images/bkp/<id>.jpg`-style paths elsewhere for consistency — check the specific layout).
- `params.year` (string, may be a range like `"2000-2007"`) — display-only text on the disc listing.
- `params.concert` (bool) — present on at least one disc (`minsk3.md`) but **unused**: no template reads it yet. Looks like a forward-looking flag ("this disc documents a specific concert") that was never wired up.

## Book pages — `content/Books/*.md` (`"layout": "bookpage"`)

- `params.id` (string) — must match a Directus `books` collection id; also reused directly as the cover image filename, `Images/bkp/<id>.jpg` (`bookpage.html:79`).
- `params.buyUrl` (string, URL) — external purchase link, rendered as a button/link if present (`bookpage.html:107`).

---

# Справочник параметров front matter в контенте

Справочник по полям front matter (JSON-блок в начале `content/**/*.md`), которые реально читаются шаблонами в `layouts/`. Составлен через grep по `.Params.*`/`.Param "..."` в `layouts/` со сверкой по реальным content-файлам (2026-08-21). Если поле есть в контенте, но ни один шаблон его не читает — помечено как **не используется**.

Не входит сюда: коллекции, живущие в Directus (events/works/perfs/announces/…) — см. [docs/directus.md](directus.md). Также не входит: параметры пунктов меню в `hugo.json` (`isDateToPrint`, `dynamicLastmod`) — в шаблонах выглядят один в один как поля front matter (`.Params.isDateToPrint`), но на самом деле относятся к конфигу меню в `hugo.json`, а не к front matter какого-либо `.md`-файла, поэтому не смешиваем эти два источника.

## Стандартные поля Hugo (не специфичны для проекта)

Встроенные ключи front matter самого Hugo, не придуманные в этом проекте — полная семантика в [документации Hugo](https://gohugo.io/content-management/front-matter/).

- `title` — текст `<h1>` / запасной `<title>` страницы.
- `date`, `lastmod` — даты создания/изменения; `lastmod` также участвует в бейдже «обновлено» в меню (см. заметку про `params.isDateToPrint` выше — это уже про конфиг меню, не про это поле).
- `draft` — при `true` страница исключается из сборки.
- `type`, `layout` — выбирают, каким шаблоном из `layouts/` рендерится страница (в этом проекте контент почти всегда использует `"type": "miscellaneous"` плюс явный `"layout"` с именем файла шаблона, напр. `"layout": "songpage"`).
- `publishDate`, `expiryDate` — встроенный в Hugo механизм расписания: вне этого окна страница исключается из сборки. Используется в заготовке `archetypes/announces.md`, но, поскольку реальные анонсы концертов сейчас ведутся через Directus (см. docs/directus.md), этот архетип, видимо, уже рудимент.
- `url` — переопределяет итоговый путь страницы. Используется в `content/Disks/*.md` (напр. `"url": "/Disks/minsk3.html"`).
- `"sitemap": {"disable": true}` — убирает страницу из `sitemap.xml`. Используется для архивных редакций песен (см. docs/directus.md, «Редакции песен»).

## Переопределения общего оформления (большинство типов страниц)

- `params.subtitle` (строка) — подзаголовок `<h2>` конкретной страницы, сразу под `<h1>` (напр. `catalogue.html:21`, `concerts.html:21`). Не путать с *сайтовым* подзаголовком (`site.Params.Subtitle`, задаётся один раз в `hugo.json`) — этот же — постраничный, сейчас на большинстве страниц пустой.
- `params.name` (строка) — переопределяет текст вкладки браузера (`<title>`) независимо от видимого `.Title`/`<h1>` (`head.html:4`, `headbasic.html:4`, и продублировано инлайн в `catalogue.html`/`concerts.html`). При пустом значении используется `.Title`. Сейчас на `catalogue.md`/`concerts.md` и т.п. поле объявлено, но пустое — видимого эффекта пока нет.

## Баннер анонсов на главной — только `content/news.md`

Поскольку реальные анонсы концертов сейчас ведутся через Directus (см. docs/directus.md), эта секция, видимо, уже рудимент.

Баннер аннонса читался и из `news.html` (сама страница новостей), и из `header.html` (баннер на главной) — в обоих случаях через `site.GetPage "news"`, то есть эти поля жили **только** в `content/news.md`, не на других страницах.

- `params.showAnnounce` (bool) — общий переключатель: показывать ли баннер анонса (шапка главной) / блок анонса (страница новостей) вообще.
- `params.announceTitle` (строка) — заголовок над списком анонсов, если `showAnnounce` включён.
- `params.announce` (массив markdown-строк) — старые вручную написанные строки анонса, всё ещё подмешиваются `announces.html` вместе с анонсами из Directus. Сейчас пустой (`[]`) — живые анонсы теперь берутся из коллекции `announces` в Directus.
- `params.showAnnounceTitle`, `params.showAnnounceOnHome` — присутствуют в `content/news.md`, но **не используются**: ни один шаблон их не читает. Не полагайтесь на них; если нужно управлять заголовком или баннером на главной по отдельности — эту логику сперва придётся дописать.

## Страницы текстов песен — `content/texts/<год>/<id>.md`

С 2026-10-01 страница песни — **один файл: минимальный JSON front matter + текст песни телом файла** (прежние `assets/texts/<id>.txt` слиты в `.md` и удалены). `type`/`layout` задаёт правило `cascade` в `hugo.json`; **имя файла — id песни** (`works.id` в Directus), папка — год актуальной редакции (`works.edit`, иначе `works.date`). Тело читается как есть (`.RawContent`, Markdown не применяется) и начинается сразу с песни — строки-заголовка в тексте нет: `<h1>`, `<title>` и `<meta name="description">` берутся из Directus (`song-page-info.html`, `song-meta.html`): `<h1>` — `fname` или `name` с заглавной буквы, иначе «* * *» с невидимым `fincipit` для экранного доступа; `<title>` — то же или `fincipit`; description — `incipit`. Видимость: `noindex` и исключение из `sitemap.xml` (свой шаблон `layouts/sitemap.xml`) — `works.noindex` или ранняя редакция; каталог песен — `works.hidden`.

- `params.tonality` (строка, напр. `"Hm"`) — базовая тональность для транспонирования. Если не задано, `song.html` пытается определить её по аккордам в тексте — явное значение надёжнее.
- `params.chordsStartAt` (int, столбец с 1) — столбец, с которого начинаются аккорды; по нему строки делятся на текст и аккорды в видах «над строкой»/«справа». Необязательно: без него колонки аккордов нет (стихи).
- `params.textFinishAtLine` (int, индекс строки тела с 0) — строки начиная с этой — не «основной» текст и выводятся как есть в блоке `<pre>` (табулатуры, примечания). Необязательно: по умолчанию — последняя строка.
- `params.editionOf` (строка, id актуальной редакции) — страница ранней редакции: noindex, не в sitemap, заголовок и год — от актуальной редакции, плашка-ссылка на неё.
- `title` (в корне, необязательно) — заменяет заголовок из Directus; только для ранней редакции с другим названием (`pazh0`); `"* * *"` — ранняя редакция без названия (`japomnju`): `<title>` и description тогда берутся из первой строки собственного текста страницы.
- `aliases` (в корне) — старые адреса переименованной страницы (страницы-редиректы).

## Страницы дисков — `content/Disks/*.md` (`"layout": "diskpage"`)

- `params.id` (строка) — должен совпадать с `sets.id` в Directus (запись альбома/коллекции); используется для получения названия и списка треков через `directus-sets.html` (`diskpage.html:21-23`).
- `params.image` (строка, только имя файла) — обложка, путь собирается как `Images/<значение>` (`disks-index.html:54`; в других местах имя файла используется и напрямую в путях вида `Images/bkp/<id>.jpg` — сверяйтесь с конкретным шаблоном).
- `params.year` (строка, может быть диапазоном вроде `"2000-2007"`) — чисто отображаемый текст в списке дисков.
- `params.concert` (bool) — встречается как минимум в одном диске (`minsk3.md`), но **не используется**: ни один шаблон пока его не читает. Похоже на задел на будущее («этот диск документирует конкретный концерт»), который так и не подключили.

## Страницы книг — `content/Books/*.md` (`"layout": "bookpage"`)

- `params.id` (строка) — должен совпадать с id в коллекции `books` в Directus; также напрямую используется как имя файла обложки, `Images/bkp/<id>.jpg` (`bookpage.html:79`).
- `params.buyUrl` (строка, URL) — внешняя ссылка «купить», рендерится как кнопка/ссылка, если задана (`bookpage.html:107`).
