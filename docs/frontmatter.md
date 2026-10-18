[Русская версия](frontmatter.ru.md)

# Content front matter reference

Front matter fields (the JSON block at the top of `content/**/*.md`) that the templates in `layouts/` actually read. Checked against `layouts/` and all content files on 2026-10-02, rechecked on 2026-10-18; sections for translations, language pages and `Disks/other.md` added on 2026-10-07. Fields present in content but read by no template are marked **unused**.

Not covered: the Directus collections (works, events, perfs, sets, books, comments, announces…) — see [docs/directus.md](directus.md); and the `params` of menu entries in `config/_default/menus.json` (`isDateToPrint`, `dynamicLastmod`, `collapsible`, `toggleChild`, `mobileOnly`, `shortName`, `icon`, `dropdown`, `lang`; see the «Menus» section of the README) — they look like `.Params.*` in templates but belong to the menu config, not to any `.md` file.

## Standard Hugo fields

See the [Hugo front matter docs](https://gohugo.io/content-management/front-matter/).

- `title` — page `<h1>` and fallback `<title>`.
- `type`, `layout` — choose the template. Content uses `"type": "miscellaneous"` plus an explicit `"layout"` (template file name in `layouts/miscellaneous/`); song pages (`songpage`) and the pages of the language folders (`translation`) get both from the `cascade` rules in `hugo.json`, so a language page that is not a translation sets its own `layout`.
- `url` — the page's output path; set on almost every page to keep the legacy site's addresses (`"/Disks/minsk3.html"`).
- `aliases` — old addresses that should redirect to this page.
- `date`, `lastmod` — dates; `lastmod` feeds the "updated" date shown next to some menu items.
- `"sitemap": {"disable": true}` — keep the page out of `sitemap.xml` (redirect pages, `fans/kom2`). Song pages are handled by their own rules, see below.
- `"build": {"render": "never", "list": "never"}` — a page that is not rendered on its own, only included by another template (`Books/other-publications.md`, shown on the Books page; `_footer.md`, the home page footer) or read for its settings only (a language section whose main page has no text yet; on 2026-10-09 there is none: all six languages have a main page).
- `draft`, `publishDate`, `expiryDate` — not used in content now (the hand-written `content/announces/` and its archetype were removed 2026-10-02: announces come from Directus).

## Site chrome (most page types)

- `params.subtitle` — per-page `<h2>` under `<h1>`. Not the site-wide `site.Params.Subtitle` from `hugo.json`.
- `params.name` — short page name independent of `<h1>`: the base of the default `<title>` (`seo.html`; menus do not read it); falls back to `title`.
- `params.lang` — page language when not Russian: on any page it sets `og:locale` (`seo.html`); in the archive and language sections also the page's `lang`, see below.

## Search engines and link previews — all pages except redirects

`<title>`, description, `noindex`, canonical and Open Graph come from one partial, `layouts/partials/seo.html` (added 2026-10-13).

- `description` (standard Hugo field) — `<meta name="description">` and `og:description`. Set on the main static pages; songs, translations, albums, cassettes, books and cycles get a generated one when it is empty; all `praises-article` pages (Praises, fans, Parodies, FOM, SCH2) get the author and the beginning of the text.
- `params.seoTitle` — the full `<title>` (and `og:title`), used as is. Without it the title is generated: by page type for songs, translations, albums, books, cycles and Praises articles; otherwise `params.name`/`title` plus a section suffix: « — Михаил Щербаков» (showcase), « — фан-клуб Михаила Щербакова» (`fans`, `Parodies`, `FOM`, `SCH2`, `Images`), the author's name in the section's language (language folders); no suffix when the name already contains «Щербаков» or «Shcherbakov».
- `params.noindex` (bool) — `noindex, follow` and no canonical (e.g. `search.md`, `Cycles/monologi.md`).
- `params.author` (`praises-article`) — also used in the generated description; for Praises articles also in the title (up to the first comma).

canonical and `og:url` point to the page itself, or, if `params.canonicalBase` is set in `hugo.json` (empty now), to the same path on that address — for when a copy of the site is published under another domain.

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
- `params.backUrl`, `params.backTitle` — the "back" link in the corner navigation. Without them a page under `content/fans/` gets «Фан-клуб → fans/index.html», any other page «Отзывы → praises.html» (as all Praises articles do); parodies, FOM and SCH2 set them explicitly.
- `params.bgColor` — page background (`fans/fans-index.md`, `fans/memory.md`).
- `params.monoPre` (bool) — `<pre>` in a monospace font (the page's `<body>` gets `class="mono-pre"`). By default `<pre>` uses the page font: in the fan club and parodies it holds mostly verse and quotations. Set where text is aligned with spaces: `tab.md` (tablature), `statistics.md` (tables), the SCH2 questions `101-e` and `203-e` (quotations aligned with spaces), letters of sections kept in the private overlay (2026-10-14). Crosswords (`<pre class="crossword">`) are monospace without it.
- `params.prevUrl`, `params.prevTitle`, `params.prevHint`, `params.nextUrl`, `params.nextTitle`, `params.nextHint` (strings) — a page in a series read in order: «[← previous] [next →]» in one line of the corner navigation, a separate group at the top and at the bottom (`layouts/partials/series-nav.html`). Url is site-relative (`SCH2/102-e.html`), Hint is the tooltip. Set by the converter on the SCH2 question pages (1.1 … 7.5, the 4.1 polemic in between, 2026-10-17); set by hand on the FOM chapters, in table-of-contents order (2026-10-17).
- `params.palette` (string) — the page's own colour scheme: the `<body>` gets `class="palette-<name>"`, which overrides the palette variables (`assets/css/palette.css`, section "per-page schemes"). Available: `olive` — the old site's dark olive scheme (background `#666656`, light-yellow text, yellow links), used for a contents page of the private overlay (2026-10-15); `warm` — a warmer, yellower background (`#fcf2cf`) for the rest of that section (2026-10-15). A new scheme is a new `body.palette-<name>` block in `palette.css`.

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
  - `params.labels` (dictionary) — interface strings in that language: the menu and breadcrumb names (`menu`, `breadcrumbs`, `language`, `translations`, `top`, `page`), translation page labels (`original`, `translatedBy`, `showOriginal`, `hideOriginal`, `performances`, `recordedIn`, `inRussian`), the view switches (`text`, `chords`, `above`, `side`, `source`, `transpose`, `stress`), the list headings and sort buttons (`translationsTitle`, `sortTranslation`, `sortOriginal`, `sortTranslator`, `sortSongYear`; optional `sortAscending`, `sortDescending` — the tooltip of the active sort button, English by default);
  - `params.sortable` (bool) — sort buttons on the list of translations;
  - a new language may start with this settings page alone, with `"build": {"render": "never", "list": "never"}` and empty `href` in `nav`, until its main page gets text; then `build` is removed and `href` filled in (so it was with `eo` and `he` until 2026-10-09).
- `<language>-translations.md` (`language-translations`) — the list of translations: `params.lang`.
- An article of the section (`language-article`, `fr/ostromoukhov-2000.md`): `params.lang`, `params.crumb` (the last breadcrumb, `title` by default). `params.description` — **unused**.

## Pictures — `content/Images/*.md` (`images-page`)

- `params.subtitle`, `params.bgColor`.
- `params.centerText` (bool) — centre the text (for pages that were centred on the legacy site).
- `params.parentUrl`, `params.parentTitle` — an extra "up" link in the corner navigation (default title «Выше»).

## Directus tables — `content/admin-directus.md` (`admin-directus`)

- `params.groups` (list of `{title, tables}`) — table groups on the `/admin/directus.html` page and in the «Таблицы Directus» block of the editor's sidebar (the block reads its list from that page). `title` is the group heading (empty — the group's tables in one line joined with «и»); `tables` is a list of `{label, table, description}`: name, Directus collection name (as in the Directus Studio address), description.

## Archive — `content/Archive/*.md` (`archive-page`)

- `params.isIndex` (bool) — the archive hub page: no «Архив» link to itself in the corner navigation.
- `params.lang` — page language when not Russian (`america97`: `"en"`).
- `params.subtitle`.

## Redirect pages — `redirect`, `redirect-hub`

Small pages that keep legacy addresses alive (`content/Images/redirects/`, `content/redirects/legacy/`). Usually with `"sitemap": {"disable": true}`. They are kept three levels deep (`content/<folder>/<subfolder>/<file>.md`) so the editor collections, which read two levels of `content/`, never pick them up (their `url` is a section address such as `/SCH2/001.html`); the folder does not affect the page address.

- `params.target` (`redirect`) — where to go; a **relative** address (`"photos2000-2004.html#agolyanov"`, `"../Disks/index.html#tapes"`) so the page survives a move of the site to another folder or domain without a rebuild.
- `params.map`, `params.default` (`redirect-hub`) — for a legacy page that had several anchors: `map` = old anchor → new address, `default` = where to go without an anchor.
- `params.noindex` (bool) — add `noindex` to the redirect page.
