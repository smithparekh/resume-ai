import unittest

from job_store import JobApplication
from workflows import analyze_jobs_batch, analyze_job_with_llm


VALID_ANALYSIS_JSON = """
{
  "resume_score": 84,
  "jd_match_percentage": 78,
  "missing_skills": ["Docker"],
  "keyword_gaps": ["CI/CD"],
  "improvement_suggestions": ["Add deployment details"]
}
"""


class WorkflowsTest(unittest.TestCase):
    def test_analyze_job_with_llm_applies_valid_analysis(self):
        job = JobApplication(description="Build APIs")

        updated_job = analyze_job_with_llm(job, "resume", lambda _resume, _jd: VALID_ANALYSIS_JSON)

        self.assertEqual(updated_job.status, "Analyzed")
        self.assertEqual(updated_job.resume_score, 84)
        self.assertEqual(updated_job.match_percentage, 78)
        self.assertEqual(updated_job.missing_skills, ["Docker"])

    def test_analyze_jobs_batch_keeps_successes_and_failures_separate(self):
        jobs = [
            JobApplication(company="Good", description="Build APIs"),
            JobApplication(company="Bad", description="Broken"),
        ]

        def analyzer(_resume, jd):
            if jd == "Broken":
                return "not json"
            return VALID_ANALYSIS_JSON

        analyzed_jobs, failures = analyze_jobs_batch(jobs, "resume", analyzer)

        self.assertEqual([job.company for job in analyzed_jobs], ["Good"])
        self.assertEqual(failures[0][0].company, "Bad")


if __name__ == "__main__":
    unittest.main()
