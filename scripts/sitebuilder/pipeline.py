"""The build: content + templates + assets -> a static site in the output folder."""
from __future__ import annotations

import shutil
from pathlib import Path

from . import assets, fragments, seo
from .config import DEFAULT_SITE_URL, Config
from .content import load_items, load_site, load_tech
from .diagnostics import Report
from .templating import render

PROFILE_FILES = ("resume.pdf", "og-image.png", "favicon.svg")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_site(cfg: Config) -> Report:
    report = Report()
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True)

    tech = load_tech(cfg, report)
    site = load_site(cfg, report)
    items = load_items(cfg, report)
    templates = cfg.src_dir / "templates"
    partials = {path.stem: path.read_text(encoding="utf-8") for path in (templates / "partials").glob("*.html")}
    if not report.ok:
        return report

    # Static files, profile files and each project's own assets
    shutil.copytree(cfg.src_dir / "static", cfg.out_dir / "assets", dirs_exist_ok=True)
    for name in PROFILE_FILES:
        source = cfg.content_dir / "profile" / name
        if source.exists():
            shutil.copy(source, cfg.out_dir / "assets" / name)
        else:
            report.warn("content/profile/%s not found" % name)
    for item in items:
        shutil.copytree(item.source, cfg.out_dir / "assets" / item.section / item.slug,
                        ignore=shutil.ignore_patterns("project.json", "post.json", "README.md"))

    # Fingerprinted bundles
    css = assets.bundle_css(cfg.src_dir / "styles")
    js = assets.bundle_js(cfg.src_dir / "scripts", fragments.project_details_js(items))
    css_name = assets.fingerprint("styles", "css", css)
    js_name = assets.fingerprint("app", "js", js)
    _write(cfg.out_dir / "css" / css_name, css)
    _write(cfg.out_dir / "js" / js_name, js)

    # Pages
    context = {key: fragments.esc(site.get(key, "")) for key in
               ("name", "heading", "role", "tagline", "description", "email", "github", "location")}
    context.update({
        "page_title": fragments.esc("%s | %s" % (site.get("name", ""), site.get("role", ""))),
        "projects_title": fragments.esc(site.get("projects_title", "Featured projects")),
        "site_url": fragments.esc(cfg.site_url),
        "base_path": fragments.esc(cfg.base_path),
        "robots_meta": seo.robots_meta(cfg),
        "stylesheet": "./css/" + css_name,
        "script": "./js/" + js_name,
        "stats": fragments.stats(site.get("stats", [])),
        "work": fragments.experience(site.get("work", []), "work", report),
        "education": fragments.experience(site.get("education", []), "education", report),
        "skills": fragments.skills(site.get("skills", []), tech, report),
        "projects_grid": "\n".join(fragments.project_card(item, tech, partials, report) for item in items),
    })
    for page in ("index", "404"):
        template = (templates / (page + ".html")).read_text(encoding="utf-8")
        _write(cfg.out_dir / (page + ".html"), render(template, context, page + ".html", report))

    # Crawler rules and headers
    _write(cfg.out_dir / "robots.txt", seo.robots_txt(cfg))
    _write(cfg.out_dir / "_headers", seo.headers_file(cfg))
    if not cfg.noindex:
        _write(cfg.out_dir / "sitemap.xml", seo.sitemap_xml(cfg))

    posts = sum(1 for item in items if item.is_post)
    report.note("Built %d projects and %d posts into %s" % (len(items) - posts, posts, cfg.out_dir.name))
    report.note("SITE_URL=%s  NOINDEX=%s" % (cfg.site_url, str(cfg.noindex).lower()))
    if cfg.site_url == DEFAULT_SITE_URL:
        report.warn("SITE_URL is still the placeholder; set it for correct canonical and Open Graph URLs")
    return report
