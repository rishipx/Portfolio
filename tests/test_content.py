import tempfile
import unittest
from pathlib import Path

from helpers import ROOT, post, project, write_content, write_item
from sitebuilder.config import Config
from sitebuilder.content import load_items
from sitebuilder.diagnostics import Report


def load(content: Path):
    cfg = Config.from_env(ROOT, {"CONTENT_DIR": str(content)})
    report = Report()
    return load_items(cfg, report), report


class ContentTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.content = Path(self._tmp.name)
        write_content(self.content)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_items_load(self):
        write_item(self.content, "projects", "alpha", project())
        write_item(self.content, "posts", "beta", post())
        items, report = load(self.content)
        self.assertTrue(report.ok, report.errors)
        self.assertEqual([item.slug for item in items], ["alpha", "beta"])

    def test_order_then_projects_then_newest_posts(self):
        write_item(self.content, "projects", "late", project("Late"))
        write_item(self.content, "projects", "first", project("First", order=1))
        write_item(self.content, "posts", "old", post("Old", date="2025-01-01"))
        write_item(self.content, "posts", "new", post("New", date="2026-06-01"))
        items, _ = load(self.content)
        self.assertEqual([item.slug for item in items], ["first", "late", "new", "old"])

    def test_draft_items_are_skipped(self):
        write_item(self.content, "projects", "wip", project(draft=True))
        items, report = load(self.content)
        self.assertEqual(items, [])
        self.assertTrue(report.ok)

    def test_missing_fields_are_reported(self):
        write_item(self.content, "projects", "bad", {"title": "Only a title"})
        _, report = load(self.content)
        self.assertIn("missing required field(s): summary, kicker", report.errors[0])

    def test_invalid_post_kind_date_and_urls(self):
        write_item(self.content, "posts", "a", post(kind="tutorial"))
        write_item(self.content, "posts", "b", post(date="2026-13-40"))
        write_item(self.content, "projects", "c", project(website="ftp://x"))
        _, report = load(self.content)
        text = "\n".join(report.errors)
        self.assertIn('"kind" must be one of', text)
        self.assertIn('"date" must look like', text)
        self.assertIn("must start with http", text)

    def test_missing_cover_and_bad_slug(self):
        write_item(self.content, "projects", "no-cover", project(), cover=False)
        write_item(self.content, "projects", "Bad_Slug", project())
        _, report = load(self.content)
        text = "\n".join(report.errors)
        self.assertIn("add a cover image", text)
        self.assertIn("lowercase letters", text)

    def test_duplicate_slug_across_sections(self):
        write_item(self.content, "projects", "same", project())
        write_item(self.content, "posts", "same", post())
        _, report = load(self.content)
        self.assertIn("slugs must be unique", report.errors[0])


if __name__ == "__main__":
    unittest.main()
