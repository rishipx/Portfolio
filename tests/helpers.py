"""Shared test fixtures: a minimal content folder written to a temporary directory."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SITE = {
    "name": "Test Person", "heading": "Hi, I'm Test.", "role": "Engineer", "tagline": "Builds things.",
    "description": "A test site.", "email": "test@example.com", "github": "https://github.com/test",
    "location": "Remote", "stats": [{"value": "1", "label": "Thing"}],
    "work": [{"initials": "AB", "org": "Org", "dates": "2024", "role": "Dev", "bullets": ["Did it."]}],
    "education": [], "skills": [["Python"]],
}
COVER = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 3"><rect width="4" height="3"/></svg>'


def write_item(content: Path, section: str, slug: str, meta: dict, readme: str = "Hello.\n", cover: bool = True) -> None:
    folder = content / section / slug
    folder.mkdir(parents=True)
    (folder / ("post.json" if section == "posts" else "project.json")).write_text(json.dumps(meta), encoding="utf-8")
    (folder / "README.md").write_text(readme, encoding="utf-8")
    if cover:
        (folder / "cover.svg").write_text(COVER, encoding="utf-8")


def write_content(content: Path, site: dict = SITE) -> None:
    (content / "profile").mkdir(parents=True)
    (content / "site.json").write_text(json.dumps(site), encoding="utf-8")
    for name in ("resume.pdf", "og-image.png", "favicon.svg"):
        (content / "profile" / name).write_bytes(b"x")


def project(title: str = "Alpha", **extra) -> dict:
    return {"title": title, "kicker": "Tool", "summary": "A summary.", **extra}


def post(title: str = "Beta", **extra) -> dict:
    return {"title": title, "kind": "guide", "summary": "A summary.", "date": "2026-01-01", **extra}
