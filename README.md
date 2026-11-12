[Русская версия](README.ru.md)

# About

A website presenting the work of Mikhail Shcherbakov, a Russian songwriter and performer: song texts with chords, concerts, discography, reviews and fans' materials. The project continues the website created by Vladimir Smirnov in the mid-1990s, keeping its look and content, and is run by fans.

## History

The original website was created by Vladimir Smirnov in the mid-1990s at <https://blackalpinist.com/scherbakov/>. A community formed around it, with enthusiastic discussions of Mikhail Shcherbakov's work. Thanks to the community and to Vladimir's own activity, materials were added to the website in abundance: people shared impressions of concerts, sent links to reviews on the internet, photographs, academic and critical works, interviews; some participants wrote articles themselves; joint studies of Mikhail Shcherbakov's audience were carried out with the Public Opinion Foundation (FOM), and so on. After the tragic death of the website's creator at the end of 1999, the community stayed more or less active for about ten more years. During that time and after it, editors faithfully kept the website up in its original form. With the spread of the LiveJournal blogging platform and the arrival of Facebook, activity within the community naturally declined. After that, the idea of a new website came up again and again in private conversations. Depending on ready-made engines and site builders like WordPress was undesirable, investing in private development risked being unjustified, and a project controlled by one person, it seemed, could sooner or later set itself against the community.

In 2024, contact with the website's administrator was lost. After that, the editor declared one of the website's mirrors, <https://lambda.mkshch.com/>, its main address, leaving a redirect on the original server (limited technical access to the server remained). The version the project took as its starting point is expected to stay available on one of the mirrors, e.g. <https://deniskhin.ru/scherbakov/>, after the project moves to the main address.

Since the website was technically about twenty-five years out of date, an initiative group (Sergey Zlochevsky, Denis Milokhin and Liya Shabakaeva) decided to make it usable on mobile screens without losing any content, and to make shared work on it possible. To some extent, this was achieved by October 2026.

## First stage

The first step was to make the website convenient for visitors on any device and easy to maintain. The following objectives were set:

1. Convert all pages of the old website into a [HUGO](https://gohugo.io/) project manually.
2. Update the website's markup to be more friendly to modern browsers and search engines.
3. Make the layout responsive for convenient use on various devices.
4. Improve the overall user experience and interface, while preserving the style and intent of the website's creators. Add functionality, e.g. in the chords pages. Use JavaScript where appropriate.
5. Maintain the simplicity and appearance of the old version: avoid excessive CSS complexity, refrain from overloading the user interface, optimize the graphic elements.

By October 2026 these objectives have been achieved: all HTML pages of the old website have been converted into HUGO, the markup has been updated and the layout has become responsive; the pages have been re-encoded from KOI8-R to UTF-8; data on songs, concerts, albums and books is now kept in a [Directus](https://directus.io/) database (on [PostgreSQL](https://www.postgresql.org/)), the alphabetical, chronological and other song catalogues have been rethought as a single catalogue, and song pages have chord display modes and transposition. New goals have been set and achieved as well: full-text search ([Pagefind](https://pagefind.app/)), a catalogue of translations, language sections, and in-browser text editing for the site's editors. The project is meant to replace the old website at its address, so old links should lead to the corresponding new pages: redirects are planned for pages whose path has changed.

## Goal

The goal of the project is to develop, through the community's efforts, a website presenting Mikhail Shcherbakov's work on the internet.

The project sees its task as follows:

- to publish the author's latest editions of the texts and provide them with harmonies (where possible, the author's own and correct ones);
- to announce upcoming concerts and share information about past ones;
- to keep data on the author's printed editions, the discography, and the catalogue of performances, shown on the website as the concert catalogue;
- to publish materials related to Mikhail Shcherbakov's work on the website, and links to such materials on the internet (reviews, criticism, essays, reflections, research, interviews, concert photographs, song translations into other languages, fans' creative work, other people's projects with Shcherbakov's songs);
- not to publish the author's recordings of songs, but to link to the online store and to streaming services that pay royalties;
- to maintain and improve the website and make shared work on it possible;
- to maintain continuity with the old website.

