import unittest

from job_ranker import filter_jobs, jobs_ready_for_analysis, sort_jobs
from job_store import JobApplication


class JobRankerTest(unittest.TestCase):
    def test_filter_jobs_filters_by_status(self):
        jobs = [
            JobApplication(company="One", status="Saved"),
            JobApplication(company="Two", status="Applied"),
        ]

        filtered_jobs = filter_jobs(jobs, status="Applied")

        self.assertEqual([job.company for job in filtered_jobs], ["Two"])

    def test_filter_jobs_filters_by_query(self):
        jobs = [
            JobApplication(company="Acme", title="Backend Developer"),
            JobApplication(company="Globex", title="Frontend Developer"),
        ]

        filtered_jobs = filter_jobs(jobs, query="backend")

        self.assertEqual([job.company for job in filtered_jobs], ["Acme"])

    def test_sort_jobs_orders_best_match_first(self):
        jobs = [
            JobApplication(company="Low", match_percentage=45, resume_score=60),
            JobApplication(company="High", match_percentage=90, resume_score=80),
            JobApplication(company="Missing"),
        ]

        sorted_jobs = sort_jobs(jobs, "Best Match")

        self.assertEqual([job.company for job in sorted_jobs], ["High", "Low", "Missing"])

    def test_sort_jobs_orders_by_company(self):
        jobs = [
            JobApplication(company="Globex", title="Engineer"),
            JobApplication(company="Acme", title="Engineer"),
        ]

        sorted_jobs = sort_jobs(jobs, "Company")

        self.assertEqual([job.company for job in sorted_jobs], ["Acme", "Globex"])

    def test_jobs_ready_for_analysis_requires_description_and_allowed_status(self):
        jobs = [
            JobApplication(company="Ready", status="Saved", description="Build APIs"),
            JobApplication(company="No Description", status="Saved"),
            JobApplication(company="Already Applied", status="Applied", description="Build APIs"),
        ]

        ready_jobs = jobs_ready_for_analysis(jobs)

        self.assertEqual([job.company for job in ready_jobs], ["Ready"])


if __name__ == "__main__":
    unittest.main()
