import unittest

from job_importer import jobs_to_csv, parse_jobs_csv
from job_store import JobApplication


class JobImporterTest(unittest.TestCase):
    def test_parse_jobs_csv_creates_jobs_from_supported_columns(self):
        csv_text = (
            "company,title,location,url,description,notes\n"
            "Acme,Backend Developer,Remote,https://example.com,Build APIs,Good fit\n"
        )

        jobs = parse_jobs_csv(csv_text)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].company, "Acme")
        self.assertEqual(jobs[0].title, "Backend Developer")
        self.assertEqual(jobs[0].notes, "Good fit")

    def test_parse_jobs_csv_supports_headers_with_spaces(self):
        csv_text = "Company,Job title,Job URL\nAcme,AI Engineer,https://example.com\n"

        jobs = parse_jobs_csv(csv_text)

        self.assertEqual(jobs[0].company, "Acme")
        self.assertEqual(jobs[0].url, "https://example.com")

    def test_parse_jobs_csv_skips_empty_rows(self):
        csv_text = "company,title\n,\nAcme,Backend Developer\n"

        jobs = parse_jobs_csv(csv_text)

        self.assertEqual(len(jobs), 1)

    def test_parse_jobs_csv_returns_empty_list_for_empty_text(self):
        self.assertEqual(parse_jobs_csv(""), [])

    def test_parse_jobs_csv_raises_when_columns_are_unknown(self):
        with self.assertRaises(ValueError):
            parse_jobs_csv("unknown\nvalue\n")

    def test_jobs_to_csv_exports_tracker_fields(self):
        csv_text = jobs_to_csv(
            [
                JobApplication(
                    company="Acme",
                    title="Backend Developer",
                    status="Analyzed",
                    match_percentage=88,
                    resume_score=91,
                    missing_skills=["Docker"],
                    keyword_gaps=["CI/CD"],
                )
            ]
        )

        self.assertIn("company,title,location,url,status", csv_text)
        self.assertIn("Acme,Backend Developer", csv_text)
        self.assertIn("Analyzed,88,91", csv_text)
        self.assertIn("Docker", csv_text)


if __name__ == "__main__":
    unittest.main()
