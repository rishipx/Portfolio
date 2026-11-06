import unittest

from helpers import ROOT  # noqa: F401  (sets up sys.path)
from sitebuilder.markdown import to_html

BASE = "assets/projects/demo/"


class MarkdownTests(unittest.TestCase):
    def test_headings_and_paragraphs(self):
        html = to_html("## Title\n\nSome text.", BASE)
        self.assertIn('<h3 class="md-heading">Title</h3>', html)
        self.assertIn("<p>Some text.</p>", html)

    def test_lists_and_inline_formatting(self):
        html = to_html("- one\n- **two** and `code`", BASE)
        self.assertIn("<ul><li>one</li><li><strong>two</strong> and <code>code</code></li></ul>", html)

    def test_external_links_open_safely(self):
        html = to_html("[docs](https://example.com)", BASE)
        self.assertIn('target="_blank" rel="noopener noreferrer"', html)

    def test_javascript_urls_are_neutralised(self):
        self.assertIn('href="#"', to_html("[x](javascript:alert(1))", BASE))

    def test_html_is_escaped(self):
        self.assertIn("&lt;script&gt;", to_html("<script>alert(1)</script>", BASE))
        self.assertNotIn("<script>", to_html("`<script>`", BASE))

    def test_image_on_its_own_line_becomes_figure_with_caption(self):
        html = to_html('![Alt](images/a.png "A caption")', BASE)
        self.assertIn('src="assets/projects/demo/images/a.png"', html)
        self.assertIn('<p class="dialog-image-note">A caption</p>', html)
        self.assertNotIn("<p><img", html)

    def test_absolute_image_urls_are_left_alone(self):
        self.assertIn('src="https://cdn.example.com/a.png"', to_html("![a](https://cdn.example.com/a.png)", BASE))


if __name__ == "__main__":
    unittest.main()
