# Content front matter reference

Front matter fields (the JSON block at the top of `content/**/*.md`) that the templates in `layouts/` actually read. Checked against `layouts/` and all content files on 2026-10-02; sections for translations, language pages and `Disks/other.md` added on 2026-10-07. Fields present in content but read by no template are marked **unused**.

Not covered: the Directus collections (works, events, perfs, sets, books, comments, announces…) — see [docs/directus.md](directus.md); and the `params` of menu entries in `hugo.json` (`isDateToPrint`, `dynamicLastmod`, `collapsible`, `toggleChild`, `mobileOnly`, `shortName`, `dropdown`, `lang`) — they look like `.Params.*` in templates but belong to the menu config, not to any `.md` file.

## Standard Hugo fields

See the [Hugo front matter docs](https://gohugo.io/content-management/front-matter/).

- `title` — page `<h1>` and fallback `<title>`.
- `type`, `layout` — choose the template. Content uses `"type": "miscellaneous"` plus an explicit `"layout"` (template file name in `layouts/miscellaneous/`); song pages (`songpage`) and the pages of the language folders (`translation`) get both from the `cascade` rules in `hugo.json`, so a language page that is not a translation sets its own `layout`.
- `url` — the page's output path; set on almost every page to keep the legacy site's addresses (`"/Disks/minsk3.html"`).
- `aliases` — old addresses that should redirect to this page.
- `date`, `lastmod` — dates; `lastmod` feeds the "updated" date shown next to some menu items.
- `"sitemap": {"disable": true}` — keep the page out of `sitemap.xml` (redirect pages, `fans/kom2`). Song pages are handled by their own rules, see below.
- `"build": {"render": "never", "list": "never"}` — a page that is not rendered on its own, only included by another template (`Books/other-publications.md`, shown on the Books page) or read for its settings (`eo/eo-index.md`, `he/he-index.md`: language sections without a main page yet).
- `draft`, `publishDate`, `expiryDate` — not used in content now (the hand-written `content/announces/` and its archetype were removed 2026-10-02: announces come from Directus).

## Site chrome (most page types)

- `params.subtitle` — per-page `<h2>` under `<h1>`. Not the site-wide `site.Params.Subtitle` from `hugo.json`.
- `params.name` — browser-tab `<title>` independent of `<h1>`; falls back to `title`.

## Announces — `content/news.md` only

Read by `header.html` (home page) and `news.html` through `site.GetPage "news"`. The announces themselves come from the Directus `announces` collection (`partials/announces.html`).

- `params.showAnnounce` (bool) — show the announce list at all (home page header and news page).
- `params.announceTitle` — heading above the list on the news page.
- `params.announce` (array of Markdown strings) — legacy hand-written lines, appended after the Directus announces. Empty now.
- `params.showAnnounceTitle`, `params.showAnnounceOnHome` — **unused**.

## Song pages — `content/texts/<year>/<id>.md`

One file per song: minimal front matter, the song text as the body (read raw with `.RawContent`, not as Markdown; blank lines before the text are skipped, so a blank line after the front matter, as the in-browser editor writes it, changes nothing). The file name is the song id (`works.id`), the folder is the year of the current edition. `<h1>`, `<title>`, description and visibility come from Directus (`works.fname`/`name`/`fincipit`/`incipit`, `works.noindex`, `works.hidden`), see [docs/directus.md](directus.md).

- `params.tonality` (e.g. `"Hm"`) — base key for transposition. If empty, `song.html` guesses it from the chords; an explicit value is more reliable.
- `params.chordsStartAt` (int, 1-based column) — where chords begin; splits lines into lyrics and chords. Omit for poems without chords.
- `params.textFinishAtLine` (int, 0-based line of the body) — lines from here on are not lyrics and go verbatim into a `<pre>` block (tablature, notes). Default: the last line. Equivalently, it is the 1-based number of the last lyrics line, the number the editor's badge shows on that line.
- `params.editionOf` — id of the current edition; marks an early edition: noindex, not in the sitemap, title and year from the current edition, banner linking to it.
- `title` (top level, optional) — only for an early edition with a different name (`pazh0`); `"* * *"` = untitled early edition (`japomnju`), `<title>` and description then come from its first line.
- `aliases` — old addresses of a renamed page.

## Albums and cassettes — `content/Disks/*.md` (`diskpage`), `content/Tapes/*.md` (`tapepage`)

- `params.id` — `sets.id` in Directus; title, year, format, images and track list all come from the set.
- `params.year`, `params.image`, `params.images` — fallbacks used only when the set has no `year` / `album_img` / `extra_images`; no page sets them now.
- Full-size image versions are not front matter: see «Полноразмерные изображения» under `sets` in [docs/directus.md](directus.md).

## Books — `content/Books/*.md` (`bookpage`)

- `params.id` — `books.id` in Directus. Cover: `books.photo`, else `Images/bkp/<id>.jpg`.
- `params.buyUrl` — purchase link, shown as a button if set.

## Song cycles — `content/Cycles/*.md` (`cycle`)

- `params.id` — cycle id in Directus (`cycles`).

## Articles, fan club, parodies — `praises-article` (Praises, FOM, fans, Parodies, SCH2, …)

- `title`, `params.subtitle`, `params.author` — heading block.
- `params.backUrl`, `params.backTitle` — the "back" link in the corner navigation. Without them a page under `content/fans/` gets «Фан-клуб → fans/index.html»; other sections set them explicitly.
- `params.bgColor` — page background (the fan club hub `fans/fans-index.md`).

## Other projects — `content/Disks/other.md` (`other-projects`)

The releases themselves come from the Directus `releases` collection (see [docs/directus.md](directus.md)).

- `params.epigraph` (HTML) — the epigraph at the top of the page.
- `params.sections` (list of `{id, kind, title}`) — the page sections in order: `id` is the anchor, `kind` is the `releases.kind` the section shows (`cover`, `reissue`, `participation`), `title` is the heading.
- `params.credits` (HTML) — the note on sources at the bottom.

## Translations and language sections — `content/<language>/` (`en`, `de`, `eo`, `he`, `uk`, `fr`)

Translation pages:

- One file per translation, `content/<language>/<id>.md`; the file name is `translations.id` in Directus. `type` and `layout` (`translation`) come from the `cascade` rule. The title, the original, the translator, the year and recordings come from Directus (`translations`, `translators`, `works`, `recordings`). The body is the translation text, read raw like a song text.
- `params.htmlComment` — an HTML comment kept from the legacy page (credits, copyright), output as a comment in the page source.

Language section pages; each sets its own `layout`:

- `<language>-index.md` (`language-index`) — the main page of the section and the settings of the whole section, read by the other pages through `site.GetPage`:
  - `params.lang` — the language code;
  - `params.heading` — the language's own name: the `<h1>` and the breadcrumb;
  - `params.nav` (list of `{label, href}`) — the top menu of the section, in that language. The first three entries are also the breadcrumb steps: the Russian home page, the main page of the language, the list of translations. An entry with an empty `href` is an inactive cell (no page yet);
  - `params.labels` (dictionary) — interface strings in that language: the menu and breadcrumb names (`menu`, `breadcrumbs`, `language`, `translations`, `top`, `page`), translation page labels (`original`, `translatedBy`, `showOriginal`, `hideOriginal`, `performances`, `recordedIn`, `inRussian`), the view switches (`text`, `chords`, `above`, `side`, `source`, `transpose`, `stress`), the list headings and sort buttons (`translationsTitle`, `sortTranslation`, `sortOriginal`, `sortTranslator`, `sortSongYear`);
  - `params.sortable` (bool) — sort buttons on the list of translations;
  - `eo` and `he` have only this settings page so far, with `"build": {"render": "never", "list": "never"}`.
- `<language>-translations.md` (`language-translations`) — the list of translations: `params.lang`.
- An article of the section (`language-article`, `fr/ostromoukhov-2000.md`): `params.lang`, `params.crumb` (the last breadcrumb, `title` by default). `params.description` — **unused**.

## Pictures — `content/Images/*.md` (`images-page`)

- `params.subtitle`, `params.bgColor`.
- `params.centerText` (bool) — centre the text (for pages that were centred on the legacy site).
- `params.parentUrl`, `params.parentTitle` — an extra "up" link in the corner navigation (default title «Выше»).

## Archive — `content/Archive/*.md` (`archive-page`)

- `params.isIndex` (bool) — the archive hub page: no «Архив» link to itself in the corner navigation.
- `params.lang` — page language when not Russian (`america97`: `"en"`).
- `params.subtitle`.

## Redirect pages — `redirect`, `redirect-hub`

Small pages that keep legacy addresses alive (`content/Images/redirects/`, `content/redirects/`, `content/Tapes/tapes-index.md`, …). Usually with `"sitemap": {"disable": true}`.

- `params.target` (`redirect`) — where to go; a **relative** address (`"photos2000-2004.html#agolyanov"`, `"../Disks/index.html#tapes"`) so the page survives a move of the site to another folder or domain without a rebuild.
- `params.map`, `params.default` (`redirect-hub`) — for a legacy page that had several anchors: `map` = old anchor → new address, `default` = where to go without an anchor.
- `params.noindex` (bool) — add `noindex` to the redirect page.

---

# Справочник параметров front matter

Поля front matter (JSON-блок в начале `content/**/*.md`), которые реально читают шаблоны из `layouts/`. Сверено с `layouts/` и всеми файлами контента 2026-10-02; разделы о переводах, языковых страницах и `Disks/other.md` добавлены 2026-10-07. Поля, которые есть в контенте, но не читаются ни одним шаблоном, помечены **не используется**.

Не входит: коллекции Directus (works, events, perfs, sets, books, comments, announces…) — см. [docs/directus.md](directus.md); `params` пунктов меню в `hugo.json` (`isDateToPrint`, `dynamicLastmod`, `collapsible`, `toggleChild`, `mobileOnly`, `shortName`, `dropdown`, `lang`) — в шаблонах они выглядят как `.Params.*`, но относятся к настройкам меню, а не к файлам `.md`.

## Стандартные поля Hugo

См. [документацию Hugo](https://gohugo.io/content-management/front-matter/).

- `title` — `<h1>` и запасной `<title>` страницы.
- `type`, `layout` — выбор шаблона. В контенте — `"type": "miscellaneous"` и явный `"layout"` (имя файла шаблона в `layouts/miscellaneous/`); страницам песен (`songpage`) и страницам языковых папок (`translation`) оба задают правила `cascade` в `hugo.json`, поэтому языковая страница, которая не перевод, задаёт свой `layout` сама.
- `url` — адрес страницы; стоит почти у всех страниц, чтобы сохранить адреса старого сайта (`"/Disks/minsk3.html"`).
- `aliases` — старые адреса, которые должны вести на эту страницу.
- `date`, `lastmod` — даты; `lastmod` даёт дату «обновлено» у некоторых пунктов меню.
- `"sitemap": {"disable": true}` — не включать страницу в `sitemap.xml` (страницы-редиректы, `fans/kom2`). Для страниц песен — свои правила, см. ниже.
- `"build": {"render": "never", "list": "never"}` — страница не выводится сама: её вставляет другой шаблон (`Books/other-publications.md` на странице «Книги») или из неё читают настройки (`eo/eo-index.md`, `he/he-index.md` — разделы языков, у которых пока нет главной страницы).
- `draft`, `publishDate`, `expiryDate` — сейчас в контенте не используются (ручные `content/announces/` и их заготовка удалены 2026-10-02: анонсы берутся из Directus).

## Общее оформление (большинство страниц)

- `params.subtitle` — подзаголовок `<h2>` под `<h1>`. Не путать с общим `site.Params.Subtitle` из `hugo.json`.
- `params.name` — текст вкладки браузера (`<title>`) независимо от `<h1>`; по умолчанию — `title`.

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
  - `params.labels` (словарь) — строки интерфейса на этом языке: названия меню и крошек (`menu`, `breadcrumbs`, `language`, `translations`, `top`, `page`), подписи страницы перевода (`original`, `translatedBy`, `showOriginal`, `hideOriginal`, `performances`, `recordedIn`, `inRussian`), переключатели вида (`text`, `chords`, `above`, `side`, `source`, `transpose`, `stress`), заголовок списка и кнопки сортировки (`translationsTitle`, `sortTranslation`, `sortOriginal`, `sortTranslator`, `sortSongYear`);
  - `params.sortable` (bool) — кнопки сортировки в списке переводов;
  - у `eo` и `he` пока есть только эта страница настроек, с `"build": {"render": "never", "list": "never"}`.
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
