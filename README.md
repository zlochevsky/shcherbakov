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

Hugo's configuration is `hugo.json` in the root directory (site parameters, menus). The Directus access token lives in `config/_default/params.json`, which is not in git: copy `config/_default/params.json.example` to it (see Building below).

Standard Hugo directories:

- `content` -- the pages: `.md` files whose body is mostly HTML markup. At the top of each file there is *front matter* -- page parameters in JSON. The fields the templates actually read are listed in [docs/frontmatter.md](docs/frontmatter.md);
- `layouts` -- templates: page layouts in `layouts/miscellaneous`, shared parts in `layouts/partials`, shortcodes for page bodies in `layouts/shortcodes`. `{{< lastmod "translations" >}}` gives the date of the latest record added to a Directus collection (on the home page). `{{< translations-count >}}` gives the number of translations into the page's language and the date of the latest one, as " (59, 07.10.26)" with the date in red (on the main language pages). Records migrated from the old site have no creation date, so for them only the number is shown;
- `assets` -- files processed during the build: CSS (`assets/css`; all shared colours are CSS variables in `assets/css/palette.css`, embedded into every page by `layouts/partials/palette.html`) and SVG icons (`assets/svg`: album icons for the song catalogue, `svg/cd`, and format icons, `svg/format`);
- `static` -- files copied to the site as they are: images, PDFs, legacy pages that are not converted yet; `static/admin` is the in-browser editor (see "Editing in the browser" below);
- `data`, `archetypes`, `i18n` -- Hugo data files, templates for new pages, translations of interface strings;
- `public` -- where Hugo puts the built site. It is not stored in git: the published site is built by GitHub Actions (see below).

Project directories:

- `docs` -- project documentation (mostly in Russian): the Directus schema and conventions ([docs/directus.md](docs/directus.md)), the front matter reference, the site structure analysis ([docs/site-structure-analysis.md](docs/site-structure-analysis.md)) and plans for migrating legacy sections;
- `scripts` -- Python tools: `check-links.py` (links to pages that do not exist yet), `check-separation.py` (see "Two sites in one" below), `sveltia-normalize.py` (see "Editing in the browser" below), `legacy-convert` (converting legacy pages to Hugo content);
- `directus-extensions` -- sources of some custom Directus extensions;
- `workfiles` -- local working files (images, tables, drafts). The directory is in `.gitignore`.

A part of the site's content (song catalogue, concerts, performances, albums, books, announces) is served from an external Directus database (`db.sch.com.ru`) rather than from files in this repository. To learn how the data is organised:

- [docs/directus.md](docs/directus.md) describes the collections, their relations, automation (Flows) and naming conventions;
- `https://db.sch.com.ru/server/specs/oas` with the public token (see Building) returns the OpenAPI description of exactly the collections and fields that token can read. Open it in any OpenAPI viewer, e.g. Swagger UI;
- the API itself shows real records, e.g. `https://db.sch.com.ru/items/works?limit=5` with the token in the `Authorization: Bearer` header or the `access_token` query parameter.

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
- before each build the workflow archives announces whose expiry date has passed (sets their status in Directus to `archived`);
- the build uses the public read-only Directus token from `params.json.example`, runs Hugo, then Pagefind to make the search index.

## Editing in the browser

