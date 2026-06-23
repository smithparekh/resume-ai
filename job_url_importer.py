from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

from job_board_integrations import (
    JobBoardIntegrationError,
    UnsupportedJobBoardError,
    fetch_job_with_integration,
)
from job_store import JobApplication


DEFAULT_TIMEOUT_SECONDS = 15
MAX_DESCRIPTION_CHARS = 12000
MIN_USEFUL_DESCRIPTION_CHARS = 120


class JobPageFetchError(Exception):
    pass


class JobPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta = {}
        self.text_parts = []
        self._current_tag = ""
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self._current_tag = tag

        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1

        if tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            content = attributes.get("content")

            if key and content:
                self.meta[key.lower()] = content.strip()

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

        self._current_tag = ""

    def handle_data(self, data):
        cleaned_data = " ".join(data.split())

        if not cleaned_data:
            return

        if self._current_tag == "title" and not self.title:
            self.title = cleaned_data

        if not self._skip_depth:
            self.text_parts.append(cleaned_data)


def fetch_job_from_url(
    url: str,
    use_browser: bool = False,
    use_job_board_integration: bool = True,
) -> JobApplication:
    normalized_url = normalize_url(url)

    if use_job_board_integration:
        try:
            return fetch_job_with_integration(normalized_url, DEFAULT_TIMEOUT_SECONDS)
        except UnsupportedJobBoardError:
            pass
        except JobBoardIntegrationError as error:
            if not use_browser:
                raise JobPageFetchError(str(error)) from error

    if use_browser:
        return fetch_job_from_url_with_browser(normalized_url)

    try:
        response = requests.get(
            normalized_url,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            headers={"User-Agent": "resume-ai-job-copilot/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise JobPageFetchError(str(error)) from error

    return parse_job_page(normalized_url, response.text)


def fetch_job_from_url_with_browser(url: str) -> JobApplication:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise JobPageFetchError(
            "Browser import requires Playwright. Install it with: pip install playwright && playwright install chromium"
        ) from error

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(user_agent="resume-ai-job-copilot/1.0")
            page.goto(url, wait_until="networkidle", timeout=DEFAULT_TIMEOUT_SECONDS * 1000)
            html = page.content()
            browser.close()
    except Exception as error:
        raise JobPageFetchError(f"Browser import failed: {error}") from error

    job = parse_job_page(url, html)
    job.notes = f"{job.notes}. Imported with browser rendering."
    return job


def parse_job_page(url: str, html: str) -> JobApplication:
    parser = JobPageParser()
    parser.feed(html)

    title = _first_present(
        parser.meta.get("og:title"),
        parser.meta.get("twitter:title"),
        parser.title,
    )
    description = _choose_description(
        parser.meta.get("description"),
        parser.meta.get("og:description"),
        " ".join(parser.text_parts),
    )

    company, job_title = split_title(title, url)
    notes = "Imported from URL"

    if len(description) < MIN_USEFUL_DESCRIPTION_CHARS:
        notes += ". Review imported details; this page may require JavaScript or manual cleanup."

    return JobApplication(
        company=company,
        title=job_title,
        url=url,
        source=detect_job_source(url),
        description=description[:MAX_DESCRIPTION_CHARS],
        notes=notes,
    )


def parse_urls(value: str) -> list[str]:
    urls = []

    for line in value.splitlines():
        cleaned_line = line.strip()
        if cleaned_line:
            urls.append(normalize_url(cleaned_line))

    return urls


def normalize_url(url: str) -> str:
    cleaned_url = url.strip()

    if not cleaned_url or any(character.isspace() for character in cleaned_url):
        raise ValueError(f"Invalid URL: {url}")

    parsed_url = urlparse(cleaned_url)

    if not parsed_url.scheme:
        cleaned_url = f"https://{cleaned_url}"

    parsed_url = urlparse(cleaned_url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {url}")

    return cleaned_url


def split_title(title: str, url: str) -> tuple[str, str]:
    cleaned_title = title.strip()
    separators = [" | ", " - ", " at "]

    for separator in separators:
        if separator in cleaned_title:
            left, right = cleaned_title.split(separator, 1)

            if separator == " at ":
                return right.strip(), left.strip()

            return right.strip(), left.strip()

    domain = urlparse(url).netloc.replace("www.", "")
    return domain, cleaned_title


def detect_job_source(url: str) -> str:
    parsed_url = urlparse(url)
    host = parsed_url.netloc.lower()
    path = parsed_url.path.lower()

    if "greenhouse.io" in host or "greenhouse" in path:
        return "Greenhouse"
    if "lever.co" in host or "lever" in path:
        return "Lever"
    if "ashbyhq.com" in host or "ashby" in path:
        return "Ashby"
    if "workdayjobs.com" in host or "myworkdayjobs.com" in host:
        return "Workday"

    return "URL"


def _first_present(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return " ".join(value.split())

    return ""


def _choose_description(*values: str | None) -> str:
    cleaned_values = [" ".join(value.split()) for value in values if value and value.strip()]

    for value in cleaned_values:
        if len(value) >= MIN_USEFUL_DESCRIPTION_CHARS:
            return value

    return cleaned_values[0] if cleaned_values else ""
