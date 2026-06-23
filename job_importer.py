import csv
from io import StringIO

from job_store import JobApplication


SUPPORTED_COLUMNS = {
    "company",
    "title",
    "location",
    "url",
    "description",
    "notes",
}
COLUMN_ALIASES = {
    "job_title": "title",
    "role": "title",
    "job_url": "url",
    "link": "url",
    "jd": "description",
    "job_description": "description",
}


def parse_jobs_csv(csv_text: str) -> list[JobApplication]:
    reader = csv.DictReader(StringIO(csv_text))

    if not reader.fieldnames:
        return []

    normalized_fieldnames = {_normalize(column) for column in reader.fieldnames}
    if not normalized_fieldnames.intersection(SUPPORTED_COLUMNS):
        raise ValueError("CSV must include at least one supported job column.")

    jobs = []

    for row in reader:
        normalized_row = {_normalize(key): value for key, value in row.items()}

        job = JobApplication(
            company=_clean(normalized_row.get("company")),
            title=_clean(normalized_row.get("title")),
            location=_clean(normalized_row.get("location")),
            url=_clean(normalized_row.get("url")),
            description=_clean(normalized_row.get("description")),
            notes=_clean(normalized_row.get("notes")),
        )

        if job.company or job.title or job.url or job.description:
            jobs.append(job)

    return jobs


def jobs_to_csv(jobs: list[JobApplication]) -> str:
    output = StringIO()
    fieldnames = [
        "company",
        "title",
        "location",
        "url",
        "status",
        "match_percentage",
        "resume_score",
        "missing_skills",
        "keyword_gaps",
        "improvement_suggestions",
        "tailoring_plan",
        "cover_letter",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for job in jobs:
        writer.writerow(
            {
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "url": job.url,
                "status": job.status,
                "match_percentage": job.match_percentage or "",
                "resume_score": job.resume_score or "",
                "missing_skills": "; ".join(job.missing_skills),
                "keyword_gaps": "; ".join(job.keyword_gaps),
                "improvement_suggestions": "; ".join(job.improvement_suggestions),
                "tailoring_plan": job.tailoring_plan,
                "cover_letter": job.cover_letter,
                "notes": job.notes,
            }
        )

    return output.getvalue()


def _normalize(value: str | None) -> str:
    normalized_value = (value or "").strip().lower().replace(" ", "_")
    return COLUMN_ALIASES.get(normalized_value, normalized_value)


def _clean(value: str | None) -> str:
    return (value or "").strip()
