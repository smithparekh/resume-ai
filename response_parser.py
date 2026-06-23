import json


REQUIRED_ANALYSIS_FIELDS = {
    "resume_score",
    "jd_match_percentage",
    "missing_skills",
    "keyword_gaps",
    "improvement_suggestions",
}


def parse_json_object(response_text: str) -> dict:
    cleaned_text = _strip_markdown_fence(response_text.strip())

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        start = cleaned_text.find("{")
        end = cleaned_text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise

        return json.loads(cleaned_text[start:end + 1])


def _strip_markdown_fence(response_text: str) -> str:
    if not response_text.startswith("```"):
        return response_text

    lines = response_text.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def validate_analysis_response(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("AI analysis must be a JSON object.")

    missing_fields = REQUIRED_ANALYSIS_FIELDS - set(data)
    if missing_fields:
        missing_text = ", ".join(sorted(missing_fields))
        raise ValueError(f"AI analysis is missing required field(s): {missing_text}.")

    return {
        "resume_score": _score(data["resume_score"], "resume_score"),
        "jd_match_percentage": _score(data["jd_match_percentage"], "jd_match_percentage"),
        "missing_skills": _string_list(data["missing_skills"], "missing_skills"),
        "keyword_gaps": _string_list(data["keyword_gaps"], "keyword_gaps"),
        "improvement_suggestions": _string_list(
            data["improvement_suggestions"],
            "improvement_suggestions",
        ),
    }


def _score(value, field_name: str) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a number from 0 to 100.") from error

    if score < 0 or score > 100:
        raise ValueError(f"{field_name} must be between 0 and 100.")

    return score


def _string_list(value, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")

    return [str(item).strip() for item in value if str(item).strip()]
