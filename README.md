# About

This project, built with [HUGO](https://gohugo.io/), static site generator written in [Go](https://go.dev/), develops the layout of website dedicated to the works of Mikhail Shcherbakov, a russian songwriter and performer. The original website was created by Vladimir Smirnov in the mid-1990s at <https://blackalpinist.com/scherbakov/>. The maintained version, serving as the starting point for the project, is available at <https://lambda.mkshch.com/>.

The goal of the project is to create a responsive layout for the website while preserving the original style and content as much as possible, making the website more usable for visitors and convenient for maintenance and support. The following objectives are set:

1. Convert current set of the whole website's pages into HUGO project manually.
2. Update the website's markup to be more friendly to modern browsers and seach engines.
3. Make the layout responsive for convenient use on various devices.
4. Improve the overall user experience and interface, while preserving the style and intent of the website's creators as much as possible.
5. Maintain the simplicity and appearance of the current version: avoid excessive CSS complexity, refrain from overloading the user interface, optimize the graphic elements, and, where possible, avoid using JavaScript on pages.

Thus, the website is intended to be developed in a retro, old-fashioned, style, while striving for elegance and usability. I hope that after successfully achieving the set objectives, the website will become easier to develop, and new goals will become possible, such as integrating a full-text search mechanism and implementing multilingual support.

Specific implementation aspects, e.g. integration with the studio records store or changing the russian character encoding, are intentionally not considered here, as they are deemed not significant enough for the main readme file.

Currently, the website is created and maintained by a small Russian-speaking community, which explains why the vast majority of the pages are in Russian. Unfortunately, this circumstance makes it more difficult to attract new people and resources to the project, but at the same time, it gives hope that the website will be cared for by individuals who are passionate about both the work and person of Mikhail Shcherbakov and the memory of the website's creator, Vladimir Smirnov.

The website is created and maintained by people not affiliated with the author, Mikhail Shcherbakov, although some of them know him personally. Moreover, a significant portion of the content is not approved by the author. Therefore, the website will remain inofficial in the foreseeable future. Nevertheless, it continues to be, as it has been for the past decades, the most complete collection of the author's texts on the internet, as well as materials dedicated to him.

# Structure

Main configuration file is hugo.json in the root directory. All the directories in the root, except the `workfiles` directory, are standard Hugo project directories:

- archetypes -- contains so called *archetypes* -- small template files, that configure Hugo's behaviour while creating new pages with no content yet;
- content -- directory, where all the content files are placed by Hugo and to be placed by developer/editor. These are .md files in *markdown* format, which contain the html markup as well, with the main page content. Hugo converts them to the .html pages on the build stage. At the top of each .md file there is so called *front matter* -- set of page parameters, stored in JSON (or TOML/YAML) format;
- public -- the directory, where Hugo places all the ready-to-upload site, built with all the static stuff.
- themes -- contains subdirectories with the site *themes*. Each theme is a site layout, that contains templates files. The project develops `blackalpinist` theme for the site. In theory, it is possible to create an alternative design for the site with another theme.
- workfiles -- contains files, used for creating current theme and content: images, song catalogue table etc.

# Installation

The project requires:

- <https://git-scm.com/> Git client to work with this repository;
- <https://go.dev/dl/> Go installed on your machine;
- <https://gohugo.io/> Hugo Extended Edition installed on your machine. Follow the intructions in the installation manual: https://gohugo.io/installation/


# Links

Current development build of the project (literrally its `public` directory) is viewable on our GitHub Pages:

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

