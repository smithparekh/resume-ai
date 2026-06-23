import unittest

from analytics import build_tracker_metrics
from job_store import JobApplication


class AnalyticsTest(unittest.TestCase):
    def test_build_tracker_metrics_summarizes_tracker(self):
        jobs = [
            JobApplication(status="Applied", match_percentage=80, missing_skills=["Docker"]),
            JobApplication(status="Interview", match_percentage=90, missing_skills=["Docker", "AWS"]),
            JobApplication(status="Saved"),
        ]

        metrics = build_tracker_metrics(jobs)

        self.assertEqual(metrics["total_jobs"], 3)
        self.assertEqual(metrics["analyzed_jobs"], 2)
        self.assertEqual(metrics["applied_count"], 2)
        self.assertEqual(metrics["interview_count"], 1)
        self.assertEqual(metrics["interview_conversion"], 50)
        self.assertEqual(metrics["average_match"], 85)
        self.assertEqual(metrics["top_missing_skills"][0], ("Docker", 2))


if __name__ == "__main__":
    unittest.main()
