import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


DEFAULT_JOBS_PATH = Path("data/jobs.json")
VALID_STATUSES = ("Saved", "Analyzed", "Applied", "Interview", "Rejected", "Offer")


class JobStoreError(Exception):
    pass


@dataclass
class JobApplication:
    id: str = field(default_factory=lambda: uuid4().hex)
    company: str = ""
    title: str = ""
    location: str = ""
    url: str = ""
    source: str = ""
    description: str = ""
    status: str = "Saved"
    match_percentage: int | None = None
    resume_score: int | None = None
    missing_skills: list[str] = field(default_factory=list)
    keyword_gaps: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
    tailoring_plan: str = ""
    cover_letter: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: utc_now())
    updated_at: str = field(default_factory=lambda: utc_now())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_jobs(path: str | Path = DEFAULT_JOBS_PATH) -> list[JobApplication]:
    jobs_path = Path(path)

    if not jobs_path.exists():
        return []

    try:
        with jobs_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        backup_path = _backup_corrupt_file(jobs_path)
        raise JobStoreError(
            f"Could not read saved jobs. The corrupt file was backed up to {backup_path}."
        ) from error

    if not isinstance(data, list):
        backup_path = _backup_corrupt_file(jobs_path)
        raise JobStoreError(
            f"Saved jobs must be a list. The invalid file was backed up to {backup_path}."
        )

    return [_job_from_dict(item) for item in data]


def save_jobs(jobs: list[JobApplication], path: str | Path = DEFAULT_JOBS_PATH) -> None:
    jobs_path = Path(path)
    jobs_path.parent.mkdir(parents=True, exist_ok=True)

    with jobs_path.open("w", encoding="utf-8") as file:
        json.dump([asdict(job) for job in jobs], file, indent=2)
        file.write("\n")


def add_job(job: JobApplication, path: str | Path = DEFAULT_JOBS_PATH) -> JobApplication:
    jobs = load_jobs(path)
    job.updated_at = utc_now()
    jobs.append(job)
    save_jobs(jobs, path)
    return job


def add_job_if_new(job: JobApplication, path: str | Path = DEFAULT_JOBS_PATH) -> JobApplication | None:
    jobs = load_jobs(path)

    if is_duplicate_job(job, jobs):
        return None

    job.updated_at = utc_now()
    jobs.append(job)
    save_jobs(jobs, path)
    return job


def is_duplicate_job(job: JobApplication, jobs: list[JobApplication]) -> bool:
    normalized_url = _normalize_url(job.url)

    if normalized_url:
        return any(_normalize_url(existing_job.url) == normalized_url for existing_job in jobs)

    normalized_identity = _normalize_identity(job.company, job.title)

    if not normalized_identity:
        return False

    return any(
        _normalize_identity(existing_job.company, existing_job.title) == normalized_identity
        for existing_job in jobs
    )


def update_job(updated_job: JobApplication, path: str | Path = DEFAULT_JOBS_PATH) -> JobApplication:
    jobs = load_jobs(path)

    for index, job in enumerate(jobs):
        if job.id == updated_job.id:
            updated_job.created_at = job.created_at
            updated_job.updated_at = utc_now()
            jobs[index] = updated_job
            save_jobs(jobs, path)
            return updated_job

    raise ValueError(f"Job not found: {updated_job.id}")


def delete_job(job_id: str, path: str | Path = DEFAULT_JOBS_PATH) -> bool:
    jobs = load_jobs(path)
    remaining_jobs = [job for job in jobs if job.id != job_id]

    if len(remaining_jobs) == len(jobs):
        return False

    save_jobs(remaining_jobs, path)
    return True


def apply_analysis(job: JobApplication, analysis: dict) -> JobApplication:
    job.status = "Analyzed"
    job.resume_score = _optional_int(analysis.get("resume_score"))
    job.match_percentage = _optional_int(analysis.get("jd_match_percentage"))
    job.missing_skills = _string_list(analysis.get("missing_skills"))
    job.keyword_gaps = _string_list(analysis.get("keyword_gaps"))
    job.improvement_suggestions = _string_list(analysis.get("improvement_suggestions"))
    return job


def apply_tailoring_plan(job: JobApplication, tailoring_plan: str) -> JobApplication:
    job.tailoring_plan = tailoring_plan.strip()
    return job


def apply_cover_letter(job: JobApplication, cover_letter: str) -> JobApplication:
    job.cover_letter = cover_letter.strip()
    return job


def status_counts(jobs: list[JobApplication]) -> dict[str, int]:
    counts = {status: 0 for status in VALID_STATUSES}

    for job in jobs:
        if job.status not in counts:
            counts[job.status] = 0
        counts[job.status] += 1

    return counts


def _job_from_dict(data: dict) -> JobApplication:
    return JobApplication(
        id=data.get("id") or uuid4().hex,
        company=data.get("company", ""),
        title=data.get("title", ""),
        location=data.get("location", ""),
        url=data.get("url", ""),
        source=data.get("source", ""),
        description=data.get("description", ""),
        status=data.get("status", "Saved"),
        match_percentage=_optional_int(data.get("match_percentage")),
        resume_score=_optional_int(data.get("resume_score")),
        missing_skills=_string_list(data.get("missing_skills")),
        keyword_gaps=_string_list(data.get("keyword_gaps")),
        improvement_suggestions=_string_list(data.get("improvement_suggestions")),
        tailoring_plan=data.get("tailoring_plan", ""),
        cover_letter=data.get("cover_letter", ""),
        notes=data.get("notes", ""),
        created_at=data.get("created_at") or utc_now(),
        updated_at=data.get("updated_at") or utc_now(),
    )


def _optional_int(value) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _string_list(value) -> list[str]:
    if not value:
        return []
    return [str(item) for item in value]


def _normalize_url(url: str) -> str:
    return url.strip().lower().rstrip("/")


def _normalize_identity(company: str, title: str) -> str:
    cleaned_company = " ".join(company.lower().split())
    cleaned_title = " ".join(title.lower().split())

    if not cleaned_company or not cleaned_title:
        return ""

    return f"{cleaned_company}|{cleaned_title}"


def _backup_corrupt_file(path: Path) -> Path:
    backup_path = path.with_suffix(f"{path.suffix}.corrupt.{utc_now().replace(':', '-')}")
    shutil.copy(path, backup_path)
    return backup_path
