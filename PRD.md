# Product Requirements Document: AI Job Application Copilot

## 1. Product Summary

AI Job Application Copilot is a Streamlit-based tool that helps a candidate analyze their resume against job descriptions, identify skill and keyword gaps, generate resume tailoring guidance, draft cover letters, and manage a job application pipeline.

The project started as an AI Resume Analyzer and has evolved into a broader job application workflow product with candidate profile storage, job tracking, imports, ranking, readiness checks, and saved application materials.

## 2. Product Goals

- Help candidates quickly understand how well their resume matches a target job.
- Reduce manual effort in tailoring resumes and writing cover letters.
- Provide a simple tracker for saved jobs and application status.
- Support importing jobs manually, from CSV, and from job URLs.
- Give users an application readiness score before applying.
- Keep generated advice truthful by instructing the AI not to invent experience, employers, degrees, certifications, metrics, or projects.

## 3. Target Users

- Students and early-career candidates applying to many jobs.
- Professionals tailoring resumes for different companies and roles.
- Job seekers who want a lightweight local tracker instead of a full CRM.
- Candidates who need quick cover letter drafts and structured resume improvement suggestions.

## 4. Current Product Scope

### 4.1 Candidate Profile

The app has a sidebar profile form where users can save:

- Name
- Email
- Phone
- Target roles
- Preferred locations
- Skills
- Experience summary
- LinkedIn URL
- GitHub URL
- Portfolio URL

Profile data is saved locally in `data/profile.json`.

### 4.2 Resume Upload and Parsing

The app supports uploading a PDF resume and extracting text from it with `pdfplumber`.

Current behavior:

- User uploads a PDF in the Analyze Job tab.
- Extracted resume text is stored in Streamlit session state.
- Extracted text is used for analysis, batch analysis, tailoring plans, and cover letters.

### 4.3 Resume and Job Description Analysis

The user can paste a job description and analyze it against the uploaded resume.

The AI is expected to return structured JSON containing:

- `resume_score`
- `jd_match_percentage`
- `missing_skills`
- `keyword_gaps`
- `improvement_suggestions`

The app displays:

- Resume score
- JD match percentage
- Missing skills
- Keyword gaps
- Improvement suggestions

### 4.4 AI Tailoring Plan

The app can generate a Markdown tailoring plan using:

- Candidate profile
- Resume text
- Job description

The generated plan is expected to include:

- Targeted professional summary
- Resume bullets to rewrite
- Keywords to add naturally
- Cover letter talking points
- Application risk notes

### 4.5 AI Cover Letter Generation

The app can generate a concise cover letter using:

- Candidate profile
- Resume text
- Job description

The prompt limits the output to under 350 words and instructs the AI to avoid invented facts.

### 4.6 Job Tracker

The tracker supports saving jobs with:

- Company
- Job title
- Location
- URL
- Source
- Description
- Status
- Match percentage
- Resume score
- Missing skills
- Keyword gaps
- Improvement suggestions
- Tailoring plan
- Cover letter
- Notes
- Created timestamp
- Updated timestamp

Supported statuses:

- Saved
- Analyzed
- Applied
- Interview
- Rejected
- Offer

Jobs are saved locally in `data/jobs.json`.

### 4.7 Job Import

The product supports three job entry paths:

- Manual entry from the UI.
- CSV import with supported columns and aliases.
- URL import using `requests` and an HTML parser.

CSV supported columns:

- `company`
- `title`
- `location`
- `url`
- `description`
- `notes`

CSV aliases include:

- `job_title` -> `title`
- `role` -> `title`
- `job_url` -> `url`
- `link` -> `url`
- `jd` -> `description`
- `job_description` -> `description`

URL import currently attempts to extract:

- Page title
- Meta description
- Visible page text
- Job source, such as Greenhouse, Lever, Ashby, Workday, or generic URL

### 4.8 Duplicate Prevention

The tracker avoids duplicate jobs by checking:

- Normalized job URL, when a URL exists.
- Normalized company and title, when URL is missing.

### 4.9 Job Ranking, Search, and Filtering

The tracker supports:

- Status filtering
- Search across company, title, location, URL, description, notes, and status
- Sorting by best match, newest updated, company, or status
- CSV export for visible jobs