## Work areas

1. **Events** — following Shcherbakov's concerts and keeping the information on the main page up to date, keeping the announcements, the news section and the "Log".
2. **Fan club, performers, criticism** — looking for information on events among performers of Shcherbakov's songs (not started yet), not missing interesting photographs, following publications on the internet (including discussions in blogs and social networks, and videos), fans' creative work, criticism, academic work; maintaining the "Dictionary of Foreign Words".
3. **Code and maintenance** — development, support, and the project's infrastructure. Writing the documentation, keeping it up to date and in order. Further organizing of the fan club and criticism materials now that they have been moved from the old website. How the website works is described in this README and in `docs/`.
4. **Performances** — the database of concerts and studio recordings: adding and checking what was performed, where and when, and what was special about particular performances. The books and discs sections of the website go with it.
5. **Texts and music** — keeping the song catalogue, correcting errors found in the texts, recording performance variants in the texts. Chords (notation) in the song texts: correcting errors, refining, making the notation more convenient, without a zealous drive to show every nuance in it.
6. **Statements** — organizing the author's remarks (answers to notes from the audience, introductions to songs). An ambitious area; work has not started yet.
7. **Language sections** — adding song translations into other languages, creating website pages in other languages. Each language section is meant to be curated by one person.

## Principles

- **Simplicity and the old look.** The website keeps its old-fashioned style while striving to become more convenient: no excessive CSS complexity, no overloaded interface, new graphics optimized.
- **Unofficial status.** The website is created and maintained by people not affiliated with the author, Mikhail Shcherbakov, although some of them know him personally. The texts of most songs in the catalogue have been checked against the edition "Собрание текстов" (Collected Texts, 2023), but a fair part of the other content is not approved by the author, so the website will remain unofficial in the foreseeable future. Nevertheless, as in the past decades, it remains the most complete collection of the author's texts and materials about him on the internet.
- **AI under human review.** The code, templates, and documentation were largely written with the help of AI ([Claude](https://claude.ai/)) under the guidance of project participants. AI was also used to translate the main pages into other languages; these translations await review by the section curators.

## Participation

Editing rights in the database are given by area: each person can get the role with access to the sections they need (see ["Who updates the site and how"](#who-updates-the-site-and-how) below). When the work is shared among people, the website does not rest on one person.

The data outside the database (e.g. song texts, chords, translations, articles, gallery pages, other pages of the old website, page parameters (front matter), page templates, project documentation) is kept in this public repository. Participants with write access edit it directly (including through the `/admin/` editor); anyone can propose a change with a pull request.

Currently, the website is created and maintained by a small Russian-speaking community. The vast majority of the website's pages and of the code documentation is naturally written in Russian, but the community considers itself open to working both with those who speak Russian but do not read it (e.g. children of emigrants who know another language well) and with those who do not know Russian at all. The community encourages good equirhythmic translations of Mikhail Shcherbakov's songs into other languages. It would like to widen the website's language coverage by finding curators for its language sections. The community is ready to expand the documentation in English. It hopes that the website will be cared for by people who hold dear the work and person of Mikhail Shcherbakov.

How new participants will join the work is not decided yet. The editorial email is always available: <deniskhin@gmail.com>.

# Terminology

- Performer abbreviations used throughout the database: MKS — Mikhail Konstantinovich Shcherbakov; MLS — Mikhail Leonidovich Starodubtsev.
- The term "event" in the project always or almost always refers to a concert (public or private/home) or a studio recording session (or a series of sessions).
- The project clearly distinguishes between songs (`works` — e.g. for the song catalogue) and performances (`perfs` — e.g. for the concerts list page). Performances of songs are always linked to an event (a concert or a studio recording). Printed editions contain the songs themselves (song texts), with no link to the events at which they may have been performed.

# Structure

Hugo's configuration is `hugo.json` in the root directory (site parameters); the menus are in `config/_default/menus.json` (Hugo merges the files of `config/_default/` into the configuration). The Directus access token lives in `config/_default/params.json`, which is not in git: copy `config/_default/params.json.example` to it (see Building below).

Standard Hugo directories:

- `content` — the pages: `.md` files whose body is mostly HTML markup. At the top of each file there is *front matter* — page parameters in JSON. The fields the templates actually read are listed in [docs/frontmatter.md](docs/frontmatter.md). It holds both sections of the old site and new ones:
    - inherited from the old site: sections `Archive/`, `Books/`, `Disks/`, `fans/`, `FOM/`, `Images/`, `Parodies/`, `Praises/`, `SCH2/`, `Tapes/`, pages `about.md`, `bio.md`, `buy.md`, `kniga_pamyati.md`, `log.md`, `news.md`, `no.md`, `praises.md`, `sociology.md`, `statistics.md`, `tab.md`;
    - new sections and pages:
        - sections: language subdirectories `de/`, `en/`, `eo/`, `fr/`, `he/`, `uk/` (more may follow), `texts/` for song texts; `redirects/legacy/` for redirect pages from old URLs (such as `/Tapes/index.html`); redirects from old song addresses (`/htmtexts/<year>/<id>.html`, `/htmaccords/<year>/<id>.html`) and yearly indexes are not files: `redirects/legacy/songs/_content.gotmpl` creates them at build time from `data/legacy-songs.json` (old path → song id), and the `redirect-song` layout finds the song page; `Cycles/` for song cycles (its pages have front matter only, as they take their content from the Directus database at build time);
        - pages: `admin-directus.md` — a reference page for the editor describing the tables in the Directus database; `catalogue.md` — the song catalogue; `concerts.md` — the concert catalogue; `translations.md` — the translations catalogue (all three catalogues have front matter only, as they take their content from Directus at build time); `search.md` — the search page (front matter only too, as the page has no text of its own); `_index.md` and `_footer.md`, the content of the home page;
- `layouts` — templates: page layouts in `layouts/miscellaneous`, shared parts in `layouts/partials`, shortcodes for page bodies in `layouts/shortcodes`. `{{< lastmod "translations" >}}` gives the date of the latest record added to a Directus collection (on the home page). `{{< translations-count >}}` gives the number of translations into the page's language and the date of the latest one, as " (59, 07.10.26)" with the date in red (on the main language pages). Records migrated from the old site have no creation date, so for them only the number is shown;
- `assets` — files processed during the build: CSS (`assets/css`; all shared colours are CSS variables in `assets/css/palette.css`, embedded into every page by `layouts/partials/palette.html` together with `assets/css/site.css`, the rules for every page, e.g. no underline on hovered links; `assets/css/mobile-header.css` is the compact mobile header shared by the home page, search and the three catalogues) and SVG icons (`assets/svg`: album icons for the song catalogue, `svg/cd`, and format icons, `svg/format`);
- `static` — files copied to the site as they are: images, PDFs and other downloadable files; `static/admin` is the in-browser editor (see "Editing in the browser" below);
- `archetypes` — templates for new pages, not used in the project (archetypes only apply when a page is created with `hugo new content ...` in the terminal);
- `public` — where Hugo puts the built site. It is not stored in git: the published site is built by GitHub Actions (see below).

Project directories:

- `docs` — project documentation (mostly in Russian): the Directus schema and conventions ([docs/directus.md](docs/directus.md)), the front matter reference, the site structure analysis ([docs/site-structure-analysis.md](docs/site-structure-analysis.md)) the rules for converting legacy pages ([docs/legacy-conversion.md](docs/legacy-conversion.md)) and plans of open work (`docs/*-plan.md`);
- `scripts` — Python tools: `check-links.py` (links to pages that do not exist yet), `check-separation.py` (see "Two sites in one" below), `sveltia-normalize.py` (see "Editing in the browser" below), `comments-markup` (markup of the «Словарь» texts), `legacy-convert` (used to convert legacy pages to Hugo content; the conversion is complete), `directus-schema.py` (Directus schema snapshot, Flows and permissions export, relation diagrams in docs/directus.md), `directus-roles.py` (editor roles and permissions by work area, see «Роли и права» in docs/directus.md), `legacy-concerts-sync.py` (copies concerts and their programmes into Directus from the old concerts page, which is still maintained: it only adds, by default it only reports, writing is `--apply` with the admin token; `--fix` corrects fields of existing records; see «Сверка со старой страницей концертов» in docs/directus.md; manual matches in `legacy-concerts-sync.json`), `legacy-photos-sync.py` (copies concert photos from the old page into `static/photos/<event id>/01.jpg`, recompressing them; it only adds, writing is `--apply`; manual matches in `legacy-photos-sync.json`);
- `directus-extensions` — all Directus extensions: sources of our own (`setlist-editor`, `perf-picker`, `album-tracklist`) and built third-party packages, see [docs/directus.md](docs/directus.md);
- `workfiles` — local working files (images, tables, drafts). The directory is in `.gitignore`.

As mentioned, a part of the site's content (namely song metadata, concerts, data on performances, albums, books, announces and more) comes not from files in this repository but from an external Directus database (`db.sch.com.ru`). To learn how the data is organised:

- [docs/directus.md](docs/directus.md) describes the collections, their relations, automation (Flows) and naming conventions;
- [docs/directus-snapshot.json](docs/directus-snapshot.json) is a snapshot of the database schema (all collections, fields and relations), [docs/directus-export/](docs/directus-export/) an export of the Flows and the permission model; both are refreshed with `scripts/directus-schema.py --fetch` after every model change, so git history shows what changed and when. They need neither the server nor a token;
- `https://db.sch.com.ru/server/specs/oas` with the public token (see Building) returns the OpenAPI description of exactly the collections and fields that token can read. Open it in any OpenAPI viewer, e.g. Swagger UI;
- the API itself shows real records, e.g. `https://db.sch.com.ru/items/works?limit=5` with the token in the `Authorization: Bearer` header or the `access_token` query parameter.

## Menus

The menus are in `config/_default/menus.json`: `indexheadermenu` and `indexfootermenu` (home page), `searchheadermenu`, `ctgheadermenu` (song catalogue), `trnheadermenu` (translations), `concertsheadermenu`. `layouts/partials/menu.html` renders them. Order and entries are easier to edit in the editor: «Порядок меню» (see "Editing in the browser"). Hugo sorts entries by `weight`, not by list position, so in the file the `weight`s follow the entries' order (10, 20, 30…) and children come right after their section; on saving from the editor a script in `static/admin/index.html` recalculates them.

The order of entries is set twice, and the two must agree: **Hugo looks only at `weight`** (the position in the file does not matter to it; equal `weight`s go alphabetically), while **the editor looks only at the position in the list**: it shows entries in file order and on saving rewrites `weight` from that position, dropping the old numbers. So when editing `menus.json` by hand, move the entry itself (a child right after its section) and change its `weight` so the numbers grow from top to bottom. If only `weight` is changed, the site order changes, but the next save of the menus from the editor puts the entry back where it stands in the file.

Besides the standard `name`, `pageRef`, `weight`, `parent`/`identifier`, an entry may have `params`:

- `shortName` — the label in the mobile version (the full `name` is shown on wide screens): «Песни», «Концерты», «Главная»;
- `mobileOnly: "yes"` — the entry is shown only in the mobile version;
- `icon: "home"` / `"search"` — a grey icon before the label (`layouts/partials/menu-icon.html`);
- `date: "hide"` / `"show"` — an exception for the date: hide or show it on this entry regardless of the page (normally not needed, see below);
- `collapsible: "yes"` with children marked `toggleChild: "yes"` — a section whose sub-entries open as further cells («Фан-клуб»); `dropdown: "yes"` — a list opening inside its own cell («Языки», the children have `lang`).

The update date after an entry's label is a property of the page it leads to, not of the entry: one link behaves the same in every menu. On the page it is set by the «Показывать дату в меню» checkbox (`params.menuDate`) and «Откуда дата для меню» (`params.menuDateFrom`), both in the editor under the page's parameters. The source: empty — the page's own «Дата» field (`lastmod`, top level of the front matter); `praises`, `club`, `images`, `texts`, `translations` — the latest «Дата» among reviews, fan-club articles (fans, parodies, Щ-1, Щ-2), picture pages, song texts, translations; `announces` — the latest publication date among the active Directus announces (none active — no date). A collapsible entry without a page of its own («Фан-клуб») gets the latest of its children's dates. No date — none in the menu: Hugo does not fall back to the file's modification time (`hugo.json` → `frontmatter.lastmod`), which on the site would be the build time. The date is computed by `layouts/partials/menu-entry-date.html` and `menu-date.html` and printed by `menu-datum.html`: «13.10.26» in line with the label; in narrow menu columns below the label in a smaller font and with the full year, «13.10.2026».

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

## Who updates the site and how

Changes reach the site in two ways: through the Directus database and through the repository.

**The Directus database** (Directus Studio, `db.sch.com.ru`). Roles:

- **Administrator** — everything, including the data model, Flows and permissions (the "Code and maintenance" area);
- **Content editor** — editing in all site tables;
- **six area editors** («Редактор: События», «…: Фан-клуб, исполнители, критика», «…: Исполнения», «…: Тексты и музыкальная часть», «…: Высказывания», «…: Языковые разделы», i.e. Events, Fan club, Performances, Texts and music, Statements, Language sections) — read everything, edit only their area's tables. Which tables belong to which area: «Роли и права» in [docs/directus.md](docs/directus.md).

Changes in the database appear on the site with the scheduled build (twice a day), or at once with a manual run of the workflow (the «Run workflow» button on the Actions tab on GitHub). A rebuild on every save in Directus exists but is turned off.

**The repository** (song texts and translations, pages, articles, templates). Participants with write access edit the files either in the editor on the site (`/admin/`, see "Editing in the browser" below) without git, or in their own clone with git. Each save in the editor is a commit; the build on push publishes the site. A new song or translation is created in Directus; the Flow «Create text file for new song or translation» creates the file for its text (see [docs/directus.md](docs/directus.md)).

Rights in the database and in the repository are independent: a texts editor, for instance, needs both the «Редактор: Тексты и музыкальная часть» role in Directus and write access to the repository.

New concert photos are uploaded to Directus file storage: the «Фотографии» field (`photos`) of the event in Directus, in the order set there; editors upload a copy of at most 3000 pixels, not the original (rules in docs/photos-plan.md). Directus makes the sizes itself by presets (`concert-cover`, `gallery`, see «Файлы и пресеты» in docs/directus.md), and Hugo downloads them at build time into `photos/<event id>/`. Photos transferred earlier (mostly from concerts, but not only) are files in the repository, in `static/photos/<event id>/` (outside `Images/`: they belong to the showcase, not the fan club), in file name order (`01.jpg`, `02.jpg`…). The concert catalogue takes the photos of the `photos` field first, otherwise it finds the folder by itself: the first photo is the cover of an expanded concert, and the «Фотографии» filter selects concerts with or without one. Hugo shrinks a photo larger than the 324×432 frame to a thumbnail at build time. If there are several photos (a «⧉ N» badge on the cover) or the only one is wider than 500 pixels, the cover is a button that opens all photos of the concert over the page: arrows, swipe, a counter, the caption (a Directus file title made of words); closed by Escape, the cross or a click beside the photo. The template reads the files straight from `static/photos` (`images.Config`, `resources.FromString`), without `module.mounts`: `config/_default/module.json` is not in git, so a mount there would never reach the GitHub Actions build. `scripts/legacy-photos-sync.py` copies the photos from the old concerts page. Where to keep the author, captions and the link of gallery photos (the «Картинки» galleries) to a concert is not decided yet. What is still to be done is in [docs/photos-plan.md](docs/photos-plan.md) (in Russian).

## Editing in the browser

`/admin/` on the site is [Sveltia CMS](https://sveltiacms.app/), an editor for files in this repository: `static/admin/index.html` loads it (the version is pinned in the script address; Sveltia releases almost daily, so it is updated by hand: change the number, check the song, page and «Отзывы» forms, commit), and `static/admin/config.yml` sets what it edits. It does not change any other page of the site. Each save is a commit to `master` made through the GitHub API, and the usual workflow publishes it. Data kept in Directus (titles, years, albums, translators, announces, comments) is edited in Directus. The collapsible "Таблицы Directus" block at the bottom of the editor's left panel lists links to the Directus Studio tables by group (they open in a new tab); its last line, "Что в какой таблице", opens `/admin/directus.html`, the same links with descriptions. The groups and descriptions live in `content/admin-directus.md` and are edited in the editor itself ("Страницы сайта"); the block reads its list from that page (`.table-link` links with `data-label`), so there is one source. The block is inserted by a script in `static/admin/index.html`, since Sveltia has no custom links in its panel; whether it is open is remembered in the browser.

### Signing in

- "Sign In with GitHub" works for anyone with write access to the repository. Sign-in goes through an OAuth proxy, `sveltia-cms-auth` on Cloudflare Workers (`https://sveltia-cms-auth.sergey-897.workers.dev`, the `base_url` in `config.yml`):
  - the proxy holds the client ID and secret of the GitHub OAuth App in its variables, plus `ALLOWED_DOMAINS` (the site's host and `localhost`); copies of the client ID and secret are in the owner's `pass`, `github.com/shcherbakov-sveltia-cms-auth_clientID` and `github.com/shcherbakov-sveltia-cms-auth_secret`;
  - the OAuth App is registered in the repository owner's GitHub settings, with the callback URL `<proxy>/callback`;
  - the editor asks GitHub for the `public_repo` scope (`auth_scope`), not the default `repo`, which would also reach private repositories.
- "Sign In Using Access Token" takes a GitHub personal access token that each editor makes in their own GitHub settings; the token stays in their browser:
  - the repository owner can use a fine-grained token: Repository access → this repository, Permissions → "Contents: Read and write";
  - a token has an expiry date (the owner's `sveltia-cms-zlochevsky` expires on 2027-10-06; a copy is in the owner's `pass`, `github.com/sveltia_token_zlochevsky`). After that GitHub rejects it and the editor can no longer load or save: regenerate the token on its GitHub settings page (Regenerate) and sign in again with the new value;
  - a collaborator cannot use a fine-grained token, because such a token reaches only repositories of its own owner or of an organization. A collaborator makes a classic token with the `public_repo` scope instead. It can write to every public repository the collaborator has access to, not only this one.
- On localhost the editor also offers to work with a local copy of the repository, without signing in to GitHub — see "Editing on your own computer".

### Editing on your own computer

The same editor works with a clone of the repository on disk: changes show at once in `hugo server` and are published only when you commit and push them yourself. Handy for many edits in a row and for checking the result before publishing.

1. You need a clone of the repository, Hugo and `config/_default/params.json` (see "Building"), and a Chromium browser — Chrome or Edge: the editor opens a folder on disk through the File System Access API, which Firefox and Safari lack (in the Brave browser, also Chromium-based, it is off and has to be enabled in `brave://flags`).
2. Update the clone (`git pull`) so you do not edit stale files, and run `hugo server` in its root.
3. Open `http://localhost:1313/shcherbakov/admin/`, click "Work with Local Repository" and pick the clone's root folder (the one holding `.git`); the browser asks for read and write permission.
4. Edit as usual. "Save" writes the file straight to disk: no commit and no build on GitHub. `hugo server` rebuilds the page at once, and "view on site" leads to `localhost:1313`.
5. Check the changes (`git status`, `git diff`), commit and push (`git push`) — the GitHub build publishes them as always.

A picture inserted with the editor's button is copied into the clone's `static/Images` and goes into the commit too.

### What can be edited

- Song texts (`content/texts`) and translations (`content/<language>/`, one collection, with language folders in the sidebar): the text, and for songs the tonality, `chordsStartAt` and `textFinishAtLine`.
- Language pages: title and body.
- Site pages: title and body of the home page, biography, about, where to buy, news (the chronicle; announces come from Directus), what is missing, tablature, statistics, the log (the old chronicle), the list of reviews (`praises.md`) and «Другие публикации» on the books page; the body of the footer. The song and translation catalogues, concerts and search have only the title, search engine fields and the date: the whole content of these pages is built by the template (from Directus; for search, from the Pagefind index), the file body is not output, so they have no «Текст» field. The home page body is HTML laid out in blocks, so edit it with care: an unclosed tag breaks the home page.
- Reviews (`content/Praises`): title, author, subtitle and body.
- Fan-club articles — one collection over several folders: `fans` (with the «Словарь» page `kom.md`), `Parodies`, `FOM` (Щ-1), `SCH2` (Щ-2), plus `sociology.md` and `kniga_pamyati.md`. The editor's sidebar shows a folder tree; picking a folder narrows the list. Fields: title, address (`url`), author, subtitle, "back" link and body. The "back" link is the corner-navigation item at the top and bottom of the page ([Фан-клуб], [Пародии], [Щ-1]) that leads to the parent page: the "address" is a path from the site root without a leading slash (`fans/index.html`), the "title" is the link text. Empty — the section's own table of contents; set it only when the parent is another page (as on the Щ-1 table of contents, which leads to «Фан-клуб»). Entries are selected by address, so the redirects from old addresses live deeper, in `content/redirects/legacy/`, and are not listed.
- Albums, cassettes, books, cycles and the tour archive (`Disks`, `Tapes`, `Books`, `Cycles`, `Archive`) — also one collection with a folder tree: title, address, page type (album, cassette, book, cycle, tour page, tables of contents), under the parameters the Directus record id and subtitle, search engine fields, date and body. The data (tracks, covers, imprint) come from Directus by `params.id`, so the page type and id of existing pages must not be changed.
- Showcase pages — simple article pages in the site root outside the fan club («Что такое таблатуры», «Статистика» and new ones): title, address (`/imya.html`), author, subtitle, "back" link (empty — the home page), monospace `<pre>`, search engine fields, date and body.
- Picture pages in `content/Images` (`images-page` layout): title, subtitle, "back" link, background colour, centred text and body (HTML). The redirects from old addresses in `content/Images/redirects` are not listed. Pictures themselves live in `static/Images` and are referred to by file name; the editor's insert-image button writes an address from the domain root (`/Images/…`), which does not open on github.io (site in the `/shcherbakov/` subfolder), so type the file name by hand.
- The body of every page except songs and translations (articles, site and language pages, albums and books, picture pages) is a Markdown field in source-only mode: the same HTML is edited as text, and the preview renders it (without the site's styles; scripts and iframes are stripped). Sveltia resolves relative addresses in the preview against the domain root only, so a script in `static/admin/index.html` sets the preview's base to the page's own folder on the site (the site root for the home page, `fans/` for a fan-club article, `Disks/` for an album): pictures and links show as on the site.
- «Порядок меню» — all six site menus (`config/_default/menus.json`): entries are dragged by the handle or moved with the arrows, and the order on the site follows the list. A child entry (a language, a «Фан-клуб» section) goes right after its section and is marked «— подпункт» in the list. An entry has a label, a page (file under `content`), a section code and "belongs to section" for children, and under «Оформление» the mobile label, icon and the rest (see "Menus"). A new page is not in the menu until it is added here.
- For search engines, on site pages, language pages, articles and picture pages: "Search engine title" (`params.seoTitle`) and "Search engine description" (`description`), both optional; see [docs/frontmatter.md](docs/frontmatter.md).
- The «Дата» field (`lastmod`) — on site pages, articles, albums and books, picture pages; on song texts and translations it is «Дата публикации». It does not change by itself on saving: update it by hand when an edit is worth it. The «Today» button next to it puts today's date; it is not filled in automatically, not even on a new page (otherwise an old article would get it on any edit). It drives the date in the menu (see "Menus"): the page a menu entry leads to has the «Показывать дату в меню» checkbox and «Откуда дата для меню» under its parameters.

Other front matter keys are kept as they are, but the editor writes the keys it does not know in alphabetical order and indents JSON with 4 spaces. All editable collections except songs and translations (articles, albums and books, picture pages, site pages and language pages) were brought to this layout in advance, so editing a page does not rewrite its whole front matter in the diff. `scripts/sveltia-normalize.py <collection>` does that — by hand, once, when a collection is added or its fields change; for folder (also nested and filtered) and file-list collections alike, and `--check` lists the files that differ; run it again if the fields of these collections in `config.yml` change.

### New entries

- Songs and translations cannot be created, deleted or renamed in the editor, because a file name is the record's id in Directus. A new song or translation is created in Directus; a Directus Flow then commits an empty file for its text (see [docs/directus.md](docs/directus.md)), and after a reload the entry shows up in the editor.
- A new page — the «+» button at the top of the editor (or «New» in a collection's list): first the kind is chosen — «Страница витрины», «Рецензия», «Статья фан-клуба», «Диск, книга, гастроли», «Страница картинок» — then its form is filled in. The file name is typed in Latin letters. New sections (folders) are not created in the editor: that is a decision about the site's structure, made by the developer. Nor are new page kinds (templates): that is code; a kind added by the developer appears in the list of kinds.
  - For a fan-club article and for an album, book or tour page the section folder is set by the "Parent Folder" field (the folder open in the list is filled in), and the address goes into the «Адрес» field — the same section and name: `/fans/imya.html`, `/Disks/imya.html`. A showcase page's address is `/imya.html`. Without it the page would not show in the list: these collections select entries by address.
  - An album, cassette, book or cycle also needs the page type and the Directus record id: the Directus record comes first, then the page. A review needs no address: `Praises/<name>.html`.
  - The editor fills `type` and `layout` (except the album/book page type) itself; the "back" link defaults to the section's table of contents, on a showcase page to the home page.
  - A new page does not get into the menu by itself: the entry is added in «Порядок меню». A new article also needs a link from its section's list: the list of reviews (under site pages) or its section's table of contents.
- Articles cannot be renamed or deleted in the editor (the file name is typed only when an article is created), because other pages link to them. Delete them with git and run `check-links.py`.

### Saving

- A click on "Save" opens a small confirmation box under the button: Enter or "Save" confirms, Escape or "Cancel" goes back. Ctrl+S (Cmd+S) saves at once, without the box.
- After saving, the editor stays open on the entry. This is the editor's own setting "Close the editor after saving a draft"; the page turns it off once for everyone (also where Sveltia had already stored "close"), and after that respects the choice: it can be switched back in the editor's settings.
- Both are done by a script in `static/admin/index.html` that runs before the editor loads. It recognises the button by its label on the editor toolbar, so a future editor version may need it adjusted.

### The text field

- Songs and translations are edited as plain text, so spaces, indentation and chords stay exactly as typed. Other pages have a Markdown field in source-only mode (see "What can be edited"): it is edited like text and saved unchanged, while the preview renders Markdown and HTML; Hugo shortcodes (`{{< … >}}`) stay as text in the preview.
- For songs and translations the field uses a monospace font with its own Cyrillic (PT Mono), does not wrap lines and takes the full width of the pane, because chords are aligned with spaces. With a font that lacks Cyrillic, the browser takes the letters from another font, and the chords drift. For other pages long lines wrap like paragraphs. A script on the page picks the mode from the collection in the address.
- The preview of songs and translations shows the text as the "source" view of a song page does: in `<pre>`, in the browser's default monospace font (the same as on the site). Song parameters are not shown there.
- A badge in the corner shows the line and character under the cursor, both counted from 1: the same numbers as `textFinishAtLine` and `chordsStartAt`.
- The editor puts a blank line after the front matter and writes a file with empty front matter without one. `layouts/partials/song.html` ignores blank lines before the text, so the line number in `textFinishAtLine` is not shifted.

# Links

The current development version of the project, published automatically by GitHub Actions (see `.github/workflows/static.yml`), is on GitHub Pages:

- <https://zlochevsky.github.io/shcherbakov/>

About Mikhail Shcherbakov:

- <https://deniskhin.ru/scherbakov> — the original version of the website;
- <https://deniskhin.ru/scherbakov/English/index.html> — the website's English page.

About the website's creator:

- <https://blackalpinist.com/> — a collection of mountaineering resources for the Russian-speaking communities of North America;
- <https://blackalpinist.com/~mi/orizaba/release_e.html> — the press release of 28 December 1999 on the death of Vladimir Smirnov and his companions (in English).
