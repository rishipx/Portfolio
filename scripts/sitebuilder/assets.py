"""Bundling, minifying and fingerprinting CSS and JavaScript."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path


def minify_css(css: str) -> str:
    """Strip comments and whitespace. String literals are left untouched."""
    strings: list[str] = []

    def keep(match: re.Match) -> str:
        strings.append(match.group(0))
        return "\x00%d\x00" % (len(strings) - 1)

    css = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', keep, css)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r"(?<=:)\s+", "", css)
    css = css.replace(";}", "}")
    return re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], css).strip()


def bundle_css(styles_dir: Path) -> str:
    """Concatenate src/styles/*.css in filename order, then minify."""
    return minify_css("\n".join(p.read_text(encoding="utf-8") for p in sorted(styles_dir.glob("*.css"))))


def bundle_js(scripts_dir: Path, data_js: str) -> str:
    """Wrap each src/scripts/*.js module in its own scope, behind the generated project data."""
    modules = []
    for path in sorted(scripts_dir.glob("*.js")):
        lines = [line for line in path.read_text(encoding="utf-8").splitlines()
                 if not line.lstrip().startswith("//")]
        body = re.sub(r"\n{2,}", "\n", "\n".join(lines)).strip()
        modules.append("(function () {\n%s\n})();" % body)
    return "(function () {\n'use strict';\n%s\n%s\n})();\n" % (data_js, "\n".join(modules))


def fingerprint(stem: str, extension: str, content: str) -> str:
    """File name with a content hash, so it can be cached forever: styles.1a2b3c4d5e.css."""
    return "%s.%s.%s" % (stem, hashlib.sha256(content.encode("utf-8")).hexdigest()[:10], extension)
