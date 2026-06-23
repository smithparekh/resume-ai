from urllib.parse import urlparse

import requests

from job_store import JobApplication


class JobBoardIntegrationError(Exception):
    pass


class UnsupportedJobBoardError(JobBoardIntegrationError):
    pass


def fetch_job_with_integration(url: str, timeout_seconds: int = 15) -> JobApplication:
    source = detect_supported_job_board(url)

    if source == "Greenhouse":
        return fetch_greenhouse_job(url, timeout_seconds)
    if source == "Lever":
        return fetch_lever_job(url, timeout_seconds)
    if source == "Ashby":
        return fetch_ashby_job(url, timeout_seconds)

    raise UnsupportedJobBoardError(f"No supported job board integration for {url}")


def detect_supported_job_board(url: str) -> str:
    parsed_url = urlparse(url)
    host = parsed_url.netloc.lower()

    if "greenhouse.io" in host:
        return "Greenhouse"
    if "lever.co" in host:
        return "Lever"
    if "ashbyhq.com" in host:
        return "Ashby"

    return ""


def fetch_greenhouse_job(url: str, timeout_seconds: int = 15) -> JobApplication:
    board_token, job_id = _greenhouse_parts(url)

    if not board_token or not job_id:
        raise UnsupportedJobBoardError("Greenhouse URL does not include a board token and job id.")

    api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
    data = _get_json(api_url, timeout_seconds)

    return JobApplication(
        company=data.get("company_name", "") or board_token,
        title=data.get("title", ""),
        location=_greenhouse_location(data),
        url=url,
        source="Greenhouse",
        description=_greenhouse_description(data),
        notes="Imported from Greenhouse API",
    )


def fetch_lever_job(url: str, timeout_seconds: int = 15) -> JobApplication:
    company, posting_id = _lever_parts(url)

    if not company or not posting_id:
        raise UnsupportedJobBoardError("Lever URL does not include a company and posting id.")

    api_url = f"https://api.lever.co/v0/postings/{company}/{posting_id}"
    data = _get_json(api_url, timeout_seconds)

    return JobApplication(
        company=company,
        title=data.get("text", ""),
        location=(data.get("categories") or {}).get("location", ""),
        url=url,
        source="Lever",
        description=_lever_description(data),
        notes="Imported from Lever API",
    )


def fetch_ashby_job(url: str, timeout_seconds: int = 15) -> JobApplication:
    company, job_id = _ashby_parts(url)

    if not company or not job_id:
        raise UnsupportedJobBoardError("Ashby URL does not include a company slug and job id.")

    api_url = f"https://api.ashbyhq.com/posting-api/job-board/{company}"
    data = _get_json(api_url, timeout_seconds)

    jobs = data.get("jobs") or []
    job = next(
        (j for j in jobs if isinstance(j, dict) and job_id.lower() in (j.get("jobUrl") or "").lower()),
        None,
    )

    if job is None:
        raise JobBoardIntegrationError(f"Job '{job_id}' not found in Ashby board for '{company}'.")

    return JobApplication(
        company=data.get("organizationName") or company,
        title=job.get("title", ""),
        location=job.get("location", ""),
        url=url,
        source="Ashby",
        description=_ashby_description(job),
        notes="Imported from Ashby API",
    )


def _get_json(url: str, timeout_seconds: int) -> dict:
    try:
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        raise JobBoardIntegrationError(str(error)) from error
    except ValueError as error:
        raise JobBoardIntegrationError("Job board API returned invalid JSON.") from error

    if not isinstance(data, dict):
        raise JobBoardIntegrationError("Job board API returned an unexpected response.")

    return data


def _greenhouse_parts(url: str) -> tuple[str, str]:
    parsed_url = urlparse(url)
    parts = [part for part in parsed_url.path.split("/") if part]

    if len(parts) >= 3 and parts[-2] == "jobs":
        return parts[-3], parts[-1]

    return "", ""


def _lever_parts(url: str) -> tuple[str, str]:
    parsed_url = urlparse(url)
    parts = [part for part in parsed_url.path.split("/") if part]

    if len(parts) >= 2:
        return parts[0], parts[-1]

    return "", ""


def _greenhouse_location(data: dict) -> str:
    location = data.get("location") or {}

    if isinstance(location, dict):
        return location.get("name", "")

    return str(location)


def _ashby_parts(url: str) -> tuple[str, str]:
    parsed_url = urlparse(url)
    parts = [part for part in parsed_url.path.split("/") if part]

    if len(parts) >= 2:
        return parts[0], parts[-1]

    return "", ""


def _ashby_description(job: dict) -> str:
    content = job.get("descriptionPlain") or job.get("descriptionHtml") or ""
    return " ".join(str(content).split())


def _greenhouse_description(data: dict) -> str:
    content = data.get("content") or data.get("description") or ""
    return " ".join(str(content).split())


def _lever_description(data: dict) -> str:
    parts = [data.get("descriptionPlain", ""), data.get("additionalPlain", "")]
    lists = data.get("lists") or []

    for item in lists:
        if not isinstance(item, dict):
            continue
        parts.append(item.get("text", ""))
        parts.extend(content.get("text", "") for content in item.get("content", []) if isinstance(content, dict))

    return " ".join(" ".join(str(part).split()) for part in parts if part)
