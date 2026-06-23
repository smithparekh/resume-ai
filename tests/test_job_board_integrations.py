import unittest
from unittest.mock import Mock, patch

from job_board_integrations import (
    JobBoardIntegrationError,
    UnsupportedJobBoardError,
    detect_supported_job_board,
    fetch_ashby_job,
    fetch_greenhouse_job,
    fetch_job_with_integration,
    fetch_lever_job,
)


class JobBoardIntegrationsTest(unittest.TestCase):
    def test_detect_supported_job_board(self):
        self.assertEqual(detect_supported_job_board("https://boards.greenhouse.io/acme/jobs/123"), "Greenhouse")
        self.assertEqual(detect_supported_job_board("https://jobs.lever.co/acme/abc"), "Lever")
        self.assertEqual(detect_supported_job_board("https://jobs.ashbyhq.com/acme/abc-123"), "Ashby")
        self.assertEqual(detect_supported_job_board("https://example.com/job"), "")

    @patch("job_board_integrations.requests.get")
    def test_fetch_greenhouse_job_uses_greenhouse_api(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "title": "Backend Engineer",
            "company_name": "Acme",
            "location": {"name": "Remote"},
            "content": "Build APIs",
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        job = fetch_greenhouse_job("https://boards.greenhouse.io/acme/jobs/123")

        self.assertEqual(job.company, "Acme")
        self.assertEqual(job.title, "Backend Engineer")
        self.assertEqual(job.source, "Greenhouse")
        mock_get.assert_called_once_with(
            "https://boards-api.greenhouse.io/v1/boards/acme/jobs/123",
            timeout=15,
        )

    @patch("job_board_integrations.requests.get")
    def test_fetch_lever_job_uses_lever_api(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "text": "Data Engineer",
            "categories": {"location": "Remote"},
            "descriptionPlain": "Build pipelines",
            "lists": [{"text": "Requirements", "content": [{"text": "Python"}]}],
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        job = fetch_lever_job("https://jobs.lever.co/acme/abc")

        self.assertEqual(job.company, "acme")
        self.assertEqual(job.title, "Data Engineer")
        self.assertIn("Python", job.description)
        self.assertEqual(job.source, "Lever")

    @patch("job_board_integrations.requests.get")
    def test_fetch_ashby_job_uses_ashby_api(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "organizationName": "Acme Inc",
            "jobs": [
                {
                    "title": "ML Engineer",
                    "location": "Remote",
                    "descriptionPlain": "Build ML systems",
                    "jobUrl": "https://jobs.ashbyhq.com/acme/abc-123",
                },
            ],
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        job = fetch_ashby_job("https://jobs.ashbyhq.com/acme/abc-123")

        self.assertEqual(job.company, "Acme Inc")
        self.assertEqual(job.title, "ML Engineer")
        self.assertEqual(job.location, "Remote")
        self.assertEqual(job.description, "Build ML systems")
        self.assertEqual(job.source, "Ashby")
        mock_get.assert_called_once_with(
            "https://api.ashbyhq.com/posting-api/job-board/acme",
            timeout=15,
        )

    @patch("job_board_integrations.requests.get")
    def test_fetch_ashby_job_falls_back_to_slug_when_no_org_name(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [
                {
                    "title": "SWE",
                    "location": "",
                    "descriptionPlain": "Write code",
                    "jobUrl": "https://jobs.ashbyhq.com/acme/abc-123",
                },
            ],
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        job = fetch_ashby_job("https://jobs.ashbyhq.com/acme/abc-123")

        self.assertEqual(job.company, "acme")

    @patch("job_board_integrations.requests.get")
    def test_fetch_ashby_job_raises_when_job_not_found(self, mock_get):
        response = Mock()
        response.json.return_value = {"organizationName": "Acme", "jobs": []}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaises(JobBoardIntegrationError):
            fetch_ashby_job("https://jobs.ashbyhq.com/acme/nonexistent-id")

    def test_fetch_ashby_job_raises_on_bad_url(self):
        with self.assertRaises(UnsupportedJobBoardError):
            fetch_ashby_job("https://jobs.ashbyhq.com/acme")

    def test_fetch_job_with_integration_rejects_unsupported_board(self):
        with self.assertRaises(UnsupportedJobBoardError):
            fetch_job_with_integration("https://example.com/job")


if __name__ == "__main__":
    unittest.main()
