import unittest

from response_parser import parse_json_object, validate_analysis_response


class ResponseParserTest(unittest.TestCase):
    def test_parse_json_object_reads_plain_json(self):
        data = parse_json_object('{"resume_score": 80}')

        self.assertEqual(data["resume_score"], 80)

    def test_parse_json_object_reads_json_inside_markdown_fence(self):
        data = parse_json_object('```json\n{"resume_score": 80}\n```')

        self.assertEqual(data["resume_score"], 80)

    def test_parse_json_object_reads_json_with_intro_text(self):
        data = parse_json_object('Here is the result:\n{"resume_score": 80}\nThanks')

        self.assertEqual(data["resume_score"], 80)

    def test_parse_json_object_raises_for_invalid_response(self):
        with self.assertRaises(ValueError):
            parse_json_object("No JSON here")

    def test_validate_analysis_response_accepts_valid_payload(self):
        data = validate_analysis_response(
            {
                "resume_score": "80",
                "jd_match_percentage": 75,
                "missing_skills": ["Docker", ""],
                "keyword_gaps": ["CI/CD"],
                "improvement_suggestions": ["Add deployment project"],
            }
        )

        self.assertEqual(data["resume_score"], 80)
        self.assertEqual(data["missing_skills"], ["Docker"])

    def test_validate_analysis_response_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            validate_analysis_response({"resume_score": 80})

    def test_validate_analysis_response_rejects_score_outside_range(self):
        with self.assertRaises(ValueError):
            validate_analysis_response(
                {
                    "resume_score": 120,
                    "jd_match_percentage": 75,
                    "missing_skills": [],
                    "keyword_gaps": [],
                    "improvement_suggestions": [],
                }
            )

    def test_validate_analysis_response_rejects_non_list_fields(self):
        with self.assertRaises(ValueError):
            validate_analysis_response(
                {
                    "resume_score": 80,
                    "jd_match_percentage": 75,
                    "missing_skills": "Docker",
                    "keyword_gaps": [],
                    "improvement_suggestions": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
