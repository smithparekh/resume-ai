from job_store import JobApplication


SORT_OPTIONS = (
    "Best Match",
    "Newest Updated",
    "Company",
    "Status",
)


def filter_jobs(
    jobs: list[JobApplication],
    status: str = "All",
    query: str = "",
) -> list[JobApplication]:
    normalized_query = query.strip().lower()
    filtered_jobs = []

    for job in jobs:
        if status != "All" and job.status != status:
            continue

        if normalized_query and normalized_query not in _search_text(job):
            continue

        filtered_jobs.append(job)

    return filtered_jobs


def sort_jobs(jobs: list[JobApplication], sort_by: str = "Best Match") -> list[JobApplication]:
    if sort_by == "Best Match":
        return sorted(jobs, key=_match_sort_key, reverse=True)
    if sort_by == "Company":
        return sorted(jobs, key=lambda job: (job.company.lower(), job.title.lower()))
    if sort_by == "Status":
        return sorted(jobs, key=lambda job: (job.status.lower(), job.company.lower()))

    return sorted(jobs, key=lambda job: job.updated_at, reverse=True)


def jobs_ready_for_analysis(jobs: list[JobApplication]) -> list[JobApplication]:
    return [
        job
        for job in jobs
        if job.description and job.status in {"Saved", "Analyzed"}
    ]


def _match_sort_key(job: JobApplication) -> tuple[int, int, str]:
    return (
        job.match_percentage if job.match_percentage is not None else -1,
        job.resume_score if job.resume_score is not None else -1,
        job.updated_at,
    )


def _search_text(job: JobApplication) -> str:
    return " ".join(
        [
            job.company,
            job.title,
            job.location,
            job.url,
            job.description,
            job.notes,
            job.status,
        ]
    ).lower()