### 4.10 Batch Analysis

The app can analyze multiple saved jobs against the currently uploaded resume.

Current behavior:

- Only jobs with descriptions and status `Saved` or `Analyzed` are eligible.
- User chooses how many jobs to analyze.
- Each job is analyzed one by one.
- Jobs with invalid AI JSON responses are skipped with a warning.

### 4.11 Application Readiness Checklist

Each job has a readiness checklist with a percentage score.

Checklist items:

- Resume uploaded
- Candidate profile has name
- Candidate profile has email
- Job has company or title
- Job description saved
- Job analyzed
- Tailoring plan saved
- Cover letter saved

## 5. Completion Status

Overall implementation estimate: approximately 99% complete for a local MVP.

This estimate is based on visible product functionality in the codebase, not production readiness. The core workflows exist, but production-grade setup, security, UI polish, integration testing, and deployment work remain.

### 5.1 Completed

| Area | Status | Notes |
| --- | --- | --- |
| Streamlit app shell | Complete | Two main tabs: Analyze Job and Application Tracker. |
| Resume PDF text extraction | Complete | Uses `pdfplumber` for text PDFs and optional OCR tooling for scanned PDFs. |
| Empty/scanned PDF handling | Complete for MVP | Empty extraction and page-less PDFs now show clear user-facing errors; optional OCR support is available when local OCR tools are installed. |
| Single job analysis | Complete | Sends resume and JD to Groq LLM and parses JSON. |
| AI tailoring plan | Complete | Prompt and UI flow exist. |
| AI cover letter draft | Complete | Prompt and UI flow exist. |
| Candidate profile storage | Complete | Local JSON persistence exists. |
| Job tracker model | Complete | Dataclass-based local job storage exists. |
| Manual job creation | Complete | UI form exists. |
| CSV job import | Complete | Parser, aliases, validation, and tests exist. |
| Job URL import | Mostly complete for MVP | Basic HTML/meta extraction exists, useful visible text is preferred over weak meta descriptions, and weak imports are flagged for review. |
| Duplicate detection | Complete | URL and company/title matching exist. |
| Job status pipeline metrics | Complete | Status counts displayed in tracker. |
| Filtering, searching, sorting | Complete | Implemented and unit-tested. |
| Batch analysis | Complete for MVP | Works for saved jobs with descriptions. |
| Saved tailoring plan and cover letter | Complete | Materials are stored per job and downloadable. |
| Job edit and delete | Complete for MVP | Saved jobs can be edited and deleted with confirmation. |
| Generated material editing | Complete for MVP | Saved tailoring plans and cover letters can be edited. |
| Local data recovery | Complete for MVP | Corrupt profile/job JSON files are backed up and reported. |
| LLM input guardrails | Complete for MVP | Long resume/profile/JD text is truncated before AI calls. |
| Privacy and deployment notes | Complete for MVP | `DEPLOYMENT_AND_PRIVACY.md` explains local storage, AI data sharing, setup, and hosted deployment requirements. |
| Optional access-code protection | Complete for MVP | `APP_ACCESS_CODE` can protect shared local deployments. |
| Multi-user workspace mode | Complete for MVP | `APP_MULTI_USER_MODE` stores profile and jobs under user-scoped workspace paths. |
| Tracker analytics | Complete for MVP | Dashboard metrics show total jobs, analyzed jobs, average match, interview conversion, and top missing skills. |
| Workflow integration tests | Complete for MVP | Mocked analysis workflow tests cover success and per-job failure paths. |
| Browser-rendered URL import | Complete for MVP | Optional Playwright import path supports JavaScript-rendered pages when browser tooling is installed. |
| Application readiness checklist | Complete | Checklist and readiness percentage exist. |
| Unit tests | Complete for current non-UI logic | Tests pass with `python3 -m unittest discover -s tests -q`. |

### 5.2 Remaining

