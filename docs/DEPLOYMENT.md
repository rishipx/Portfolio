# Deployment

The build produces a static site in `_site/`. Deployment differs only in a few environment variables.

## Settings

| Variable | Default | Purpose |
|---|---|---|
| `SITE_URL` | GitHub Pages placeholder | Public URL. Used for canonical and Open Graph URLs and the 404 base path |
| `NOINDEX` | `true` | `true`: `noindex` meta tags, `X-Robots-Tag` header and `Disallow: /`. `false`: indexable, with a sitemap |
| `BASE_PATH` | derived from `SITE_URL` | Only set this when the path cannot be derived |
| `CONTENT_DIR` | `content` | Use a different content folder |
| `OUTPUT_DIR` | `_site` | Use a different output folder |

AI crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended, PerplexityBot and others) stay blocked in `robots.txt` in both modes.

## GitHub Pages

1. Push the repository to GitHub (default branch `main`).
2. Go to **Settings > Pages > Build and deployment > Source** and choose **GitHub Actions**.
3. The `Deploy to GitHub Pages` workflow builds the site and publishes it. `SITE_URL` is set automatically.

To allow search indexing, add a repository variable `NOINDEX` with the value `false`
(**Settings > Secrets and variables > Actions > Variables**).

## Cloudflare Pages

Create a project from your repository with:

- Build command: `python3 scripts/build.py`
- Build output directory: `_site`
- Environment variables: `SITE_URL=https://your-domain.com`, and `NOINDEX=false` when you want to be found

Cloudflare reads the generated `_headers` file, so `X-Robots-Tag` also covers the PDF and images, and the fingerprinted
CSS and JavaScript are cached for a year.

## Custom domain

Set `SITE_URL` to the final URL. On a domain root, the base path becomes `/` and the 404 page uses it automatically.

## Keep your real content private

All personal data lives in `content/`, so the public repository can stay a template while a private fork holds your
content. Pull template updates from the public repository; conflicts stay inside `content/`.

## Privacy note

`noindex` and `robots.txt` are requests that well-behaved crawlers honour. They are not access control: anyone with the
link can open the site. Because `robots.txt` blocks crawling, search engines cannot read the `noindex` tag, so an
external link may still surface the bare URL, though never the content.

## Releases

Versions follow semantic versioning and the current version is in the `VERSION` file. Tag a release with
`git tag v1.0.0 && git push --tags`.
