import tempfile
import unittest
from pathlib import Path

from job_store import JobApplication
from profile_store import CandidateProfile
from sqlite_store import (
    add_job_if_new,
    delete_job,
    load_jobs,
    load_profile,
    save_profile,
    update_job,
)


class SqliteStoreTest(unittest.TestCase):
    def test_profile_round_trip_is_scoped_by_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "app.sqlite3"
            save_profile(CandidateProfile(name="Aarav"), "user-a", database_path)

            self.assertEqual(load_profile("user-a", database_path).name, "Aarav")
            self.assertEqual(load_profile("user-b", database_path).name, "")

    def test_jobs_crud_is_scoped_by_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "app.sqlite3"
            job = add_job_if_new(
                JobApplication(company="Acme", title="Engineer"),
                "user-a",
                database_path,
            )

            self.assertIsNotNone(job)
            self.assertEqual(len(load_jobs("user-a", database_path)), 1)
            self.assertEqual(load_jobs("user-b", database_path), [])

            job.status = "Applied"
            update_job(job, "user-a", database_path)
            self.assertEqual(load_jobs("user-a", database_path)[0].status, "Applied")

            self.assertTrue(delete_job(job.id, "user-a", database_path))
            self.assertEqual(load_jobs("user-a", database_path), [])

    def test_add_job_if_new_skips_duplicate_within_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "app.sqlite3"
            add_job_if_new(JobApplication(company="Acme", title="Engineer"), "user-a", database_path)
            duplicate = add_job_if_new(JobApplication(company="Acme", title="Engineer"), "user-a", database_path)

            self.assertIsNone(duplicate)


if __name__ == "__main__":
    unittest.main()