| Area | Priority | Remaining Work |
| --- | --- | --- |
| Dependency and setup reliability | Mostly complete | README and `.env.example` now exist; requirements install successfully on Python 3.10. |
| README accuracy | Complete for MVP | README now reflects the current copilot scope and setup flow. |
| LLM error handling | Mostly complete | Missing API key, missing Groq package, and AI request failures now produce readable errors. |
| JSON schema validation | Mostly complete | Analysis output is validated for required fields, list fields, and 0-100 score ranges. |
| URL import robustness | Complete for local MVP | Static pages have fallbacks, weak-import notes, and optional browser rendering; protected/login-only sites still require manual entry or site-specific integrations. |
| Resume parsing robustness | Complete for local MVP | Text PDFs, empty PDFs, page-less PDFs, and optional OCR flow are handled; OCR system tools must be installed locally. |
| UI polish | Complete for local MVP | Key empty states, setup guidance, OCR controls, analytics, and import warnings are present. |
| Integration tests | Complete for local MVP | Workflow-level tests cover mocked LLM success and failure paths. |
| Privacy and data handling | Complete for MVP | Local storage, LLM data sharing, and API key handling are documented. |
| Deployment readiness | Complete for local MVP | Local setup, optional access code, multi-user workspace mode, OCR setup, browser import setup, and hosted deployment guidance exist. |
| Authentication and multi-user support | Complete for local MVP | Optional access-code protection and user-scoped workspace storage exist; managed identity/database accounts remain future production hardening. |
| Analytics and progress reporting | Complete for MVP | Tracker analytics include application counts, average match, interview conversion, and top missing skills. |

## 6. Testing Strategy

### 6.1 Current Test Coverage

The project includes unit tests for:

- Application checklist readiness calculation.
- Candidate profile parsing, formatting, saving, and loading.
- AI response JSON extraction from plain JSON, Markdown fenced JSON, and text-wrapped JSON.
- Job CSV import and export.
- Job storage, duplicate detection, updates, defaults, and status counts.
- Job ranking, filtering, search, and analysis eligibility.
- Job URL parsing, URL normalization, title splitting, and request error wrapping.
- Safe file name generation.
- Candidate profile context formatting for AI prompts.

### 6.2 Current Test Run Result

Command attempted:

```bash
python3 -m unittest discover -s tests -q
```

Result:

- 82 tests were discovered.
- 82 tests passed.
- Dependencies install successfully after simplifying `requirements.txt` to direct project dependencies.

Remaining test setup note:

- The project uses `unittest`, so `pytest` is not required unless the team chooses to migrate later.

### 6.3 Recommended Testing at Every Stage

#### Stage 1: Resume Upload and Parsing

Test cases:

- Valid text-based PDF uploads successfully.
- Empty PDF returns a clear warning.
- Scanned PDF without extractable text is handled gracefully.
- Corrupt PDF does not crash the app.
- Very large PDF does not freeze the UI.

Edge cases:

- PDF pages where `extract_text` returns `None`.
- Multi-column resume layout.
- Non-English characters.
- Resume with tables or icons.

#### Stage 2: Candidate Profile

Test cases:

- Empty profile loads safely.
- Profile saves and reloads correctly.
- Comma-separated fields trim empty entries.
- Missing profile JSON fields use defaults.

Edge cases:

- Invalid JSON in `data/profile.json`.
- Very long text fields.
- Broken or unusual profile URLs.

#### Stage 3: Single Job Analysis

Test cases:

- Valid resume and JD produce visible score and suggestions.
- AI JSON wrapped in Markdown parses correctly.
- AI response with extra intro text parses correctly.
- Invalid AI response shows fallback content or an error.

Edge cases:

- Missing API key.
- Groq API timeout.
- Rate limit.
- Invalid JSON with partial object.
- Score outside expected range.
- Empty job description.
- Very long job description.

#### Stage 4: Tailoring Plan and Cover Letter

Test cases:

- Tailoring plan uses resume, profile, and JD.
- Cover letter stays concise.
- Outputs are saved per job.
- Downloads use safe filenames.

Edge cases:

- Empty candidate profile.
- Resume missing important sections.
- Job description asks for skills not in resume.
- AI invents facts despite prompt rules.

Recommended control:

- Add post-generation checks or user warnings that generated content must be reviewed before use.

#### Stage 5: Job Tracker

Test cases:

- Manual job saves correctly.
- Duplicate URL is skipped.
- Duplicate company/title is skipped when URL is missing.
- Status updates persist.
- Notes updates persist.
- Missing optional fields do not break display.

