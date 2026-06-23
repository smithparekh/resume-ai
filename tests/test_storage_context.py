import os
import unittest
from pathlib import Path
from unittest.mock import patch

from storage_context import (
    DEFAULT_JOBS_PATH,
    DEFAULT_PROFILE_PATH,
    MULTI_USER_ENV,
    jobs_path_for_workspace,
    profile_path_for_workspace,
    resolve_storage_paths,
    sanitize_workspace_id,
)


class StorageContextTest(unittest.TestCase):
    def test_sanitize_workspace_id_removes_unsafe_characters(self):
        self.assertEqual(sanitize_workspace_id(" Jane Smith@example.com "), "jane-smith-example-com")

    def test_resolve_storage_paths_uses_local_paths_by_default(self):
        with patch.dict(os.environ, {MULTI_USER_ENV: ""}, clear=False):
            self.assertEqual(resolve_storage_paths(), (DEFAULT_PROFILE_PATH, DEFAULT_JOBS_PATH))

    def test_resolve_storage_paths_uses_user_workspace_when_enabled(self):
        with patch.dict(os.environ, {MULTI_USER_ENV: "true"}, clear=False):
            profile_path, jobs_path = resolve_storage_paths("Jane Smith")

        self.assertEqual(profile_path, Path("data/users/jane-smith/profile.json"))
        self.assertEqual(jobs_path, Path("data/users/jane-smith/jobs.json"))

    def test_resolve_storage_paths_requires_workspace_when_enabled(self):
        with patch.dict(os.environ, {MULTI_USER_ENV: "true"}, clear=False):
            with self.assertRaises(ValueError):
                resolve_storage_paths("")

    def test_workspace_path_helpers_accept_custom_base_dir(self):
        base_dir = Path("/tmp/users")

        self.assertEqual(profile_path_for_workspace("Jane", base_dir), Path("/tmp/users/jane/profile.json"))
        self.assertEqual(jobs_path_for_workspace("Jane", base_dir), Path("/tmp/users/jane/jobs.json"))


if __name__ == "__main__":
    unittest.main()
