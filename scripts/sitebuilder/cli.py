"""Command-line interface."""
from __future__ import annotations

import argparse
import functools
import http.server
import sys
from pathlib import Path

from .config import Config
from .pipeline import build_site


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the portfolio site.")
    parser.add_argument("--serve", action="store_true", help="serve the built site locally after building")
    parser.add_argument("--port", type=int, default=8000, help="port for --serve (default: 8000)")
    args = parser.parse_args(argv)

    cfg = Config.from_env(Path(__file__).resolve().parents[2])
    report = build_site(cfg)

    print("portfolio v%s" % cfg.version)
    for note in report.notes:
        print(note)
    for warning in report.warnings:
        print("warning: " + warning)
    if not report.ok:
        print("\nBuild failed:")
        for error in report.errors:
            print("  - " + error)
        sys.exit(1)

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(cfg.out_dir))
        with http.server.ThreadingHTTPServer(("", args.port), handler) as server:
            print("Serving http://localhost:%d  (Ctrl+C to stop)" % args.port)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