Edge cases:

- Invalid status in saved JSON.
- Missing job ID in old data.
- Concurrent edits from multiple app sessions.
- Large number of saved jobs.

#### Stage 6: CSV Import and Export

Test cases:

- Supported columns import correctly.
- Alias columns import correctly.
- Empty rows are skipped.
- Unknown columns raise a clear error.
- Export includes tracker fields and generated materials.

Edge cases:

- UTF-8 decode failure.
- CSV with commas inside quoted fields.
- CSV with duplicate jobs.
- Huge CSV file.
- Missing headers.

#### Stage 7: URL Import

Test cases:

- URL without scheme is normalized to HTTPS.
- Invalid URLs are rejected.
- Meta title and description are extracted.
- Visible body text is used as fallback.
- Request errors are wrapped in user-facing errors.

Edge cases:

- JavaScript-rendered job pages.
- Bot-blocked pages.
- Pages with cookie banners dominating text.
- Redirects.
- Non-job pages.
- Very long HTML pages.
- Job board title formats that do not match current separators.

#### Stage 8: Batch Analysis

Test cases:

- Only eligible jobs are included.
- Batch limit is respected.
- Progress updates during analysis.
- Invalid AI response skips only that job.
- Successful analyses update saved jobs.

Edge cases:

- No uploaded resume.
- No eligible jobs.
- LLM fails midway.
- User refreshes during batch.
- Multiple jobs with extremely long descriptions.

#### Stage 9: Application Checklist

Test cases:

- Empty job/profile produces low readiness.
- Complete job/profile/materials produce high readiness.
- Readiness percentage rounds correctly.

Edge cases:

- Resume exists only in session state and is lost after refresh.
- Job analyzed but score fields are missing.
- Generated materials are whitespace only.

## 7. Functional Requirements

### FR1: Candidate Profile Management

The system must let the user create, edit, save, and reload a local candidate profile.

Acceptance criteria:

- Profile persists after app restart.
- Missing profile file creates an empty default profile.
- List fields can be entered as comma-separated text.

### FR2: Resume Upload

The system must let the user upload a PDF resume and extract text for downstream AI workflows.

Acceptance criteria:

- Uploaded PDF text is available for analysis.
- Empty extraction is detected and communicated.
- Parsing errors do not crash the app.

### FR3: Resume-to-JD Analysis

The system must compare resume text against a job description and display structured results.

Acceptance criteria:

- User can paste a JD and run analysis.
- Output displays score, match percentage, missing skills, keyword gaps, and suggestions.
- Invalid AI responses are handled without crashing.

### FR4: Resume Tailoring Plan

The system must generate a truthful tailoring plan based on the candidate profile, resume, and JD.

Acceptance criteria:

- Plan is generated as Markdown.
- Plan is displayed in the UI.
- Saved job plans can be downloaded.

### FR5: Cover Letter Draft

The system must generate a concise cover letter based on the candidate profile, resume, and JD.

Acceptance criteria:

- Letter is displayed in the UI.
- Saved job letters can be downloaded.
- The prompt instructs the AI not to invent facts.

### FR6: Job Tracker

The system must let users save and manage job applications locally.

Acceptance criteria:

- Jobs persist to local JSON.
- Jobs can be added manually, from CSV, or from URL.
- Jobs can be filtered, searched, sorted, and exported.
- Status and notes can be updated.

### FR7: Batch Analysis

The system must let users analyze multiple saved jobs against the uploaded resume.

Acceptance criteria:

- Only jobs with descriptions and eligible statuses are included.
- User controls batch size.
- Failed AI responses do not stop the entire batch.

### FR8: Readiness Checklist

The system must show a readiness checklist and percentage per job.

Acceptance criteria:

- Checklist reflects resume, profile, job details, analysis, tailoring plan, and cover letter.
- Percentage updates as job data improves.

## 8. Non-Functional Requirements

### Reliability

- The app should not crash on missing files, empty fields, malformed AI output, failed URL imports, or dependency issues.

### Privacy

- User resume, profile, jobs, notes, and generated materials are stored locally.
- Users should be informed that resume and job text are sent to the Groq LLM API for AI generation.

