"""Local, no-network tests for sitemap XML parsing."""

import unittest

from inspect_sitemap import SitemapFormatError, parse_sitemap


class SitemapParsingTests(unittest.TestCase):
    """Check supported sitemap shapes using small XML strings in memory."""

    def test_urlset_keeps_allowed_candidates_and_lastmod_values(self) -> None:
        """A regular sitemap keeps only allowed support-host URLs."""

        sitemap_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://support.brilliantdirectories.com/support/example</loc>
                <lastmod>2026-01-15</lastmod>
            </url>
            <url>
                <loc>https://support.brilliantdirectories.com/support/without-lastmod</loc>
            </url>
            <url>
                <loc>http://support.brilliantdirectories.com/support/not-https</loc>
            </url>
            <url>
                <loc>https://other.example/support/not-approved</loc>
            </url>
        </urlset>
        """

        result = parse_sitemap(sitemap_xml)

        self.assertEqual(result["sitemap_type"], "urlset")
        self.assertEqual(
            result["candidates"],
            [
                {
                    "loc": "https://support.brilliantdirectories.com/support/example",
                    "lastmod": "2026-01-15",
                },
                {
                    "loc": "https://support.brilliantdirectories.com/support/without-lastmod",
                    "lastmod": None,
                },
            ],
        )

    def test_sitemap_index_reports_children_without_treating_them_as_articles(self) -> None:
        """A sitemap index reports allowed child sitemap URLs without candidates."""

        sitemap_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://support.brilliantdirectories.com/support/help-sitemap.xml</loc>
                <lastmod>2026-02-01</lastmod>
            </sitemap>
            <sitemap>
                <loc>https://other.example/unapproved-sitemap.xml</loc>
            </sitemap>
        </sitemapindex>
        """

        result = parse_sitemap(sitemap_xml)

        self.assertEqual(result["sitemap_type"], "sitemapindex")
        self.assertEqual(result["candidates"], [])
        self.assertEqual(
            result["child_sitemaps"],
            [
                {
                    "loc": "https://support.brilliantdirectories.com/support/help-sitemap.xml",
                    "lastmod": "2026-02-01",
                }
            ],
        )

    def test_malformed_xml_raises_a_clear_format_error(self) -> None:
        """Invalid XML is converted into the script's sitemap format error."""

        with self.assertRaisesRegex(SitemapFormatError, "not valid XML"):
            parse_sitemap(b"<urlset><url><loc>https://example.test</loc></urlset>")


if __name__ == "__main__":
    unittest.main()
