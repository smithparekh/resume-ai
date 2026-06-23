# Project Checklist

Current local MVP status: approximately 99% complete.

## Completed

- Streamlit app shell with Analyze Job and Application Tracker tabs.
- PDF resume text extraction.
- Clear errors for empty, scanned, or page-less PDFs.
- Candidate profile storage in local JSON.
- Single resume-to-job-description analysis through Groq.
- Structured response parsing and schema validation.
- AI tailored resume draft generation.
- AI cover letter generation.
- Local job tracker model and persistence.
- Manual job creation.
- CSV job import and export.
- Basic URL job import.
- Better URL import fallback for weak meta descriptions.
- Weak URL imports flagged for manual review.
- Duplicate job detection by URL or company/title.
- Job status metrics.
- Search, filter, sort, and visible-job CSV export.
- Batch analysis for eligible saved jobs.
- Saved tailoring plans and cover letters.
- Editing for jobs, generated resumes, and cover letters.
- Delete confirmation for saved jobs.
- Local profile/job JSON corruption backup and recovery.
- LLM input-length guardrails.
- Missing API key, missing package, and AI request error messages.
- Application readiness checklist and percentage.
- Privacy and deployment documentation.
- Optional OCR support path for scanned resumes.
- Optional local access-code protection.
- Tracker analytics for applications, match quality, conversion, and missing skills.
- Workflow-level integration tests with mocked AI responses.
- Clearer empty states and form guidance.
- Optional browser-rendered URL import for JavaScript-heavy job pages.
- Multi-user workspace mode with user-scoped local data files.
- Unit tests for current non-UI logic.

## Remaining

- Production database, managed authentication, monitoring, and backups for a real hosted SaaS deployment.
- Site-specific authenticated job board integrations where scraping is blocked or disallowed.

## Verification

- `python3 -m unittest discover -s tests -q`
- Latest result: 82 tests passed.
