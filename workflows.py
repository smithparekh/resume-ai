from collections.abc import Callable

from job_store import JobApplication, apply_analysis
from response_parser import parse_json_object, validate_analysis_response


def parse_analysis_result(result: str) -> dict:
    return validate_analysis_response(parse_json_object(result))


def analyze_job_with_llm(
    job: JobApplication,
    resume_text: str,
    analyzer: Callable[[str, str], str],
) -> JobApplication:
    result = analyzer(resume_text, job.description)
    analysis = parse_analysis_result(result)
    return apply_analysis(job, analysis)


def analyze_jobs_batch(
    jobs: list[JobApplication],
    resume_text: str,
    analyzer: Callable[[str, str], str],
) -> tuple[list[JobApplication], list[tuple[JobApplication, Exception]]]:
    analyzed_jobs = []
    failures = []

    for job in jobs:
        try:
            analyzed_jobs.append(analyze_job_with_llm(job, resume_text, analyzer))
        except Exception as error:
            failures.append((job, error))

    return analyzed_jobs, failures