`/admin/` on the site is [Sveltia CMS](https://sveltiacms.app/), an editor for files in this repository: `static/admin/index.html` loads it, and `static/admin/config.yml` sets what it edits. It does not change any other page of the site. Each save is a commit to `master` made through the GitHub API, and the usual workflow publishes it. Data kept in Directus (titles, years, albums, translators, announces, comments) is edited in Directus. The "Таблицы Directus" item at the bottom of the editor's left panel opens `/admin/directus.html`: links to the Directus Studio tables, grouped by topic, with descriptions. The groups and descriptions live in `content/admin-directus.md` and are edited in the editor itself ("Страницы сайта"). The item itself is inserted by a script in `static/admin/index.html`, since Sveltia has no custom links in its panel.

### Signing in

- "Sign In with GitHub" works for anyone with write access to the repository. Sign-in goes through an OAuth proxy, `sveltia-cms-auth` on Cloudflare Workers (`https://sveltia-cms-auth.sergey-897.workers.dev`, the `base_url` in `config.yml`):
  - the proxy holds the client ID and secret of the GitHub OAuth App in its variables, plus `ALLOWED_DOMAINS` (the site's host and `localhost`);
  - the OAuth App is registered in the repository owner's GitHub settings, with the callback URL `<proxy>/callback`;
  - the editor asks GitHub for the `public_repo` scope (`auth_scope`), not the default `repo`, which would also reach private repositories.
- "Sign In Using Access Token" takes a GitHub personal access token that each editor makes in their own GitHub settings; the token stays in their browser:
  - the repository owner can use a fine-grained token: Repository access → this repository, Permissions → "Contents: Read and write";
  - a collaborator cannot use a fine-grained token, because such a token reaches only repositories of its own owner or of an organization. A collaborator makes a classic token with the `public_repo` scope instead. It can write to every public repository the collaborator has access to, not only this one.
- On localhost the editor also offers to work with a local copy of the repository. In that mode "Save" writes the file to disk with no commit, and the change is committed with git as usual.

### What can be edited

- Song texts (`content/texts`) and translations (`content/<language>/`): the text, and for songs the tonality, `chordsStartAt` and `textFinishAtLine`.
- Language pages: title and body.
- Site pages: title and body of the home page, biography, about, where to buy, news (the chronicle; announces come from Directus), what is missing, tablature and the list of reviews (`praises.md`); the body of the footer. The home page body is HTML laid out in blocks, so edit it with care: an unclosed tag breaks the home page.
- Fan-club articles in `content/Praises`, `content/Parodies` and `content/fans`: title, author, subtitle and body, for parodies and fan-club materials also the "back" link. Only pages with the `praises-article` layout are listed, so `fans/kom.md` (the comments page built from Directus) and the `kom2` redirect are left out.

Other front matter keys are kept as they are, but the editor writes the keys it does not know in alphabetical order and indents JSON with 4 spaces. The fan-club articles were brought to this layout in advance, so editing one does not rewrite its whole front matter in the diff. `scripts/sveltia-normalize.py <collection>` does that, and `--check` lists the files that differ; run it again if the fields of these collections in `config.yml` change.

### New entries

- Songs and translations cannot be created, deleted or renamed in the editor, because a file name is the record's id in Directus. A new song or translation is created in Directus; a Directus Flow then commits an empty file for its text (see [docs/directus.md](docs/directus.md)), and after a reload the entry shows up in the editor.
- Fan-club articles can be created in their sections. The file name is typed in Latin letters, and the page URL is `<section>/<name>.html`. The editor fills `type` and `layout` itself, and gives parodies and fan-club materials a default "back" link. A new article needs a link in its section's list: the list of reviews (under site pages), or the parody and fan-club tables of contents.
- Articles cannot be renamed or deleted in the editor (the file name is typed only when an article is created), because other pages link to them. Delete them with git and run `check-links.py`.

### Saving

- A click on "Save" opens a small confirmation box under the button: Enter or "Save" confirms, Escape or "Cancel" goes back. Ctrl+S (Cmd+S) saves at once, without the box.
- After saving, the editor stays open on the entry. This is the editor's own setting "Close the editor after saving a draft"; the page turns it off for anyone who has not changed it, and it can be switched back in the editor's settings.
- Both are done by a script in `static/admin/index.html` that runs before the editor loads. It recognises the button by its label on the editor toolbar, so a future editor version may need it adjusted.

### The text field

- Texts are edited as plain text, so spaces, indentation and chords stay exactly as typed.
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

