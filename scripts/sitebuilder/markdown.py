"""A small Markdown-to-HTML converter for project READMEs.

Supports headings, paragraphs, lists, quotes, code fences, rules, links, images and
bold / italic / inline code. An image on its own line becomes a figure whose optional
"title" is rendered as a caption.
"""
from __future__ import annotations

import html
import posixpath
import re

IMAGE = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)'
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+\.)\s+(.*)$")


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def safe_url(url: str) -> str:
    url = url.strip()
    return "#" if re.match(r"(?i)^(javascript|data|vbscript):", url) else url


def resolve_url(url: str, base: str) -> str:
    """Make relative URLs point at the project's copied asset folder."""
    url = safe_url(url)
    if re.match(r"^([a-z][a-z0-9+.-]*:|//|/|#)", url, re.I):
        return url
    return base + posixpath.normpath(url)


def _image(alt: str, url: str, base: str) -> str:
    return '<img class="dialog-preview" src="%s" alt="%s" loading="lazy">' % (
        _esc(resolve_url(html.unescape(url), base)), _esc(html.unescape(alt)))


def _inline(text: str, base: str) -> str:
    codes: list[str] = []

    def stash(match: re.Match) -> str:
        codes.append(match.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(IMAGE, lambda m: _image(m.group(1), m.group(2), base), text)

    def link(match: re.Match) -> str:
        url = html.unescape(match.group(2))
        external = ' target="_blank" rel="noopener noreferrer"' if re.match(r"(?i)^https?://", url) else ""
        return '<a href="%s"%s>%s</a>' % (_esc(safe_url(url)), external, match.group(1))

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00",
                  lambda m: "<code>%s</code>" % html.escape(codes[int(m.group(1))], quote=False), text)


def to_html(source: str, base: str) -> str:
    """Convert Markdown to HTML. `base` prefixes relative image and link paths."""
    lines = source.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph)
        paragraph.clear()
        figure = re.fullmatch(IMAGE, html.escape(text, quote=False))
        if figure:
            out.append(_image(figure.group(1), figure.group(2), base))
            if figure.group(3):
                out.append('<p class="dialog-image-note">%s</p>' % figure.group(3))
        else:
            out.append("<p>%s</p>" % _inline(text, base))

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code), quote=False))
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            level = 3 if len(heading.group(1)) <= 3 else 4
            out.append('<h%d class="md-heading">%s</h%d>' % (level, _inline(heading.group(2), base), level))
        elif re.fullmatch(r"\s*([-*_])(\s*\1){2,}\s*", line):
            flush()
            out.append("<hr>")
        elif LIST_ITEM.match(line):
            flush()
            ordered = LIST_ITEM.match(line).group(1)[0].isdigit()
            items: list[str] = []
            while i < len(lines) and LIST_ITEM.match(lines[i]):
                items.append("<li>%s</li>" % _inline(LIST_ITEM.match(lines[i]).group(2), base))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(items), tag))
            continue
        elif line.startswith(">"):
            flush()
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % _inline(" ".join(quote), base))
            continue
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
        i += 1
    flush()
    return "".join(out)
