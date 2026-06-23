import unittest

from profile_store import CandidateProfile
from resume_tailor import build_profile_context


class ResumeTailorTest(unittest.TestCase):
    def test_build_profile_context_includes_profile_fields(self):
        profile = CandidateProfile(
            name="Aarav Sharma",
            email="aarav@example.com",
            phone="9999999999",
            target_roles=["Backend Developer"],
            preferred_locations=["Remote"],
            skills=["Python", "SQL"],
            experience_summary="Built APIs.",
            links={"github": "https://github.com/aarav"},
        )

        context = build_profile_context(profile)

        self.assertIn("Name: Aarav Sharma", context)
        self.assertIn("Target roles: Backend Developer", context)
        self.assertIn("Skills: Python, SQL", context)
        self.assertIn("github: https://github.com/aarav", context)

    def test_build_profile_context_uses_defaults_for_empty_profile(self):
        context = build_profile_context(CandidateProfile())

        self.assertIn("Name: Not provided", context)
        self.assertIn("Skills: Not provided", context)
        self.assertIn("Links: Not provided", context)


if __name__ == "__main__":
    unittest.main()
