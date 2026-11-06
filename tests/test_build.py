import re
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT, post, project, write_content, write_item
from sitebuilder.config import Config
from sitebuilder.pipeline import build_site


class BuildTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.content, self.out = self.tmp / "content", self.tmp / "out"
        write_content(self.content)
        write_item(self.content, "projects", "alpha", project("Alpha", source="https://github.com/test/alpha"))
        write_item(self.content, "posts", "beta", post("Beta"))

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, **env):
        settings = {"CONTENT_DIR": str(self.content), "OUTPUT_DIR": str(self.out), **env}
        report = build_site(Config.from_env(ROOT, settings))
        self.assertTrue(report.ok, report.errors)
        return report

    def test_outputs_and_fingerprinted_bundles(self):
        self.build()
        for name in ("index.html", "404.html", "robots.txt", "_headers"):
            self.assertTrue((self.out / name).exists(), name)
        html = (self.out / "index.html").read_text(encoding="utf-8")
        for url in re.findall(r'(?:href|src)="\./((?:css|js)/[^"]+)"', html):
            self.assertTrue((self.out / url).exists(), url)
        self.assertRegex(html, r"css/styles\.[0-9a-f]{10}\.css")
        self.assertRegex(html, r"js/app\.[0-9a-f]{10}\.js")
        self.assertIn('data-project="alpha"', html)
        self.assertNotIn("{{", html)

    def test_local_asset_references_exist(self):
        self.build()
        html = (self.out / "index.html").read_text(encoding="utf-8")
        for url in re.findall(r'src="(assets/[^"]+)"', html):
            self.assertTrue((self.out / url).exists(), url)

    def test_project_data_is_bundled(self):
        self.build()
        bundle = next((self.out / "js").glob("app.*.js")).read_text(encoding="utf-8")
        self.assertIn('"alpha"', bundle)
        self.assertIn("use strict", bundle)

    def test_noindex_default(self):
        self.build()
        self.assertIn("noindex", (self.out / "index.html").read_text(encoding="utf-8"))
        self.assertIn("Disallow: /\n", (self.out / "robots.txt").read_text(encoding="utf-8"))
        self.assertIn("X-Robots-Tag", (self.out / "_headers").read_text(encoding="utf-8"))
        self.assertFalse((self.out / "sitemap.xml").exists())

    def test_indexable_build_keeps_ai_crawlers_blocked(self):
        self.build(NOINDEX="false", SITE_URL="https://me.dev")
        robots = (self.out / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /", robots)
        self.assertIn("User-agent: GPTBot\nDisallow: /", robots)
        self.assertIn("Sitemap: https://me.dev/sitemap.xml", robots)
        self.assertNotIn("X-Robots-Tag", (self.out / "_headers").read_text(encoding="utf-8"))
        self.assertTrue((self.out / "sitemap.xml").exists())

    def test_base_path_comes_from_site_url(self):
        self.build(SITE_URL="https://user.github.io/portfolio")
        self.assertIn('<base href="/portfolio/">', (self.out / "404.html").read_text(encoding="utf-8"))
        self.build(SITE_URL="https://me.dev")
        self.assertIn('<base href="/">', (self.out / "404.html").read_text(encoding="utf-8"))

    def test_invalid_content_fails_the_build(self):
        write_item(self.content, "projects", "broken", {"title": "No summary"})
        report = build_site(Config.from_env(ROOT, {"CONTENT_DIR": str(self.content), "OUTPUT_DIR": str(self.out)}))
        self.assertFalse(report.ok)


class RepositoryContentTests(unittest.TestCase):
    """The shipped example content must always build cleanly."""

    def test_example_content_builds(self):
        with tempfile.TemporaryDirectory() as out:
            report = build_site(Config.from_env(ROOT, {"OUTPUT_DIR": out}))
            self.assertTrue(report.ok, report.errors)


if __name__ == "__main__":
    unittest.main()


VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def inspect_html(source: str) -> dict:
    """Parse a page and collect structural problems."""
    from html.parser import HTMLParser

    result = {"ids": [], "refs": [], "anchors": [], "unsafe_blank": [], "no_alt": [], "unbalanced": []}

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if "id" in a:
                result["ids"].append(a["id"])
            for key in ("aria-controls", "aria-labelledby", "aria-describedby"):
                result["refs"] += [(key, ref) for ref in (a.get(key) or "").split()]
            href = a.get("href") or ""
            if tag == "a" and href.startswith("#") and len(href) > 1:
                result["anchors"].append(href[1:])
            if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                result["unsafe_blank"].append(href)
            if tag == "img" and "alt" not in a:
                result["no_alt"].append(a.get("src"))
            if tag not in VOID_TAGS:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if tag in VOID_TAGS:
                return
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                result["unbalanced"].append(tag)

    parser = Parser()
    parser.feed(source)
    result["unbalanced"] += parser.stack
    return result


class HtmlIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        build_site(Config.from_env(ROOT, {"OUTPUT_DIR": cls._tmp.name}))
        cls.pages = {name: inspect_html((Path(cls._tmp.name) / name).read_text(encoding="utf-8"))
                     for name in ("index.html", "404.html")}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_tags_are_balanced(self):
        for name, page in self.pages.items():
            self.assertEqual(page["unbalanced"], [], name)

    def test_ids_are_unique(self):
        ids = self.pages["index.html"]["ids"]
        self.assertEqual(sorted({i for i in ids if ids.count(i) > 1}), [])

    def test_aria_references_and_anchors_resolve(self):
        page = self.pages["index.html"]
        for key, ref in page["refs"]:
            self.assertIn(ref, page["ids"], key)
        for anchor in page["anchors"]:
            self.assertIn(anchor, page["ids"], "#" + anchor)

    def test_links_and_images_are_safe_and_accessible(self):
        page = self.pages["index.html"]
        self.assertEqual(page["unsafe_blank"], [])
        self.assertEqual(page["no_alt"], [])


class ExampleContentTests(unittest.TestCase):
    """Guards the shipped example content against silently losing text or images."""

    def test_every_example_item_has_readme_text(self):
        for readme in (ROOT / "content").glob("*/*/README.md"):
            self.assertGreater(len(readme.read_text(encoding="utf-8").strip()), 20, str(readme))

    def test_readme_images_exist(self):
        for readme in (ROOT / "content").glob("*/*/README.md"):
            for target in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", readme.read_text(encoding="utf-8")):
                if not target.startswith("http"):
                    self.assertTrue((readme.parent / target).exists(), "%s -> %s" % (readme, target))


class DocumentationLinkTests(unittest.TestCase):
    """Relative links and images in the Markdown files must point at real files."""

    def test_relative_links_resolve(self):
        for doc in [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *(ROOT / "docs").glob("*.md")]:
            for target in re.findall(r"\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                path = (doc.parent / target.split("#")[0]).resolve()
                self.assertTrue(path.exists(), "%s -> %s" % (doc.name, target))
