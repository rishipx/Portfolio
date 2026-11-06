"""Minimal {{token}} templating."""
from __future__ import annotations

import re
from typing import Mapping

from .diagnostics import Report

TOKEN = re.compile(r"\{\{(\w+)\}\}")


def render(template: str, context: Mapping[str, object], label: str, report: Report) -> str:
    """Replace {{tokens}}; tokens missing from the context are reported as errors."""
    missing = sorted(set(TOKEN.findall(template)) - set(context))
    if missing:
        report.error("%s: unknown template tokens: %s" % (label, ", ".join(missing)))
    return TOKEN.sub(lambda m: str(context.get(m.group(1), m.group(0))), template)
