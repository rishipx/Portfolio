# Architecture

## Build pipeline

`python scripts/build.py` runs `sitebuilder.pipeline.build_site`:

1. Load and validate `content/site.json`, projects and posts (`content.py`). All problems are collected and reported together.
2. Convert each `README.md` to HTML (`markdown.py`).
3. Copy static files, profile files and each item's assets into `_site/assets/`.
4. Bundle `src/styles/*.css` and `src/scripts/*.js`, minify the CSS and name each bundle after its content hash (`assets.py`).
5. Render `src/templates/` with generated fragments for the stats, experience, skills and project cards (`fragments.py`).
6. Write `robots.txt`, `_headers` and, when indexable, `sitemap.xml` (`seo.py`).

| Module | Responsibility |
|---|---|
| `config.py` | Settings from environment variables |
| `content.py` | Loading, validating and ordering content |
| `markdown.py` | Markdown to HTML |
| `fragments.py` | HTML generated from content |
| `templating.py` | `{{token}}` substitution |
| `assets.py` | CSS and JavaScript bundling and fingerprinting |
| `seo.py` | Crawler rules and HTTP headers |
| `pipeline.py` | Orchestration |
| `cli.py` | Command-line interface |

## Front end

- **CSS** is split into numbered files that are concatenated in filename order, so the cascade is explicit. Add a
  file with the right number instead of appending to an unrelated one.
- **JavaScript** modules in `src/scripts/` each run in their own scope. The generated project data (`projectDetails`)
  is prepended to the bundle.
- **No framework, no runtime dependencies.** Fonts load from Google Fonts and most technology icons from CDNs.

## Naming conventions

- Classes follow `component`, `component-part`, for example `project-card`, `project-card-thumb`.
- State classes use an `is-` prefix: `is-open`, `is-expanded`.
- Theme variables live in `src/styles/01-tokens.css`. Dark mode is selected with `[data-theme="dark"]`.
- Dark is the default theme. A saved choice (`localStorage`) overrides it.

## Caching and performance

- CSS and JavaScript file names contain a content hash and are served with `Cache-Control: immutable` on hosts that
  read `_headers`.
- Images use `loading="lazy"`; covers are stored as lossless WebP.
- The theme is applied before first paint by a small inline script, so there is no flash.

## Tests

`python -m unittest discover -s tests` covers the Markdown converter, content validation and ordering, and full builds
(including the shipped example content). CI runs the same checks plus a syntax check of the generated bundle.
