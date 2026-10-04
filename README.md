[Русская версия](README.ru.md)

# About

This project, built with [HUGO](https://gohugo.io/), static site generator written in [Go](https://go.dev/), develops the layout of website dedicated to the works of Mikhail Shcherbakov, a russian songwriter and performer. The original website was created by Vladimir Smirnov in the mid-1990s at <https://blackalpinist.com/scherbakov/>. The maintained version, serving as the starting point for the project, is available at <https://lambda.mkshch.com/>.

The goal of the project is to create a responsive layout for the website while preserving the original style and content as much as possible, making the website more usable for visitors and convenient for maintenance and support. The following objectives are set:

1. Convert current set of the whole website's pages into HUGO project manually.
2. Update the website's markup to be more friendly to modern browsers and search engines.
3. Make the layout responsive for convenient use on various devices.
4. Improve the overall user experience and interface, while preserving the style and intent of the website's creators. Add functionality, e.g. in the chords pages. Use JavaScript where appropriate.
5. Maintain the simplicity and appearance of the current version: avoid excessive CSS complexity, refrain from overloading the user interface, optimize the graphic elements.

Thus, the website is intended to be developed in a retro, old-fashioned, style, while striving for elegance and usability. I hope that after successfully achieving the set objectives, the website will become easier to develop, and new goals will become possible, such as implementing multilingual support. One such goal, full-text search, is already in place: the site's search page is built with [Pagefind](https://pagefind.app/).

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
- `layouts` -- templates: page layouts in `layouts/miscellaneous`, shared parts in `layouts/partials`;
- `assets` -- files processed during the build: CSS (`assets/css`; all shared colours are CSS variables in `assets/css/palette.css`, embedded into every page by `layouts/partials/palette.html`) and SVG icons (`assets/svg`: album icons for the song catalogue, `svg/cd`, and format icons, `svg/format`);
- `static` -- files copied to the site as they are: images, PDFs, legacy pages that are not converted yet;
- `data`, `archetypes`, `i18n` -- Hugo data files, templates for new pages, translations of interface strings;
- `public` -- where Hugo puts the built site. It is not stored in git: the published site is built by GitHub Actions (see below).

Project directories:

- `docs` -- project documentation (mostly in Russian): the Directus schema and conventions ([docs/directus.md](docs/directus.md)), the front matter reference, the site structure analysis ([docs/site-structure-analysis.md](docs/site-structure-analysis.md)) and plans for migrating legacy sections;
- `scripts` -- Python tools: `check-links.py` (links to pages that do not exist yet), `check-separation.py` (see "Two sites in one" below), `legacy-convert` (converting legacy pages to Hugo content);
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

