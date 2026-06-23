import unittest

from application_checklist import build_application_checklist, readiness_percentage
from job_store import JobApplication
from profile_store import CandidateProfile


class ApplicationChecklistTest(unittest.TestCase):
    def test_build_application_checklist_marks_ready_items(self):
        job = JobApplication(
            company="Acme",
            description="Build APIs",
            match_percentage=80,
            tailoring_plan="Plan",
            cover_letter="Letter",
        )
        profile = CandidateProfile(name="Aarav", email="aarav@example.com")

        items = build_application_checklist(job, profile, has_resume=True)
        ready_by_label = {item.label: item.is_ready for item in items}

        self.assertTrue(ready_by_label["Resume uploaded"])
        self.assertTrue(ready_by_label["Candidate profile has name"])
        self.assertTrue(ready_by_label["Cover letter saved"])

    def test_build_application_checklist_marks_missing_items(self):
        items = build_application_checklist(
            JobApplication(),
            CandidateProfile(),
            has_resume=False,
        )
        ready_by_label = {item.label: item.is_ready for item in items}

        self.assertFalse(ready_by_label["Resume uploaded"])
        self.assertFalse(ready_by_label["Candidate profile has email"])
        self.assertFalse(ready_by_label["Job analyzed"])

    def test_readiness_percentage_calculates_ready_share(self):
        items = build_application_checklist(
            JobApplication(company="Acme"),
            CandidateProfile(name="Aarav"),
            has_resume=True,
        )

        self.assertEqual(readiness_percentage(items), 38)

    def test_readiness_percentage_returns_zero_for_empty_items(self):
        self.assertEqual(readiness_percentage([]), 0)


if __name__ == "__main__":
    unittest.main()
