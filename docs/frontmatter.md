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

## Song text pages — `content/texts/**/*.md` (`"layout": "songpage"`)

- `params.id` (string) — must match the `works.id` in Directus; used to load `assets/texts/<id>.txt` (`song.html:1`) and to look up `works.is_poem` (`directus-work.html`, added for the poem-mode feature).
- `params.tonality` (string, e.g. `"Hm"`) — chord transposition base key. If omitted, `song.html` tries to auto-detect it by regex-matching chord tokens in the source text (`song.html:14-18`) — an explicit value is more reliable.
- `params.year` (string) — used only to build the "outdated edition" banner link (`printf "texts/%s/%s.html" .year .id`, `songpage.html`), for redirecting from an old archived edition to the current one. Unrelated to sorting/display of the work's actual date, which comes from Directus `works.date`.
- `params.chordsStartAt` (int, 1-based column) — column in the source `.txt` where chords begin, used to split each line into lyrics/chords for the "above"/"side" chord views (`song.html:31`). **Optional as of 2026-08-21**: if omitted, treated as `0` (no chord column at all — every line is plain text). Appropriate for poems (`works.is_poem = true`), which have no chords.
- `params.textFinishAtLine` (int, 0-based line index) — the source file's last line that's still "main lyrics"; everything from this line onward, plus this line if it's *only* used as a cutoff, is instead dumped verbatim into a trailing `<pre>` block appended after the "side"/"above" views (extra notes, alternate verses, etc. — see `song.html:57-146`). **Optional as of 2026-08-21**: if omitted, defaults to the last line of the file, i.e. the whole file is treated as main lyrics. Before this default was added, omitting the field made the "text" view render completely empty (see the 2026-08-21 fix in `song.html`) — always prefer omitting it over guessing a wrong value.
- `params.newerEdition` (object `{"year": ..., "id": ...}`) — marks this page as an archived/superseded text edition; `songpage.html` adds a `<meta name="robots" content="noindex, follow">` tag and a `.notice` banner linking to `texts/<year>/<id>.html` (the current edition). Pair with top-level `"sitemap": {"disable": true}` — see docs/directus.md, "Редакции песен".

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

## Страницы текстов песен — `content/texts/**/*.md` (`"layout": "songpage"`)

- `params.id` (строка) — должен совпадать с `works.id` в Directus; используется для загрузки `assets/texts/<id>.txt` (`song.html:1`) и для запроса `works.
- `is_poem` (`directus-work.html`, добавлен для режима «стихотворение»).
- `params.tonality` (строка, напр. `"Hm"`) — базовая тональность для транспонирования аккордов. Если не задано, `song.html` пытается определить её сам по регэкспу над текстом аккордов (`song.html:14-18`) — явное значение гораздо надёжнее.
- `params.year` (строка) — используется только для ссылки в баннере «устаревшая редакция» (`printf "texts/%s/%s.html" .year .id`, `songpage.html`), для перехода со старой архивной редакции на актуальную. С сортировкой/отображением реальной даты произведения не связано — та берётся из `works.date` в Directus.
- `params.chordsStartAt` (int, столбец, нумерация с 1) — столбец в исходном `.txt`, с которого начинаются аккорды; используется, чтобы разбить каждую строку на текст/аккорды для видов «над строкой»/«справа» (`song.html:31`). **Необязателен с 2026-08-21**: если не задан, считается равным `0` (столбца аккордов нет вовсе — вся строка это текст). Подходит для стихов (`works.is_poem = true`), где аккордов нет вовсе.
- `params.textFinishAtLine` (int, индекс строки с 0) — последняя строка исходника, которая ещё относится к «основному» тексту; всё начиная с неё уходит не в обычную обработку, а целиком в хвостовой блок `<pre>`, добавляемый после видов «сбоку»/«над строкой» (доп. примечания, альтернативные куплеты и т.п. — см. `song.html:57-146`). **Необязателен с 2026-08-21**: если не задан, по умолчанию берётся последняя строка файла, т.е. весь файл считается основным текстом. Лучше вообще не указывать поле, чем угадывать неверное значение.
- `params.newerEdition` (объект `{"year": ..., "id": ...}`) — помечает страницу как архивную/замененную редакцию текста; `songpage.html` добавляет `<meta name="robots" content="noindex, follow">` и баннер `.notice` со ссылкой на `texts/<year>/<id>.html` (актуальную редакцию). Используйте в паре с `"sitemap": {"disable": true}` в корне front matter — см. docs/directus.md, «Редакции песен».

## Страницы дисков — `content/Disks/*.md` (`"layout": "diskpage"`)

- `params.id` (строка) — должен совпадать с `sets.id` в Directus (запись альбома/коллекции); используется для получения названия и списка треков через `directus-sets.html` (`diskpage.html:21-23`).
- `params.image` (строка, только имя файла) — обложка, путь собирается как `Images/<значение>` (`disks-index.html:54`; в других местах имя файла используется и напрямую в путях вида `Images/bkp/<id>.jpg` — сверяйтесь с конкретным шаблоном).
- `params.year` (строка, может быть диапазоном вроде `"2000-2007"`) — чисто отображаемый текст в списке дисков.
- `params.concert` (bool) — встречается как минимум в одном диске (`minsk3.md`), но **не используется**: ни один шаблон пока его не читает. Похоже на задел на будущее («этот диск документирует конкретный концерт»), который так и не подключили.

## Страницы книг — `content/Books/*.md` (`"layout": "bookpage"`)

- `params.id` (строка) — должен совпадать с id в коллекции `books` в Directus; также напрямую используется как имя файла обложки, `Images/bkp/<id>.jpg` (`bookpage.html:79`).
- `params.buyUrl` (строка, URL) — внешняя ссылка «купить», рендерится как кнопка/ссылка, если задана (`bookpage.html:107`).
