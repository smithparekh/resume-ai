import tempfile
import unittest
from pathlib import Path

from backup_manager import backup_paths, create_file_backup


class BackupManagerTest(unittest.TestCase):
    def test_create_file_backup_copies_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "jobs.json"
            backup_dir = Path(temp_dir) / "backups"
            source.write_text("[]", encoding="utf-8")

            backup = create_file_backup(source, backup_dir)

            self.assertTrue(backup.exists())
            self.assertEqual(backup.read_text(encoding="utf-8"), "[]")

    def test_backup_paths_skips_missing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing = Path(temp_dir) / "profile.json"
            missing = Path(temp_dir) / "missing.json"
            existing.write_text("{}", encoding="utf-8")

            backups = backup_paths([existing, missing], Path(temp_dir) / "backups")

            self.assertEqual(len(backups), 1)


if __name__ == "__main__":
    unittest.main()
