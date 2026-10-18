[Русская версия](README.ru.md)

# About

This project, built with [HUGO](https://gohugo.io/), static site generator written in [Go](https://go.dev/), develops the layout of website dedicated to the works of Mikhail Shcherbakov, a russian songwriter and performer. The original website was created by Vladimir Smirnov in the mid-1990s at <https://blackalpinist.com/scherbakov/>. The maintained version, serving as the starting point for the project, is available at <https://lambda.mkshch.com/>.

The goal of the project was to create a responsive layout for the website while preserving the original style and content as much as possible, making the website more usable for visitors and easier to maintain. The following objectives were set:

1. Convert current set of the whole website's pages into HUGO project manually.
2. Update the website's markup to be more friendly to modern browsers and search engines.
3. Make the layout responsive for convenient use on various devices.
4. Improve the overall user experience and interface, while preserving the style and intent of the website's creators. Add functionality, e.g. in the chords pages. Use JavaScript where appropriate.
5. Maintain the simplicity and appearance of the current version: avoid excessive CSS complexity, refrain from overloading the user interface, optimize the graphic elements.

By design, the website was to keep its old-fashioned style while being as usable as possible. By October 2026 the main objectives have been achieved: all pages of the old website have been converted into HUGO, the markup has been updated and the layout is responsive; data on songs, concerts, albums and books is kept in a [Directus](https://directus.io/) database (on [PostgreSQL](https://www.postgresql.org/)), the song catalogue has been rethought, and song pages have chord display modes and transposition. New goals have become possible too: full-text search ([Pagefind](https://pagefind.app/)), a catalogue of translations and language sections, and editing texts in the browser. The aim not to depart from simplicity and the old look (objective 5) remains a working principle.

The code, templates, and documentation were largely written with the help of AI ([Claude](https://claude.ai/)) under the guidance and review of project participants. AI was also used to prepare page content in languages ​​other than Russian and English.

Specific implementation aspects, e.g. integration with the studio records store or changing the russian character encoding, are intentionally not considered here, as they are deemed not significant enough for the main readme file.

Currently, the website is created and maintained by a small Russian-speaking community, which explains why the vast majority of the pages are in Russian. Unfortunately, this circumstance makes it more difficult to attract new people and resources to the project, but at the same time, it gives hope that the website will be cared for by individuals who are passionate about both the work and person of Mikhail Shcherbakov and the memory of the website's creator, Vladimir Smirnov.

The website is created and maintained by people not affiliated with the author, Mikhail Shcherbakov, although some of them know him personally. Moreover, a significant portion of the content is not approved by the author. Therefore, the website will remain unofficial in the foreseeable future. Nevertheless, it continues to be, as it has been for the past decades, the most complete collection of the author's texts on the internet, as well as materials dedicated to him.

# Terminology

- Performer abbreviations used throughout the database: MKS — Mikhail Konstantinovich Shcherbakov; MLS — Mikhail Leonidovich Starodubtsev.
- The term "event" almost always refers to a concert (public or private/home) or a studio recording session (or a series of sessions).
- The project clearly distinguishes between songs (`works` — e.g. in the song catalogue) and performances (`perfs` — e.g. on the concerts list page). Performances belong to events (both concerts and studio recordings), while songs belong to published editions. Performances are naturally linked to songs in the database, but they remain distinct entities.

# Structure

Hugo's configuration is `hugo.json` in the root directory (site parameters); the menus are in `config/_default/menus.json` (Hugo merges the files of `config/_default/` into the configuration). The Directus access token lives in `config/_default/params.json`, which is not in git: copy `config/_default/params.json.example` to it (see Building below).

Standard Hugo directories:

- `content` -- the pages: `.md` files whose body is mostly HTML markup. At the top of each file there is *front matter* -- page parameters in JSON. The fields the templates actually read are listed in [docs/frontmatter.md](docs/frontmatter.md);
- `layouts` -- templates: page layouts in `layouts/miscellaneous`, shared parts in `layouts/partials`, shortcodes for page bodies in `layouts/shortcodes`. `{{< lastmod "translations" >}}` gives the date of the latest record added to a Directus collection (on the home page). `{{< translations-count >}}` gives the number of translations into the page's language and the date of the latest one, as " (59, 07.10.26)" with the date in red (on the main language pages). Records migrated from the old site have no creation date, so for them only the number is shown;
- `assets` -- files processed during the build: CSS (`assets/css`; all shared colours are CSS variables in `assets/css/palette.css`, embedded into every page by `layouts/partials/palette.html` together with `assets/css/site.css`, the rules for every page, e.g. no underline on hovered links; `assets/css/mobile-header.css` is the compact mobile header shared by the home page, search and the three catalogues) and SVG icons (`assets/svg`: album icons for the song catalogue, `svg/cd`, and format icons, `svg/format`);
- `static` -- files copied to the site as they are: images, PDFs and other downloadable files; `static/admin` is the in-browser editor (see "Editing in the browser" below);
- `archetypes` -- the template for new pages;
- `public` -- where Hugo puts the built site. It is not stored in git: the published site is built by GitHub Actions (see below).

Project directories:

- `docs` -- project documentation (mostly in Russian): the Directus schema and conventions ([docs/directus.md](docs/directus.md)), the front matter reference, the site structure analysis ([docs/site-structure-analysis.md](docs/site-structure-analysis.md)) and plans for migrating legacy sections;
- `scripts` -- Python tools: `check-links.py` (links to pages that do not exist yet), `check-separation.py` (see "Two sites in one" below), `sveltia-normalize.py` (see "Editing in the browser" below), `comments-markup` (markup of the comments texts), `legacy-convert` (used to convert legacy pages to Hugo content; the conversion is complete);
- `directus-extensions` -- sources of some custom Directus extensions;
- `workfiles` -- local working files (images, tables, drafts). The directory is in `.gitignore`.

A part of the site's content (song catalogue, concerts, performances, albums, books, announces) is served from an external Directus database (`db.sch.com.ru`) rather than from files in this repository. To learn how the data is organised:

- [docs/directus.md](docs/directus.md) describes the collections, their relations, automation (Flows) and naming conventions;
- `https://db.sch.com.ru/server/specs/oas` with the public token (see Building) returns the OpenAPI description of exactly the collections and fields that token can read. Open it in any OpenAPI viewer, e.g. Swagger UI;
- the API itself shows real records, e.g. `https://db.sch.com.ru/items/works?limit=5` with the token in the `Authorization: Bearer` header or the `access_token` query parameter.

## Menus

The menus are in `config/_default/menus.json`: `indexheadermenu` and `indexfootermenu` (home page), `searchheadermenu`, `ctgheadermenu` (song catalogue), `trnheadermenu` (translations), `concertsheadermenu`. `layouts/partials/menu.html` renders them. Besides the standard `name`, `pageRef`/`url`, `weight`, `parent`/`identifier`, an entry may have `params`:

- `shortName` -- the label in the mobile version (the full `name` is shown on wide screens): «Песни», «Концерты», «Главная»;
- `mobileOnly: "yes"` -- the entry is shown only in the mobile version;
- `icon: "home"` / `"search"` -- a grey icon before the label (`layouts/partials/menu-icon.html`);
- `isDateToPrint: "yes"` -- the update date after the label: the `lastmod` of the target page (top level of its front matter, not inside `params`), or, with `dynamicLastmod: "works"` / `"translations"`, the date the latest record was added to that Directus collection. The date is printed by `layouts/partials/menu-datum.html`: «13.10.26» in line with the label; in narrow menu columns it goes below the label in a smaller font and with the full year, «13.10.2026». A page without a date gets none (planned changes: [docs/editor-pages-plan.md](docs/editor-pages-plan.md), step 3);
- `collapsible: "yes"` with children marked `toggleChild: "yes"` -- a section whose sub-entries open as further cells («Фан-клуб»); `dropdown: "yes"` -- a list opening inside its own cell («Языки», the children have `lang`).

In the mobile version the menu hides behind the button and is laid out in columns: one column below 18.75em, two from 18.75em, three from 35em (300 and 560 px at the default font size; all thresholds are in `em`, so they grow with the reader's font size). The home page header has two steps: below 25em the title and the button are smaller; from 25em the button has its full size and the title is centred.

## Search page

`search.html` searches the Pagefind index (see Building). The scope is two checkboxes, "song texts" (on by default) and "the rest of the site"; the choice is kept in the `searchScope` cookie (path `/shcherbakov/`, one year). With no scope selected the page says so instead of searching.

## Two sites in one

The site is split into a *showcase* (songs, catalogues, concerts, albums, books, biography, news, shop) and a *fan club* (reviews, comments, pictures, parodies and other fan materials). Showcase pages must not link to the fan club in their text; the fan club may link to the showcase, and both are reachable from the menus. `scripts/check-separation.py` checks this rule on the built site. The decisions and their reasons are in [docs/showcase-and-club.md](docs/showcase-and-club.md) (in Russian); the link analysis behind them is in [docs/site-structure-analysis.md](docs/site-structure-analysis.md).

# Building

The project requires:

- [Git](https://git-scm.com/) to work with this repository;
- [Hugo](https://gohugo.io/installation/), a recent version. The standard edition is enough: the project uses neither Sass nor image processing. GitHub Actions builds the site with the latest Hugo release, so a template that works with an older local Hugo may still fail there;
- a Directus access token in `config/_default/params.json`: pages request their data from Directus during the build. Copy `config/_default/params.json.example` to `config/_default/params.json`; it contains a public read-only token. That token can read only published data, without internal notes, and cannot change anything; the site it builds is identical to the published one;
- [Node.js](https://nodejs.org/) (for `npx`), only to build the search index: `npx pagefind --site public` after `hugo`. Without it the search page does not work locally;
- Python 3, only to run the tools in `scripts`.

Run `hugo server` for a local preview, or `hugo` to build the site into `public`.

# Publishing

The site is built and published to GitHub Pages by GitHub Actions ([.github/workflows/static.yml](.github/workflows/static.yml)):

- on every push to `master`, on manual start, and on schedule twice a day (05:00 and 17:00 UTC), so that data changed in Directus reaches the site without a push;
- first the workflow checks that Directus answers and that the public token reads data from the collections the build uses; if not, the workflow stops and the published site stays as it was (otherwise Hugo would build pages with empty data);
- before each build the workflow archives announces whose expiry date has passed (sets their status in Directus to `archived`);
- the build uses the public read-only Directus token from `params.json.example`, runs Hugo, then Pagefind to make the search index.

## Editing in the browser

`/admin/` on the site is [Sveltia CMS](https://sveltiacms.app/), an editor for files in this repository: `static/admin/index.html` loads it, and `static/admin/config.yml` sets what it edits. It does not change any other page of the site. Each save is a commit to `master` made through the GitHub API, and the usual workflow publishes it. Data kept in Directus (titles, years, albums, translators, announces, comments) is edited in Directus. The collapsible "Таблицы Directus" block at the bottom of the editor's left panel lists links to the Directus Studio tables by group (they open in a new tab); its last line, "Что в какой таблице", opens `/admin/directus.html`, the same links with descriptions. The groups and descriptions live in `content/admin-directus.md` and are edited in the editor itself ("Страницы сайта"); the block reads its list from that page (`.table-link` links with `data-label`), so there is one source. The block is inserted by a script in `static/admin/index.html`, since Sveltia has no custom links in its panel; whether it is open is remembered in the browser.

### Signing in

- "Sign In with GitHub" works for anyone with write access to the repository. Sign-in goes through an OAuth proxy, `sveltia-cms-auth` on Cloudflare Workers (`https://sveltia-cms-auth.sergey-897.workers.dev`, the `base_url` in `config.yml`):
  - the proxy holds the client ID and secret of the GitHub OAuth App in its variables, plus `ALLOWED_DOMAINS` (the site's host and `localhost`);
  - the OAuth App is registered in the repository owner's GitHub settings, with the callback URL `<proxy>/callback`;
  - the editor asks GitHub for the `public_repo` scope (`auth_scope`), not the default `repo`, which would also reach private repositories.
- "Sign In Using Access Token" takes a GitHub personal access token that each editor makes in their own GitHub settings; the token stays in their browser:
  - the repository owner can use a fine-grained token: Repository access → this repository, Permissions → "Contents: Read and write";
  - a collaborator cannot use a fine-grained token, because such a token reaches only repositories of its own owner or of an organization. A collaborator makes a classic token with the `public_repo` scope instead. It can write to every public repository the collaborator has access to, not only this one.
- On localhost the editor also offers to work with a local copy of the repository, without signing in to GitHub — see "Editing on your own computer".

### Editing on your own computer

The same editor works with a clone of the repository on disk: changes show at once in `hugo server` and are published only when you commit and push them yourself. Handy for many edits in a row and for checking the result before publishing.

1. You need a clone of the repository, Hugo and `config/_default/params.json` (see "Building"), and a Chromium browser — Chrome or Edge: the editor opens a folder on disk through the File System Access API, which Firefox and Safari lack (in Brave it has to be enabled in `brave://flags`).
2. Update the clone (`git pull`) so you do not edit stale files, and run `hugo server` in its root.
3. Open `http://localhost:1313/shcherbakov/admin/`, click "Work with Local Repository" and pick the clone's root folder (the one holding `.git`); the browser asks for read and write permission.
4. Edit as usual. "Save" writes the file straight to disk: no commit and no build on GitHub. `hugo server` rebuilds the page at once, and "view on site" leads to `localhost:1313`.
5. Check the changes (`git status`, `git diff`), commit and push (`git push`) — the GitHub build publishes them as always.

A picture inserted with the editor's button is copied into the clone's `static/Images` and goes into the commit too.

### What can be edited

- Song texts (`content/texts`) and translations (`content/<language>/`, one collection, with language folders in the sidebar): the text, and for songs the tonality, `chordsStartAt` and `textFinishAtLine`.
- Language pages: title and body.
- Site pages: title and body of the home page, biography, about, where to buy, news (the chronicle; announces come from Directus), what is missing, tablature, statistics, the log (the old chronicle), the list of reviews (`praises.md`) and «Другие публикации» on the books page; the body of the footer. The song and translation catalogues, concerts and search have the title, search engine fields and the introduction: the rest is built by the template from Directus. The home page body is HTML laid out in blocks, so edit it with care: an unclosed tag breaks the home page.
- Reviews (`content/Praises`): title, author, subtitle and body.
- Fan-club articles — one collection over several folders: `fans` (with the comments page `kom.md`), `Parodies`, `FOM` (Щ-1), `SCH2` (Щ-2), plus `sociology.md` and `kniga_pamyati.md`. The editor's sidebar shows a folder tree; picking a folder narrows the list. Fields: title, address (`url`), author, subtitle, "back" link and body. The "back" link is the corner-navigation item at the top and bottom of the page ([Фан-клуб], [Пародии], [Щ-1]) that leads to the parent page: the "address" is a path from the site root without a leading slash (`fans/index.html`), the "title" is the link text. Empty — the section's own table of contents; set it only when the parent is another page (as on the Щ-1 table of contents, which leads to «Фан-клуб»). Entries are selected by address, so the redirects from old addresses live deeper, in `content/redirects/legacy/`, and are not listed.
- Albums, cassettes, books, cycles and the tour archive (`Disks`, `Tapes`, `Books`, `Cycles`, `Archive`) — also one collection with a folder tree: title, subtitle, search engine fields and body. The data (tracks, covers, imprint) come from Directus by `params.id`; the parameters are not shown in the form and are kept as they are.
- Picture pages in `content/Images` (`images-page` layout): title, subtitle, "back" link, background colour, centred text and body (HTML). The redirects from old addresses in `content/Images/redirects` are not listed. Pictures themselves live in `static/Images` and are referred to by file name; the editor's insert-image button writes an address from the domain root (`/Images/…`), which does not open on github.io (site in the `/shcherbakov/` subfolder), so type the file name by hand.
- The body of articles and picture pages is a Markdown field in source-only mode: the same HTML is edited as text, and the preview renders it (without the site's styles; scripts and iframes are stripped). Sveltia resolves relative addresses in the preview against the domain root only, so a script in `static/admin/index.html` sets the preview's base to the site's `Images/` folder: pictures and links of picture pages and articles show as on the site, except `../../` addresses from fan-club subfolders.
- For search engines, on site pages, language pages, articles and picture pages: "Search engine title" (`params.seoTitle`) and "Search engine description" (`description`), both optional; see [docs/frontmatter.md](docs/frontmatter.md).

Other front matter keys are kept as they are, but the editor writes the keys it does not know in alphabetical order and indents JSON with 4 spaces. All editable collections except songs and translations (articles, albums and books, picture pages, site pages and language pages) were brought to this layout in advance, so editing a page does not rewrite its whole front matter in the diff. `scripts/sveltia-normalize.py <collection>` does that — by hand, once, when a collection is added or its fields change; for folder (also nested and filtered) and file-list collections alike, and `--check` lists the files that differ; run it again if the fields of these collections in `config.yml` change.

### New entries

- Songs and translations cannot be created, deleted or renamed in the editor, because a file name is the record's id in Directus. A new song or translation is created in Directus; a Directus Flow then commits an empty file for its text (see [docs/directus.md](docs/directus.md)), and after a reload the entry shows up in the editor.
- Reviews and fan-club articles can be created. The file name is typed in Latin letters. A review's page URL is `Praises/<name>.html`. For a fan-club article the section folder is set by the "Parent Folder" field (the folder open in the list is filled in), and the address goes into the «Адрес» field — the same section and name: `/fans/imya.html`. Without it the article would not show in the list, which selects entries by address. The editor fills `type` and `layout` itself; the "back" link defaults to the section's table of contents. A new article needs a link in its section's list: the list of reviews (under site pages) or its section's table of contents.
- Articles cannot be renamed or deleted in the editor (the file name is typed only when an article is created), because other pages link to them. Delete them with git and run `check-links.py`.

### Saving

- A click on "Save" opens a small confirmation box under the button: Enter or "Save" confirms, Escape or "Cancel" goes back. Ctrl+S (Cmd+S) saves at once, without the box.
- After saving, the editor stays open on the entry. This is the editor's own setting "Close the editor after saving a draft"; the page turns it off for anyone who has not changed it, and it can be switched back in the editor's settings.
- Both are done by a script in `static/admin/index.html` that runs before the editor loads. It recognises the button by its label on the editor toolbar, so a future editor version may need it adjusted.

### The text field

- Songs, translations, site pages and language pages are edited as plain text, so spaces, indentation and chords stay exactly as typed. Articles and picture pages have a Markdown field in source-only mode (see "What can be edited").
- For songs and translations the field uses a monospace font with its own Cyrillic (PT Mono), does not wrap lines and takes the full width of the pane, because chords are aligned with spaces. With a font that lacks Cyrillic, the browser takes the letters from another font, and the chords drift. For other pages long lines wrap like paragraphs. A script on the page picks the mode from the collection in the address.
- The preview of songs and translations shows the text as the "source" view of a song page does: in `<pre>`, in the browser's default monospace font (the same as on the site). Song parameters are not shown there.
- A badge in the corner shows the line and character under the cursor, both counted from 1: the same numbers as `textFinishAtLine` and `chordsStartAt`.
- The editor puts a blank line after the front matter and writes a file with empty front matter without one. `layouts/partials/song.html` ignores blank lines before the text, so the line number in `textFinishAtLine` is not shifted.

# Links

Current development build of the project, published automatically via GitHub Actions (see `.github/workflows/static.yml`), is viewable on our GitHub Pages:

- <https://zlochevsky.github.io/shcherbakov/>

Links on Mikhail Shcherbakov:

- <https://lambda.mkshch.com/> -- startpoint version of the site (mostly in Russian);
- <https://lambda.mkshch.com/English/index.html> -- the english page of the site.

Links on the website creator:

- <https://blackalpinist.com/> -- collection of mountaineering resources for the Russian communities of North America. (mostly in Russian);
- <https://blackalpinist.com/~mi/orizaba/release_e.html> -- press release on December 28 1999 about death of Vladimir Smirnov and his companions (in English).

Links on HUGO:

- https://gohugo.io/ -- the official HUGO site
- https://gohugo.io/installation/ -- HUGO installation manuals
- https://gohugo.io/documentation/ -- HUGO documentation
- https://www.youtube.com/playlist?list=PLLAZ4kZ9dFpOnyRlyS-liKL5ReHDcj4G3 -- HUGO video tutorials

