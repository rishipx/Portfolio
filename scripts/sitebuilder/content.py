"""Loading and validating everything under content/ (site details, projects, posts)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Optional

from . import markdown
from .config import COVER_EXTENSIONS, KINDS, Config
from .diagnostics import Report

SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
SITE_FIELDS = ("name", "heading", "role", "tagline", "description", "email", "github", "location")


@dataclass
class Item:
    """A project or post, ready to render."""
    slug: str
    section: str            # content folder: "projects" or "posts"
    meta: dict
    source: Path
    cover: str              # site-relative URL of the cover image
    body: str               # README rendered to HTML
    is_post: bool
    published: Optional[date] = None

    @property
    def order_key(self) -> tuple:
        order = self.meta.get("order")
        has_order = isinstance(order, (int, float)) and not isinstance(order, bool)
        return (
            0 if has_order else 1,
            order if has_order else 0,
            1 if self.is_post else 0,
            -(self.published.toordinal() if self.published else 0),
            self.meta["title"].lower(),
        )


class TechRegistry:
    """Maps technology names (and aliases) to the icons in src/data/tech.json."""

    def __init__(self, entries: dict[str, dict]) -> None:
        self.entries = entries
        self._index: dict[str, str] = {}
        for key, entry in entries.items():
            self._index[key.lower()] = key
            for alias in entry.get("aliases", []):
                self._index[alias.lower()] = key

    def resolve(self, name: Any) -> Optional[str]:
        return self._index.get(str(name).strip().lower())


def read_json(path: Path, label: str, report: Report) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.error("%s: missing file %s" % (label, path.name))
    except ValueError as exc:
        report.error("%s: invalid JSON in %s (%s)" % (label, path.name, exc))
    return None


def load_tech(cfg: Config, report: Report) -> TechRegistry:
    entries = read_json(cfg.src_dir / "data" / "tech.json", "src/data/tech.json", report)
    return TechRegistry(entries or {})


def load_site(cfg: Config, report: Report) -> dict:
    site = read_json(cfg.content_dir / "site.json", "site.json", report) or {}
    for field in SITE_FIELDS:
        if not str(site.get(field, "")).strip():
            report.error("site.json: missing %s" % field)
    return site


def _find_cover(folder: Path) -> Optional[Path]:
    for path in sorted(folder.iterdir()):
        if path.stem == "cover" and path.suffix[1:].lower() in COVER_EXTENSIONS:
            return path
    return None


def _load_item(folder: Path, section: str, meta_file: str, is_post: bool, report: Report) -> Optional[Item]:
    label = "%s/%s" % (section, folder.name)
    if not SLUG.fullmatch(folder.name):
        report.error("%s: folder names may only use lowercase letters, digits and hyphens" % label)
        return None
    meta = read_json(folder / meta_file, label, report)
    if not isinstance(meta, dict) or meta.get("draft"):
        return None

    required = ["title", "summary"] + (["kind", "date"] if is_post else ["kicker"])
    missing = [key for key in required if not str(meta.get(key, "")).strip()]
    if missing:
        report.error("%s/%s: missing required field(s): %s" % (label, meta_file, ", ".join(missing)))
        return None

    published = None
    if is_post:
        if meta["kind"] not in KINDS:
            report.error('%s: "kind" must be one of: %s' % (label, ", ".join(KINDS)))
            return None
        try:
            published = date.fromisoformat(str(meta["date"]))
        except ValueError:
            report.error('%s: "date" must look like 2026-09-18' % label)
            return None

    valid = True
    for key in ("website", "source"):
        if meta.get(key) and not re.match(r"(?i)^https?://", str(meta[key])):
            report.error('%s: "%s" must start with http:// or https://' % (label, key))
            valid = False
    if not isinstance(meta.get("stack", []), list) or not isinstance(meta.get("icons", []), list):
        report.error('%s: "stack" and "icons" must be lists' % label)
        valid = False
    cover = _find_cover(folder)
    if cover is None:
        report.error("%s: add a cover image named cover.png (or .jpg / .webp / .svg)" % label)
        valid = False
    if not valid:
        return None

    asset_base = "assets/%s/%s/" % (section, folder.name)
    readme = folder / "README.md"
    return Item(
        slug=folder.name, section=section, meta=meta, source=folder, is_post=is_post,
        published=published, cover=asset_base + cover.name,
        body=markdown.to_html(readme.read_text(encoding="utf-8"), asset_base) if readme.exists() else "",
    )


def load_items(cfg: Config, report: Report) -> list[Item]:
    """Load projects and posts, check for duplicate slugs, and return them in display order."""
    items: list[Item] = []
    for section, meta_file, is_post in (("projects", "project.json", False), ("posts", "post.json", True)):
        root = cfg.content_dir / section
        if not root.is_dir():
            continue
        for folder in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
            item = _load_item(folder, section, meta_file, is_post, report)
            if item:
                items.append(item)
    slugs = [item.slug for item in items]
    for slug in sorted({s for s in slugs if slugs.count(s) > 1}):
        report.error('"%s" is used by both a project and a post; slugs must be unique' % slug)
    return sorted(items, key=lambda item: item.order_key)
