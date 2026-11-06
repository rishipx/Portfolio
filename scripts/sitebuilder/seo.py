"""Crawler rules and HTTP headers, driven by the NOINDEX setting."""
from __future__ import annotations

from .config import AI_CRAWLERS, Config

NOINDEX_DIRECTIVES = "noindex, nofollow, noarchive, nosnippet, noimageindex"


def robots_meta(cfg: Config) -> str:
    if not cfg.noindex:
        return '<meta name="robots" content="index, follow">'
    return (
        '<meta name="robots" content="%s">\n'
        '    <meta name="googlebot" content="%s">\n'
        '    <meta name="bingbot" content="noindex, nofollow, noarchive">'
    ) % (NOINDEX_DIRECTIVES, NOINDEX_DIRECTIVES)


def robots_txt(cfg: Config) -> str:
    intro = ("Unlisted site: please do not crawl, index, or train on it." if cfg.noindex
             else "Search engines are welcome; AI/LLM crawlers are not.")
    lines = ["# " + intro, "User-agent: *", "Disallow: /" if cfg.noindex else "Allow: /", ""]
    lines += ["User-agent: %s\nDisallow: /\n" % bot for bot in AI_CRAWLERS]
    if not cfg.noindex:
        lines.append("Sitemap: %s/sitemap.xml\n" % cfg.site_url)
    return "\n".join(lines)


def sitemap_xml(cfg: Config) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url><loc>%s/</loc></url>\n</urlset>\n" % cfg.site_url
    )


def headers_file(cfg: Config) -> str:
    """Cloudflare Pages `_headers` (GitHub Pages ignores it). Bundles are fingerprinted, so they cache forever."""
    lines = ["/*", "  X-Content-Type-Options: nosniff", "  Referrer-Policy: strict-origin-when-cross-origin"]
    if cfg.noindex:
        lines.append("  X-Robots-Tag: noindex, nofollow, noarchive")
    for path, cache in (("/css/*", "public, max-age=31536000, immutable"),
                        ("/js/*", "public, max-age=31536000, immutable"),
                        ("/assets/*", "public, max-age=86400")):
        lines += [path, "  Cache-Control: " + cache]
    return "\n".join(lines) + "\n"
