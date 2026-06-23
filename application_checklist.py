from dataclasses import dataclass

from job_store import JobApplication
from profile_store import CandidateProfile


@dataclass(frozen=True)
class ChecklistItem:
    label: str
    is_ready: bool


def build_application_checklist(
    job: JobApplication,
    profile: CandidateProfile,
    has_resume: bool,
) -> list[ChecklistItem]:
    return [
        ChecklistItem("Resume uploaded", has_resume),
        ChecklistItem("Candidate profile has name", bool(profile.name.strip())),
        ChecklistItem("Candidate profile has email", bool(profile.email.strip())),
        ChecklistItem("Job has company or title", bool(job.company.strip() or job.title.strip())),
        ChecklistItem("Job description saved", bool(job.description.strip())),
        ChecklistItem("Job analyzed", job.match_percentage is not None or job.resume_score is not None),
        ChecklistItem("Tailoring plan saved", bool(job.tailoring_plan.strip())),
        ChecklistItem("Cover letter saved", bool(job.cover_letter.strip())),
    ]


def readiness_percentage(items: list[ChecklistItem]) -> int:
    if not items:
        return 0

    ready_count = sum(1 for item in items if item.is_ready)
    return round((ready_count / len(items)) * 100)
