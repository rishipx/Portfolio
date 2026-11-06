"""HTML fragments generated from content: cards, stats, experience and skills."""
from __future__ import annotations

import html
import json

from .config import KINDS
from .content import Item, TechRegistry
from .diagnostics import Report
from .templating import render


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def project_card(item: Item, tech: TechRegistry, partials: dict, report: Report) -> str:
    meta = item.meta
    if item.is_post:
        label = meta.get("tag") or KINDS[meta["kind"]]
        left = '<div class="project-card-tags"><span class="post-tag">%s</span></div>' % esc(label)
    else:
        keys: list[str] = []
        for name in meta.get("icons") or meta.get("stack", []):
            key = tech.resolve(name)
            if key and key not in keys and tech.entries[key].get("icon"):
                keys.append(key)
        left = ""
        if keys:
            left = '<div class="tech-icon-group">%s</div>' % "".join(
                '<span class="tech-icon-wrap" data-tooltip="%s"><img src="%s" alt="%s"></span>'
                % (esc(key), esc(tech.entries[key]["icon"]), esc(key)) for key in keys)

    actions = "".join(
        render(partials[partial], {"url": esc(meta[field])}, "partial " + partial, report)
        for field, partial in (("website", "action-website"), ("source", "action-source")) if meta.get(field))
    group = '<div class="project-card-actions">%s</div>' % actions if actions else ""
    footer = '<div class="project-card-footer">%s%s</div>' % (left, group) if (left or group) else ""

    return (
        '<article class="project-card" data-project="%s" tabindex="0" role="button">'
        '<div class="project-card-thumb"><img src="%s" alt="%s preview" loading="lazy" decoding="async"></div>'
        "<h3>%s</h3><p>%s</p>%s</article>"
    ) % (esc(item.slug), esc(item.cover), esc(meta["title"]), esc(meta["title"]), esc(meta["summary"]), footer)


def project_details_js(items: list[Item]) -> str:
    """The data the project dialog reads when a card is opened."""
    details = {
        item.slug: {
            "kicker": item.meta.get("kicker") or KINDS.get(item.meta.get("kind"), ""),
            "title": item.meta["title"],
            "stack": [str(entry) for entry in item.meta.get("stack", [])],
            "website": item.meta.get("website", ""),
            "source": item.meta.get("source", ""),
            "readme": item.body,
        }
        for item in items
    }
    return "const projectDetails = %s;" % json.dumps(details, ensure_ascii=False, separators=(",", ":"))


def stats(entries: list[dict]) -> str:
    return "\n".join(
        '<div class="stat"><div class="stat-value">%s</div><div class="stat-label">%s</div></div>'
        % (esc(entry.get("value", "")), esc(entry.get("label", ""))) for entry in entries)


def experience(entries: list[dict], label: str, report: Report) -> str:
    out = []
    for entry in entries:
        missing = [key for key in ("initials", "org", "dates", "role") if not entry.get(key)]
        if missing:
            report.error("site.json %s entry missing: %s" % (label, ", ".join(missing)))
            continue
        bullets = "".join("<li>%s</li>" % esc(bullet) for bullet in entry.get("bullets", []))
        out.append(
            '<div class="experience-item"><div class="experience-avatar">%s</div><div class="experience-body">'
            '<div class="experience-row"><h3 class="experience-org">%s</h3><span class="experience-date">%s</span></div>'
            '<div class="experience-role">%s</div><ul class="experience-bullets">%s</ul></div></div>'
            % (esc(entry["initials"]), esc(entry["org"]), esc(entry["dates"]), esc(entry["role"]), bullets))
    return "\n".join(out)


def skills(groups: list[list[str]], tech: TechRegistry, report: Report) -> str:
    blocks = []
    for group in groups:
        lines = []
        for name in group:
            key = tech.resolve(name)
            entry = tech.entries.get(key, {}) if key else {}
            if entry.get("html"):
                icon = entry["html"]
            elif entry.get("icon"):
                icon = '<span class="skill-icon"><img src="%s" alt="%s" width="18" height="18"></span>' % (
                    esc(entry["icon"]), esc(name))
            else:
                icon = ""
                report.warn('no icon for skill "%s" (add it to src/data/tech.json)' % name)
            lines.append('<div class="skill-item">%s<span>%s</span></div>' % (icon, esc(name)))
        blocks.append('<div class="skill-group">%s</div>' % "\n".join(lines))
    return "\n".join(blocks)
