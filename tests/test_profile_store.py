import json
import tempfile
import unittest
from pathlib import Path

from profile_store import (
    CandidateProfile,
    ProfileStoreError,
    format_list,
    load_profile,
    parse_list,
    save_profile,
)


class ProfileStoreTest(unittest.TestCase):
    def test_load_profile_returns_empty_profile_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = load_profile(Path(temp_dir) / "missing.json")

        self.assertEqual(profile, CandidateProfile())

    def test_save_and_load_profile_round_trip(self):
        profile = CandidateProfile(
            name="Aarav Sharma",
            email="aarav@example.com",
            phone="9999999999",
            target_roles=["Backend Developer", "AI Engineer"],
            preferred_locations=["Bengaluru", "Remote"],
            skills=["Python", "FastAPI", "LLM"],
            experience_summary="Built production Python services.",
            links={"linkedin": "https://linkedin.com/in/aarav"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "profile.json"
            save_profile(profile, profile_path)
            loaded_profile = load_profile(profile_path)

        self.assertEqual(loaded_profile, profile)

    def test_load_profile_uses_defaults_for_missing_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "profile.json"
            profile_path.write_text(json.dumps({"name": "Aarav"}), encoding="utf-8")

            profile = load_profile(profile_path)

        self.assertEqual(profile.name, "Aarav")
        self.assertEqual(profile.skills, [])
        self.assertEqual(profile.links, {})

    def test_load_profile_backs_up_corrupt_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "profile.json"
            profile_path.write_text("{broken", encoding="utf-8")

            with self.assertRaises(ProfileStoreError):
                load_profile(profile_path)

            backups = list(Path(temp_dir).glob("profile.json.corrupt*"))

        self.assertEqual(len(backups), 1)

    def test_load_profile_backs_up_non_object_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "profile.json"
            profile_path.write_text(json.dumps(["Aarav"]), encoding="utf-8")

            with self.assertRaises(ProfileStoreError):
                load_profile(profile_path)

            backups = list(Path(temp_dir).glob("profile.json.corrupt*"))

        self.assertEqual(len(backups), 1)

    def test_parse_list_trims_empty_items(self):
        self.assertEqual(parse_list("Python, FastAPI, , LLM "), ["Python", "FastAPI", "LLM"])

    def test_format_list_joins_values(self):
        self.assertEqual(format_list(["Python", "FastAPI"]), "Python, FastAPI")


if __name__ == "__main__":
    unittest.main()
