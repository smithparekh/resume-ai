import unittest
from unittest.mock import Mock, patch

import requests

from job_url_importer import (
    JobPageFetchError,
    fetch_job_from_url,
    fetch_job_from_url_with_browser,
    normalize_url,
    parse_job_page,
    parse_urls,
    split_title,
)


class JobUrlImporterTest(unittest.TestCase):
    def test_parse_job_page_uses_meta_title_and_description(self):
        html = """
        <html>
          <head>
            <meta property="og:title" content="Backend Developer - Acme">
            <meta name="description" content="Build APIs with Python.">
          </head>
          <body>Other page content</body>
        </html>
        """

        job = parse_job_page("https://example.com/jobs/1", html)

        self.assertEqual(job.company, "Acme")
        self.assertEqual(job.title, "Backend Developer")
        self.assertEqual(job.description, "Build APIs with Python.")
        self.assertEqual(job.url, "https://example.com/jobs/1")

    def test_parse_job_page_falls_back_to_visible_text(self):
        html = """
        <html>
          <head><title>AI Engineer at Globex</title></head>
          <body>
            <script>ignore me</script>
            <h1>AI Engineer</h1>
            <p>Work on LLM products.</p>
          </body>
        </html>
        """

        job = parse_job_page("https://globex.example/jobs/ai", html)

        self.assertEqual(job.company, "Globex")
        self.assertEqual(job.title, "AI Engineer")
        self.assertIn("Work on LLM products.", job.description)
        self.assertNotIn("ignore me", job.description)

    def test_parse_job_page_prefers_useful_visible_text_over_short_meta_description(self):
        useful_description = " ".join(["Build reliable data systems with Python and SQL."] * 8)
        html = f"""
        <html>
          <head>
            <title>Data Engineer - Acme</title>
            <meta name="description" content="Careers at Acme.">
          </head>
          <body><main>{useful_description}</main></body>
        </html>
        """

        job = parse_job_page("https://example.com/jobs/data", html)

        self.assertIn(useful_description, job.description)
        self.assertNotEqual(job.description, "Careers at Acme.")

    def test_parse_job_page_flags_weak_import_for_manual_review(self):
        html = """
        <html>
          <head><title>Backend Developer - Acme</title></head>
          <body>Apply now.</body>
        </html>
        """

        job = parse_job_page("https://example.com/jobs/1", html)

        self.assertIn("manual cleanup", job.notes)

    def test_parse_urls_normalizes_multiple_lines(self):
        self.assertEqual(
            parse_urls("example.com/job\nhttps://acme.com/job\n"),
            ["https://example.com/job", "https://acme.com/job"],
        )

    def test_normalize_url_rejects_invalid_urls(self):
        with self.assertRaises(ValueError):
            normalize_url("not a url with spaces")

    def test_split_title_supports_common_patterns(self):
        self.assertEqual(split_title("Backend Developer - Acme", "https://x.com"), ("Acme", "Backend Developer"))
        self.assertEqual(split_title("AI Engineer at Globex", "https://x.com"), ("Globex", "AI Engineer"))

    @patch("job_url_importer.requests.get")
    def test_fetch_job_from_url_returns_job_for_successful_response(self, mock_get):
        response = Mock()
        response.text = "<title>Backend Developer - Acme</title><p>Build APIs.</p>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        job = fetch_job_from_url("example.com/job")

        self.assertEqual(job.company, "Acme")
        self.assertEqual(job.title, "Backend Developer")
        mock_get.assert_called_once()

    @patch("job_url_importer.requests.get", side_effect=requests.RequestException("network down"))
    def test_fetch_job_from_url_wraps_request_errors(self, _mock_get):
        with self.assertRaises(JobPageFetchError):
            fetch_job_from_url("https://example.com/job")

    @patch("job_url_importer.fetch_job_from_url_with_browser")
    def test_fetch_job_from_url_uses_browser_when_requested(self, mock_fetch_browser):
        mock_fetch_browser.return_value = parse_job_page(
            "https://example.com/job",
            "<title>Backend Developer - Acme</title><p>Build APIs.</p>",
        )

        job = fetch_job_from_url("https://example.com/job", use_browser=True)

        self.assertEqual(job.company, "Acme")
        mock_fetch_browser.assert_called_once_with("https://example.com/job")

    @patch.dict("sys.modules", {"playwright.sync_api": None})
    def test_fetch_job_from_url_with_browser_requires_playwright(self):
        with self.assertRaises(JobPageFetchError) as error:
            fetch_job_from_url_with_browser("https://example.com/job")

        self.assertIn("requires Playwright", str(error.exception))


if __name__ == "__main__":
    unittest.main()