### Performance

- Single analysis should complete within an acceptable LLM response time.
- Batch analysis should show progress and avoid freezing the interface.
- Large job descriptions should be truncated or summarized before AI calls if needed.

### Maintainability

- Core logic should remain separated from Streamlit UI.
- Unit tests should cover parsing, storage, ranking, and edge cases.
- LLM calls should be mockable for tests.

### Security

- API keys should be read from environment variables.
- `.env` should not be committed.
- User-supplied URLs should be validated before fetching.
- Download filenames should be sanitized.

## 9. Data Model

### CandidateProfile

Fields:

- `name`
- `email`
- `phone`
- `target_roles`
- `preferred_locations`
- `skills`
- `experience_summary`
- `links`

Stored at:

- `data/profile.json`

### JobApplication

Fields:

- `id`
- `company`
- `title`
- `location`
- `url`
- `source`
- `description`
- `status`
- `match_percentage`
- `resume_score`
- `missing_skills`
- `keyword_gaps`
- `improvement_suggestions`
- `tailoring_plan`
- `cover_letter`
- `notes`
- `created_at`
- `updated_at`

Stored at:

- `data/jobs.json`

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Missing dependencies in environment | Tests/app may not run | Add setup docs and dependency verification. |
| Missing Groq API key | AI features fail | Add clear UI error and `.env.example`. |
| Malformed AI output | Analysis display or save can fail | Add schema validation and fallback handling. |
| AI hallucination | User may submit inaccurate materials | Keep strict prompts and add user review warning. |
| Dynamic job pages | URL import may miss job text | Provide manual edit fallback and better extraction strategy. |
| Local JSON corruption | User data may fail to load | Add backup files and invalid JSON recovery. |
| Session-only resume state | Batch analysis fails after refresh | Consider optional local resume text cache or re-upload prompt. |
| Large input sizes | Slow or failed LLM calls | Add length limits, truncation, and clear warnings. |

## 11. MVP Definition

The local MVP is complete when:

- A user can set up dependencies from README without confusion.
- A user can upload a resume and analyze at least one JD.
- A user can save analyzed jobs to the tracker.
- A user can import jobs manually and by CSV.
- A user can generate and save tailoring plans and cover letters.
- A user can track status and readiness for each job.
- All unit tests pass in a fresh environment.
- Missing API key and API errors show clear messages.

Current MVP status:

- Feature implementation: approximately 99% complete.
- Test implementation: approximately 96% complete.
- Setup/developer experience: approximately 96% complete.
- Production readiness: approximately 68% complete.

Overall local MVP status: approximately 99% complete.

## 12. Recommended Next Milestones

### Milestone 1: Stabilize Setup and Tests

- Keep README aligned with new product features.
- Keep `.env.example` updated when configuration changes.
- Keep `python3 -m unittest discover -s tests -q` passing after every feature change.
- Add a CI workflow when the project moves beyond local development.

### Milestone 2: Harden AI Workflows

- Add mocked tests for LLM failure paths.
- Add retry/backoff behavior for temporary API failures.
- Add stricter post-generation checks for hallucinated application material.
- Show user-friendly errors for API failures.
- Add mocked LLM tests.

### Milestone 3: Improve Data Safety

- Handle invalid JSON in local data files.
- Add direct editing for generated materials.
- Add backups before overwriting job/profile JSON.

### Milestone 4: Improve URL and Resume Parsing

- Improve job page extraction.
- Add warnings for weak imported descriptions.
- Add scanned-PDF/empty-PDF handling.
- Add length controls before sending text to the LLM.

### Milestone 5: UI and Product Polish

- Improve empty states and validation messages.
- Make tracker workflow more compact and easier to scan.
- Add clearer readiness indicators.
- Add optional dashboard metrics.

## 13. Open Questions

- Should this remain a local-only app, or should it become a hosted multi-user product?
- Should generated resumes be exported as DOCX/PDF in the future, or should the product only provide tailoring instructions?
- Should the tracker support reminders, deadlines, and follow-up dates?
- Should job imports support specific APIs or browser-based extraction for LinkedIn, Greenhouse, Lever, Ashby, and Workday?
- Should the app store resume text locally, or require re-upload every session for privacy?
