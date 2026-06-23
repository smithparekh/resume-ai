import unittest

from file_names import safe_file_stem


class FileNamesTest(unittest.TestCase):
    def test_safe_file_stem_removes_unsafe_characters(self):
        self.assertEqual(
            safe_file_stem("Acme / India", "Backend Developer"),
            "Acme_India_Backend_Developer",
        )

    def test_safe_file_stem_uses_default_when_empty(self):
        self.assertEqual(safe_file_stem("", "   ", default="application"), "application")


if __name__ == "__main__":
    unittest.main()
