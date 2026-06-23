# AI Job Application Copilot

AI Job Application Copilot is a local Streamlit app for analyzing resumes against job descriptions, generating tailored application materials, and tracking job applications.

## Features

- Upload a PDF resume and extract resume text.
- Compare a resume with a pasted job description using the Groq LLM API.
- View resume score, JD match percentage, missing skills, keyword gaps, and improvement suggestions.
- Save a candidate profile with target roles, locations, skills, links, and experience summary.
- Generate a truthful tailored resume draft for a specific job.
- Generate a concise tailored cover letter draft for a specific job.
- Save jobs to a local application tracker.
- Add jobs manually, import jobs from CSV, or import jobs from URLs.
- Filter, search, sort, and export tracked jobs.
- Run batch analysis across saved jobs.
- View an application readiness checklist for each job.

## Tech Stack

- Python
- Streamlit
- Groq LLM API
- pdfplumber
- requests
- unittest

## Project Status

Current stage: local MVP / prototype.

Estimated completion: about 99% for a local MVP.

Completed:

- Core Streamlit app workflow.
- Resume PDF extraction.
- Single job analysis.
- Candidate profile storage.
- Job tracker with statuses.
- Manual, CSV, and basic URL job import.
- Duplicate job detection.
- Search, filter, sort, and CSV export.
- Batch analysis for saved jobs.
- Tailored resume and cover letter generation.
- Application readiness checklist.
- Job edit and delete controls.
- Editing for saved tailored resumes and cover letters.
- Safer handling for corrupt local profile/job JSON files.
- LLM input-length guardrails.
- Clearer scanned/empty PDF handling.
- Better URL import fallback notes for weak extracted descriptions.
- Privacy and deployment notes.
- Optional OCR path for scanned resumes.
- Optional access-code protection for shared local use.
- Tracker analytics for applications, match quality, conversion, and missing skills.
- Workflow-level integration tests with mocked AI responses.
- Optional browser-rendered URL import for JavaScript-heavy job pages.
- Multi-user workspace mode with user-scoped local data paths.
- Unit tests for most non-UI logic.

Remaining:

- Production database, managed authentication, monitoring, and backups for a real hosted SaaS deployment.
- Site-specific authenticated job board integrations where scraping is blocked or disallowed.

For the detailed PRD, completion estimate, remaining work, testing plan, and edge cases, see `PRD.md`.
For the compact completed/remaining checklist, see `PROJECT_CHECKLIST.md`.
For local data, AI sharing, and deployment notes, see `DEPLOYMENT_AND_PRIVACY.md`.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Add your Groq API key to `.env`:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

## Run the App

```bash
streamlit run app.py
```

The app stores local data in the `data/` folder:

- `data/profile.json`
- `data/jobs.json`

The `data/` folder is ignored by git.

## Run Tests

The tests use Python's built-in `unittest` framework:

```bash
python3 -m unittest discover -s tests -q
```

If imports fail, make sure the virtual environment is active and dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## CSV Import Format

Supported CSV columns:

- `company`
- `title`
- `location`
- `url`
- `description`
- `notes`

Supported aliases:

- `job_title` -> `title`
- `role` -> `title`
- `job_url` -> `url`
- `link` -> `url`
- `jd` -> `description`
- `job_description` -> `description`

Example:

```csv
company,title,location,url,description,notes
Acme,Backend Developer,Remote,https://example.com/job,Build APIs,Good fit
```

## Important Notes

- Resume text, profile data, job records, notes, tailored resumes, and cover letters are stored locally.
- Resume and job description text are sent to the Groq API when using AI features.
- Generated application materials should be reviewed before sending.
- URL import is basic and may not work well for pages that require JavaScript rendering or block automated requests.
