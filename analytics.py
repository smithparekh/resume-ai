from collections import Counter

from job_store import JobApplication, VALID_STATUSES


def build_tracker_metrics(jobs: list[JobApplication]) -> dict:
    status_counts = {status: 0 for status in VALID_STATUSES}
    missing_skill_counts = Counter()
    analyzed_jobs = []

    for job in jobs:
        if job.status not in status_counts:
            status_counts[job.status] = 0
        status_counts[job.status] += 1

        if job.match_percentage is not None:
            analyzed_jobs.append(job)

        for skill in job.missing_skills:
            normalized_skill = skill.strip()
            if normalized_skill:
                missing_skill_counts[normalized_skill] += 1

    applied_count = sum(status_counts.get(status, 0) for status in ("Applied", "Interview", "Offer"))
    interview_count = status_counts.get("Interview", 0) + status_counts.get("Offer", 0)
    average_match = _average([job.match_percentage for job in analyzed_jobs])

    return {
        "total_jobs": len(jobs),
        "analyzed_jobs": len(analyzed_jobs),
        "applied_count": applied_count,
        "interview_count": interview_count,
        "interview_conversion": _percentage(interview_count, applied_count),
        "average_match": average_match,
        "top_missing_skills": missing_skill_counts.most_common(5),
    }


def _average(values: list[int | None]) -> int | None:
    numeric_values = [value for value in values if value is not None]

    if not numeric_values:
        return None

    return round(sum(numeric_values) / len(numeric_values))


def _percentage(part: int, total: int) -> int:
    if total <= 0:
        return 0

    return round((part / total) * 100)
