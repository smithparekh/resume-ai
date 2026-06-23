import os
import unittest
from unittest.mock import patch

from llm import LLMError, _limit_text, analyze_resume
from prompts import COVER_LETTER_PROMPT, TAILORING_PROMPT


class LLMTest(unittest.TestCase):
    def test_limit_text_returns_short_text_unchanged(self):
        self.assertEqual(_limit_text("short", max_chars=10), "short")

    def test_limit_text_truncates_long_text(self):
        limited_text = _limit_text("a" * 12, max_chars=10)

        self.assertTrue(limited_text.startswith("a" * 10))
        self.assertIn("Content truncated to 10 characters", limited_text)

    def test_analyze_resume_raises_clear_error_when_api_key_is_missing(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
            with self.assertRaises(LLMError) as error:
                analyze_resume("resume", "job")

        self.assertIn("GROQ_API_KEY is missing", str(error.exception))

    def test_tailoring_prompt_requests_finished_resume_not_advice(self):
        self.assertIn("complete, ready-to-use tailored resume draft", TAILORING_PROMPT)
        self.assertIn("Rewrite the resume content yourself", TAILORING_PROMPT)
        self.assertIn("Do not include placeholders", TAILORING_PROMPT)

    def test_cover_letter_prompt_requests_finished_job_specific_letter(self):
        self.assertIn("complete, ready-to-send tailored cover letter", COVER_LETTER_PROMPT)
        self.assertIn("Apply the candidate's background directly to this job", COVER_LETTER_PROMPT)
        self.assertIn("Do not include placeholders", COVER_LETTER_PROMPT)


if __name__ == "__main__":
    unittest.main()
