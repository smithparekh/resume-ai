import json
import tempfile
import unittest
from pathlib import Path

from job_store import (
    JobApplication,
    JobStoreError,
    add_job,
    add_job_if_new,
    apply_analysis,
    apply_cover_letter,
    apply_tailoring_plan,
    delete_job,
    is_duplicate_job,
    load_jobs,
    save_jobs,
    status_counts,
    update_job,
)


class JobStoreTest(unittest.TestCase):
    def test_load_jobs_returns_empty_list_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs = load_jobs(Path(temp_dir) / "missing.json")

        self.assertEqual(jobs, [])

    def test_save_and_load_jobs_round_trip(self):
        job = JobApplication(
            company="Acme",
            title="Backend Developer",
            location="Remote",
            url="https://example.com/job",
            description="Build APIs",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            save_jobs([job], jobs_path)
            loaded_jobs = load_jobs(jobs_path)

        self.assertEqual(len(loaded_jobs), 1)
        self.assertEqual(loaded_jobs[0].company, "Acme")
        self.assertEqual(loaded_jobs[0].title, "Backend Developer")

    def test_add_job_appends_to_existing_jobs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            add_job(JobApplication(company="One"), jobs_path)
            add_job(JobApplication(company="Two"), jobs_path)
            jobs = load_jobs(jobs_path)

        self.assertEqual([job.company for job in jobs], ["One", "Two"])

    def test_add_job_if_new_skips_duplicate_url(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            add_job_if_new(JobApplication(company="One", url="https://example.com/job"), jobs_path)
            duplicate = add_job_if_new(JobApplication(company="Two", url="https://example.com/job/"), jobs_path)
            jobs = load_jobs(jobs_path)

        self.assertIsNone(duplicate)
        self.assertEqual(len(jobs), 1)

    def test_is_duplicate_job_matches_company_and_title_when_url_is_missing(self):
        jobs = [JobApplication(company="Acme", title="Backend Developer")]

        self.assertTrue(
            is_duplicate_job(
                JobApplication(company=" acme ", title="Backend   Developer"),
                jobs,
            )
        )

    def test_is_duplicate_job_returns_false_when_identity_is_incomplete(self):
        jobs = [JobApplication(company="Acme", title="Backend Developer")]

        self.assertFalse(is_duplicate_job(JobApplication(company="Acme"), jobs))

    def test_update_job_replaces_matching_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            job = add_job(JobApplication(company="Acme", status="Saved"), jobs_path)
            job.status = "Applied"
            update_job(job, jobs_path)
            jobs = load_jobs(jobs_path)

        self.assertEqual(jobs[0].status, "Applied")

    def test_update_job_raises_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                update_job(JobApplication(id="missing"), Path(temp_dir) / "jobs.json")

    def test_delete_job_removes_matching_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            job = add_job(JobApplication(company="Acme"), jobs_path)
            deleted = delete_job(job.id, jobs_path)
            jobs = load_jobs(jobs_path)

        self.assertTrue(deleted)
        self.assertEqual(jobs, [])

    def test_delete_job_returns_false_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            add_job(JobApplication(company="Acme"), jobs_path)

            self.assertFalse(delete_job("missing", jobs_path))

    def test_load_jobs_backs_up_corrupt_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            jobs_path.write_text("{broken", encoding="utf-8")

            with self.assertRaises(JobStoreError):
                load_jobs(jobs_path)

            backups = list(Path(temp_dir).glob("jobs.json.corrupt*"))

        self.assertEqual(len(backups), 1)

    def test_load_jobs_backs_up_non_list_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            jobs_path.write_text(json.dumps({"company": "Acme"}), encoding="utf-8")

            with self.assertRaises(JobStoreError):
                load_jobs(jobs_path)

            backups = list(Path(temp_dir).glob("jobs.json.corrupt*"))

        self.assertEqual(len(backups), 1)

    def test_apply_analysis_maps_analysis_fields_to_job(self):
        job = JobApplication()
        updated_job = apply_analysis(
            job,
            {
                "resume_score": 82,
                "jd_match_percentage": 76,
                "missing_skills": ["Docker"],
                "keyword_gaps": ["CI/CD"],
                "improvement_suggestions": ["Add deployment project"],
            },
        )

        self.assertEqual(updated_job.status, "Analyzed")
        self.assertEqual(updated_job.resume_score, 82)
        self.assertEqual(updated_job.match_percentage, 76)
        self.assertEqual(updated_job.missing_skills, ["Docker"])

    def test_load_jobs_uses_defaults_for_missing_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            jobs_path.write_text(json.dumps([{"company": "Acme"}]), encoding="utf-8")
            jobs = load_jobs(jobs_path)

        self.assertEqual(jobs[0].company, "Acme")
        self.assertEqual(jobs[0].status, "Saved")
        self.assertEqual(jobs[0].missing_skills, [])

    def test_load_jobs_uses_defaults_for_missing_material_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jobs_path = Path(temp_dir) / "jobs.json"
            jobs_path.write_text(json.dumps([{"company": "Acme"}]), encoding="utf-8")
            jobs = load_jobs(jobs_path)

        self.assertEqual(jobs[0].tailoring_plan, "")
        self.assertEqual(jobs[0].cover_letter, "")

    def test_apply_tailoring_plan_trims_and_stores_plan(self):
        job = apply_tailoring_plan(JobApplication(), "  Plan text  ")

        self.assertEqual(job.tailoring_plan, "Plan text")

    def test_apply_cover_letter_trims_and_stores_letter(self):
        job = apply_cover_letter(JobApplication(), "  Letter text  ")

        self.assertEqual(job.cover_letter, "Letter text")

    def test_status_counts_groups_jobs_by_status(self):
        jobs = [
            JobApplication(status="Saved"),
            JobApplication(status="Saved"),
            JobApplication(status="Applied"),
        ]

        counts = status_counts(jobs)

        self.assertEqual(counts["Saved"], 2)
        self.assertEqual(counts["Applied"], 1)
        self.assertEqual(counts["Interview"], 0)


if __name__ == "__main__":
    unittest.main()
