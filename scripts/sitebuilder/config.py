"""Build configuration, read from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional
from urllib.parse import urlparse

DEFAULT_SITE_URL = "https://your-username.github.io/portfolio"

# Post kinds and the label shown on their card.
KINDS = {"case-study": "Case Study", "guide": "Guide", "write-up": "Write-up"}

COVER_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "gif", "svg", "avif")

AI_CRAWLERS = (
    "GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-Web", "anthropic-ai", "CCBot",
    "Google-Extended", "PerplexityBot", "Bytespider", "Amazonbot", "Applebot-Extended", "cohere-ai",
    "Meta-ExternalAgent", "FacebookBot", "Diffbot", "ImagesiftBot", "Omgilibot",
)


@dataclass(frozen=True)
class Config:
    root: Path
    site_url: str
    noindex: bool
    base_path: str
    content_dir: Path
    out_dir: Path
    version: str

    @property
    def src_dir(self) -> Path:
        return self.root / "src"

    @classmethod
    def from_env(cls, root: Path, env: Optional[Mapping[str, str]] = None) -> "Config":
        env = os.environ if env is None else env
        site_url = env.get("SITE_URL", DEFAULT_SITE_URL).strip().rstrip("/")
        base_path = env.get("BASE_PATH") or (urlparse(site_url).path.rstrip("/") + "/")
        if not base_path.endswith("/"):
            base_path += "/"
        version_file = root / "VERSION"
        return cls(
            root=root,
            site_url=site_url,
            noindex=env.get("NOINDEX", "true").strip().lower() not in ("0", "false", "no", "off"),
            base_path=base_path,
            content_dir=root / env.get("CONTENT_DIR", "content"),
            out_dir=root / env.get("OUTPUT_DIR", "_site"),
            version=version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.0.0",
        )
