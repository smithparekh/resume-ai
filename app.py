import os

import streamlit as st
from analytics import build_tracker_metrics
from application_checklist import build_application_checklist, readiness_percentage
from app_logging import app_logger, configure_logging
from auth import (
    access_code_matches,
    is_auth_enabled,
    is_managed_auth_required,
    user_id_from_headers,
)
from backup_manager import backup_paths
from file_names import safe_file_stem
from parser import ResumeParseError, extract_text_from_pdf
from llm import LLMError, analyze_resume, generate_cover_letter, tailor_resume
from job_importer import jobs_to_csv, parse_jobs_csv
from job_ranker import SORT_OPTIONS, filter_jobs, jobs_ready_for_analysis, sort_jobs
from job_url_importer import JobPageFetchError, fetch_job_from_url, parse_urls
from job_store import (
    JobStoreError,
    VALID_STATUSES,
    JobApplication,
    add_job_if_new,
    apply_analysis,
    apply_cover_letter,
    apply_tailoring_plan,
    delete_job,
    load_jobs,
    status_counts,
    update_job,
)
from profile_store import (
    CandidateProfile,
    ProfileStoreError,
    format_list,
    load_profile,
    parse_list,
    save_profile,
)
from resume_tailor import build_profile_context
from storage_context import (
    database_path,
    is_multi_user_mode,
    resolve_storage_paths,
    sanitize_workspace_id,
    storage_backend,
)
from workflows import analyze_job_with_llm, parse_analysis_result
import sqlite_store

st.set_page_config(page_title="AI Job Application Copilot", layout="wide")
st.title("AI Job Application Copilot")
configure_logging()
logger = app_logger()

managed_user_id = user_id_from_headers(getattr(getattr(st, "context", None), "headers", None))

if is_managed_auth_required() and not managed_user_id:
    logger.warning("Managed authentication required but no user header was provided.")
    st.error("Managed authentication is required but no authenticated user header was provided.")
    st.stop()

if managed_user_id:
    st.session_state["workspace_id"] = sanitize_workspace_id(managed_user_id)

if is_auth_enabled() and not st.session_state.get("authenticated"):
    st.subheader("Access")
    access_code = st.text_input("Access code", type="password")
    if st.button("Unlock"):
        if access_code_matches(access_code):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid access code.")
    st.stop()

if is_multi_user_mode() and not st.session_state.get("workspace_id"):
    st.subheader("Workspace")
    workspace_id = st.text_input("Workspace ID")
    if st.button("Open Workspace"):
        sanitized_workspace_id = sanitize_workspace_id(workspace_id)
        if sanitized_workspace_id:
            st.session_state["workspace_id"] = sanitized_workspace_id
            st.rerun()
        else:
            st.error("Enter a valid workspace ID.")
    st.stop()

WORKSPACE_ID = st.session_state.get("workspace_id", "default")
PROFILE_PATH, JOBS_PATH = resolve_storage_paths(st.session_state.get("workspace_id", ""))
STORAGE_BACKEND = storage_backend()
DATABASE_PATH = database_path()


def load_current_profile() -> CandidateProfile:
    if STORAGE_BACKEND == "sqlite":
        return sqlite_store.load_profile(WORKSPACE_ID, DATABASE_PATH)

    return load_profile(PROFILE_PATH)


def save_current_profile(profile: CandidateProfile) -> None:
    if STORAGE_BACKEND == "sqlite":
        sqlite_store.save_profile(profile, WORKSPACE_ID, DATABASE_PATH)
        return

    save_profile(profile, PROFILE_PATH)


def load_current_jobs() -> list[JobApplication]:
    if STORAGE_BACKEND == "sqlite":
        return sqlite_store.load_jobs(WORKSPACE_ID, DATABASE_PATH)

    return load_jobs(JOBS_PATH)


def add_current_job_if_new(job: JobApplication) -> JobApplication | None:
    if STORAGE_BACKEND == "sqlite":
        return sqlite_store.add_job_if_new(job, WORKSPACE_ID, DATABASE_PATH)

    return add_job_if_new(job, JOBS_PATH)


def update_current_job(job: JobApplication) -> JobApplication:
    if STORAGE_BACKEND == "sqlite":
        return sqlite_store.update_job(job, WORKSPACE_ID, DATABASE_PATH)

    return update_job(job, JOBS_PATH)


def delete_current_job(job_id: str) -> bool:
    if STORAGE_BACKEND == "sqlite":
        return sqlite_store.delete_job(job_id, WORKSPACE_ID, DATABASE_PATH)

    return delete_job(job_id, JOBS_PATH)

try:
    profile = load_current_profile()
except ProfileStoreError as error:
    st.error(str(error))
    profile = CandidateProfile()


def current_profile() -> CandidateProfile:
    try:
        return load_current_profile()
    except ProfileStoreError as error:
        st.error(str(error))
        return CandidateProfile()


def current_jobs() -> list[JobApplication]:
    try:
        return load_current_jobs()
    except JobStoreError as error:
        st.error(str(error))
        return []

with st.sidebar:
    st.header("Candidate Profile")
    st.subheader("Setup")
    if os.getenv("GROQ_API_KEY"):
        st.success("Groq API key loaded.")
    else:
        st.warning("Add GROQ_API_KEY to .env to enable AI features.")

    if is_auth_enabled():
        st.info("Access code protection is enabled.")
    if managed_user_id:
        st.info("Managed authentication is active.")
    st.caption(f"Storage: {STORAGE_BACKEND}")

    if st.button("Create Data Backup"):
        backup_targets = [DATABASE_PATH] if STORAGE_BACKEND == "sqlite" else [PROFILE_PATH, JOBS_PATH]
        backups = backup_paths(backup_targets)
        if backups:
            logger.info("Created data backups: %s", ", ".join(str(path) for path in backups))
            st.success(f"Created {len(backups)} backup file(s).")
        else:
            st.info("No data files found to back up yet.")

    with st.form("candidate_profile_form"):
        name = st.text_input("Name", value=profile.name)
        email = st.text_input("Email", value=profile.email)
        phone = st.text_input("Phone", value=profile.phone)
        target_roles = st.text_input(
            "Target roles",
            value=format_list(profile.target_roles),
            placeholder="Backend Developer, AI Engineer",
        )
        preferred_locations = st.text_input(
            "Preferred locations",
            value=format_list(profile.preferred_locations),
            placeholder="Bengaluru, Remote",
        )
        skills = st.text_input(
            "Skills",
            value=format_list(profile.skills),
            placeholder="Python, FastAPI, SQL, LLM",
        )
        experience_summary = st.text_area(
            "Experience summary",
            value=profile.experience_summary,
        )
        linkedin = st.text_input("LinkedIn URL", value=profile.links.get("linkedin", ""))
        github = st.text_input("GitHub URL", value=profile.links.get("github", ""))
        portfolio = st.text_input("Portfolio URL", value=profile.links.get("portfolio", ""))

        if st.form_submit_button("Save Profile"):
            updated_profile = CandidateProfile(
                name=name.strip(),
                email=email.strip(),
                phone=phone.strip(),
                target_roles=parse_list(target_roles),
                preferred_locations=parse_list(preferred_locations),
                skills=parse_list(skills),
                experience_summary=experience_summary.strip(),
                links={
                    "linkedin": linkedin.strip(),
                    "github": github.strip(),
                    "portfolio": portfolio.strip(),
                },
            )
            save_current_profile(updated_profile)
            st.success("Profile saved.")

analyze_tab, tracker_tab = st.tabs(["Analyze Job", "Application Tracker"])

with analyze_tab:
    resume_file = st.file_uploader("Upload Resume (PDF)")
    enable_ocr = st.checkbox(
        "Use OCR for scanned PDF",
        help="Requires optional pdf2image and pytesseract setup.",
    )
    jd_text = st.text_area("Paste Job Description", height=220)
    resume_text = st.session_state.get("last_resume_text", "")
    resume_parse_failed = False

    if resume_file:
        try:
            resume_text = extract_text_from_pdf(resume_file, enable_ocr=enable_ocr)
        except ResumeParseError as error:
            resume_text = ""
            resume_parse_failed = True
            st.error(str(error))

        if resume_text.strip():
            st.session_state["last_resume_text"] = resume_text
            st.success("Resume text extracted.")
        elif not resume_parse_failed:
            st.warning("Could not extract readable text from this resume PDF.")

    if not resume_file:
        st.info("Upload a PDF resume to unlock analysis, tailoring, and batch matching.")
    if resume_file and not jd_text:
        st.info("Paste a job description to analyze this resume.")

    if resume_file and jd_text:
        if st.button("Analyze Resume", disabled=not resume_text.strip()):
            with st.spinner("Analyzing with AI..."):
                try:
                    result = analyze_resume(resume_text, jd_text)
                except LLMError as error:
                    st.error(str(error))
                    result = ""

            if result:
                try:
                    st.session_state["analysis_data"] = parse_analysis_result(result)
                    st.session_state["analysis_raw"] = ""
                    st.session_state["last_jd_text"] = jd_text
                except ValueError as error:
                    st.session_state["analysis_data"] = None
                    st.session_state["analysis_raw"] = result
                    st.session_state["last_jd_text"] = jd_text
                    st.error(str(error))

    analysis_data = st.session_state.get("analysis_data")
    analysis_raw = st.session_state.get("analysis_raw")

    if analysis_data:
        st.subheader("AI Analysis")
        score_col, match_col = st.columns(2)
        score_col.metric("Resume Score", analysis_data["resume_score"])
        match_col.metric("JD Match %", analysis_data["jd_match_percentage"])

        st.subheader("Missing Skills")
        for skill in analysis_data["missing_skills"]:
            st.write("-", skill)

        st.subheader("Keyword Gaps")
        for keyword in analysis_data["keyword_gaps"]:
            st.write("-", keyword)

        st.subheader("Improvement Suggestions")
        for suggestion in analysis_data["improvement_suggestions"]:
            st.write("-", suggestion)

        if st.button("Generate Tailored Resume"):
            with st.spinner("Writing tailored resume..."):
                try:
                    st.session_state["tailoring_plan"] = tailor_resume(
                        st.session_state.get("last_resume_text", ""),
                        st.session_state.get("last_jd_text", ""),
                        build_profile_context(current_profile()),
                    )
                except LLMError as error:
                    st.error(str(error))

        if st.session_state.get("tailoring_plan"):
            st.subheader("Tailored Resume Draft")
            st.markdown(st.session_state["tailoring_plan"])

        if st.button("Generate Cover Letter"):
            with st.spinner("Writing cover letter..."):
                try:
                    st.session_state["cover_letter"] = generate_cover_letter(
                        st.session_state.get("last_resume_text", ""),
                        st.session_state.get("last_jd_text", ""),
                        build_profile_context(current_profile()),
                    )
                except LLMError as error:
                    st.error(str(error))

        if st.session_state.get("cover_letter"):
            st.subheader("Cover Letter Draft")
            st.text_area(
                "Draft",
                value=st.session_state["cover_letter"],
                height=300,
            )

        st.subheader("Save to Tracker")
        with st.form("save_analyzed_job_form"):
            company = st.text_input("Company")
            title = st.text_input("Job title")
            location = st.text_input("Location")
            url = st.text_input("Job URL")
            notes = st.text_area("Notes")

            if st.form_submit_button("Save Job"):
                job = JobApplication(
                    company=company.strip(),
                    title=title.strip(),
                    location=location.strip(),
                    url=url.strip(),
                    description=st.session_state.get("last_jd_text", ""),
                    tailoring_plan=st.session_state.get("tailoring_plan", ""),
                    cover_letter=st.session_state.get("cover_letter", ""),
                    notes=notes.strip(),
                )
                added_job = add_current_job_if_new(apply_analysis(job, analysis_data))
                if added_job:
                    st.success("Job saved to tracker.")
                else:
                    st.info("This job already exists in the tracker.")

    elif analysis_raw:
        st.subheader("AI Analysis")
        st.write(analysis_raw)

with tracker_tab:
    with st.expander("Import Jobs From URLs"):
        urls_text = st.text_area(
            "Job URLs",
            placeholder="https://company.com/careers/job-1\nhttps://another-company.com/jobs/job-2",
            height=120,
        )
        use_browser_import = st.checkbox(
            "Use browser rendering",
            help="For JavaScript-heavy job pages. Requires optional Playwright setup.",
        )

        if st.button("Fetch Job URLs"):
            try:
                urls = parse_urls(urls_text)
            except ValueError as error:
                st.error(str(error))
                urls = []

            if not urls:
                st.warning("Add at least one valid job URL.")
            else:
                imported_count = 0
                skipped_count = 0
                failed_urls = []

                for url in urls:
                    try:
                        if add_current_job_if_new(fetch_job_from_url(url, use_browser=use_browser_import)):
                            imported_count += 1
                        else:
                            skipped_count += 1
                    except JobPageFetchError as error:
                        failed_urls.append(f"{url}: {error}")

                if imported_count:
                    st.success(f"Imported {imported_count} job(s) from URL.")
                if skipped_count:
                    st.info(f"Skipped {skipped_count} duplicate job(s).")
                if failed_urls:
                    st.warning("Some URLs could not be imported.")
                    for failed_url in failed_urls:
                        st.write("-", failed_url)

    with st.expander("Import Jobs CSV"):
        jobs_file = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            help="Supported columns: company, title, location, url, description, notes.",
        )

        if jobs_file and st.button("Import Jobs"):
            try:
                imported_jobs = parse_jobs_csv(jobs_file.getvalue().decode("utf-8"))
                imported_count = 0
                for imported_job in imported_jobs:
                    if add_current_job_if_new(imported_job):
                        imported_count += 1
                skipped_count = len(imported_jobs) - imported_count
                st.success(f"Imported {imported_count} job(s).")
                if skipped_count:
                    st.info(f"Skipped {skipped_count} duplicate job(s).")
            except UnicodeDecodeError:
                st.error("Could not read this CSV as UTF-8 text.")
            except ValueError as error:
                st.error(str(error))

    with st.expander("Add Job Manually"):
        with st.form("manual_job_form"):
            manual_company = st.text_input("Company", key="manual_company")
            manual_title = st.text_input("Job title", key="manual_title")
            manual_location = st.text_input("Location", key="manual_location")
            manual_url = st.text_input("Job URL", key="manual_url")
            manual_description = st.text_area(
                "Job description",
                height=180,
                key="manual_description",
            )
            manual_notes = st.text_area("Notes", key="manual_notes")

            if st.form_submit_button("Add Job"):
                if not manual_company.strip() and not manual_title.strip():
                    st.error("Add at least a company or job title.")
                else:
                    added_job = add_current_job_if_new(
                        JobApplication(
                            company=manual_company.strip(),
                            title=manual_title.strip(),
                            location=manual_location.strip(),
                            url=manual_url.strip(),
                            description=manual_description.strip(),
                            notes=manual_notes.strip(),
                        )
                    )
                    if added_job:
                        st.success("Job added.")
                    else:
                        st.info("This job already exists in the tracker.")

    jobs = current_jobs()
    counts = status_counts(jobs)
    ready_jobs = jobs_ready_for_analysis(jobs)
    tracker_metrics = build_tracker_metrics(jobs)

    st.subheader("Pipeline")
    metric_columns = st.columns(len(VALID_STATUSES))
    for column, status in zip(metric_columns, VALID_STATUSES):
        column.metric(status, counts[status])

    st.subheader("Analytics")
    analytics_columns = st.columns(4)
    analytics_columns[0].metric("Total Jobs", tracker_metrics["total_jobs"])
    analytics_columns[1].metric("Analyzed", tracker_metrics["analyzed_jobs"])
    average_match = tracker_metrics["average_match"]
    analytics_columns[2].metric("Avg Match", average_match if average_match is not None else "N/A")
    analytics_columns[3].metric("Interview Conversion", f"{tracker_metrics['interview_conversion']}%")

    if tracker_metrics["top_missing_skills"]:
        st.caption(
            "Top missing skills: "
            + ", ".join(
                f"{skill} ({count})"
                for skill, count in tracker_metrics["top_missing_skills"]
            )
        )

    st.subheader("Batch Analysis")
    st.write(f"{len(ready_jobs)} saved/analyzed job(s) have descriptions and can be analyzed.")

    batch_limit = st.number_input(
        "Jobs to analyze now",
        min_value=1,
        max_value=max(len(ready_jobs), 1),
        value=min(len(ready_jobs), 5) or 1,
        disabled=not ready_jobs,
    )

    if st.button("Analyze Batch", disabled=not ready_jobs):
        if not st.session_state.get("last_resume_text"):
            st.warning("Upload a resume in the Analyze Job tab first.")
        else:
            selected_jobs = ready_jobs[:batch_limit]
            progress = st.progress(0)
            analyzed_count = 0

            for index, job in enumerate(selected_jobs, start=1):
                with st.spinner(f"Analyzing {job.title or job.company or 'job'}..."):
                    try:
                        analyze_job_with_llm(
                            job,
                            st.session_state["last_resume_text"],
                            analyze_resume,
                        )
                    except LLMError as error:
                        st.warning(f"Skipped {job.title or job.company or job.id}: {error}")
                        progress.progress(index / len(selected_jobs))
                        continue
                    except ValueError as error:
                        st.warning(f"Skipped {job.title or job.company or job.id}: {error}")
                        progress.progress(index / len(selected_jobs))
                        continue

                try:
                    update_current_job(job)
                    analyzed_count += 1
                except ValueError as error:
                    st.warning(f"Skipped {job.title or job.company or job.id}: {error}")

                progress.progress(index / len(selected_jobs))

            st.success(f"Analyzed {analyzed_count} job(s).")
            st.rerun()

    st.subheader("Jobs")

    if not jobs:
        st.info("No jobs saved yet. Add one manually, import a CSV, or paste job URLs above.")
    else:
        filter_col, search_col, sort_col = st.columns([1, 2, 1])
        selected_status = filter_col.selectbox("Status filter", ("All", *VALID_STATUSES))
        search_query = search_col.text_input("Search jobs")
        sort_by = sort_col.selectbox("Sort by", SORT_OPTIONS)

        visible_jobs = sort_jobs(
            filter_jobs(jobs, status=selected_status, query=search_query),
            sort_by=sort_by,
        )

        st.caption(f"Showing {len(visible_jobs)} of {len(jobs)} job(s).")
        st.download_button(
            "Download Visible Jobs CSV",
            data=jobs_to_csv(visible_jobs),
            file_name="job_tracker.csv",
            mime="text/csv",
        )

        for job in visible_jobs:
            heading = f"{job.title or 'Untitled Role'} at {job.company or 'Unknown Company'}"

            with st.expander(heading):
                checklist = build_application_checklist(
                    job,
                    current_profile(),
                    has_resume=bool(st.session_state.get("last_resume_text")),
                )
                st.progress(readiness_percentage(checklist) / 100)
                st.caption(f"Application readiness: {readiness_percentage(checklist)}%")

                st.write("Location:", job.location or "Not added")
                if job.url:
                    st.link_button("Open Job", job.url)

                score_col, match_col = st.columns(2)
                score_col.metric("Resume Score", job.resume_score or "N/A")
                match_col.metric("JD Match %", job.match_percentage or "N/A")

                with st.expander("Edit Job"):
                    with st.form(f"edit_job_form_{job.id}"):
                        edit_company = st.text_input(
                            "Company",
                            value=job.company,
                            key=f"company_{job.id}",
                        )
                        edit_title = st.text_input(
                            "Job title",
                            value=job.title,
                            key=f"title_{job.id}",
                        )
                        edit_location = st.text_input(
                            "Location",
                            value=job.location,
                            key=f"location_{job.id}",
                        )
                        edit_url = st.text_input(
                            "Job URL",
                            value=job.url,
                            key=f"url_{job.id}",
                        )
                        edit_description = st.text_area(
                            "Job description",
                            value=job.description,
                            height=180,
                            key=f"description_{job.id}",
                        )
                        edit_status = st.selectbox(
                            "Status",
                            VALID_STATUSES,
                            index=VALID_STATUSES.index(job.status)
                            if job.status in VALID_STATUSES
                            else 0,
                            key=f"status_{job.id}",
                        )
                        edit_notes = st.text_area(
                            "Notes",
                            value=job.notes,
                            key=f"notes_{job.id}",
                        )
                        edit_tailoring_plan = st.text_area(
                            "Tailored resume draft",
                            value=job.tailoring_plan,
                            height=160,
                            key=f"edit_tailoring_plan_{job.id}",
                        )
                        edit_cover_letter = st.text_area(
                            "Cover letter",
                            value=job.cover_letter,
                            height=160,
                            key=f"edit_cover_letter_{job.id}",
                        )

                        if st.form_submit_button("Save Changes"):
                            job.company = edit_company.strip()
                            job.title = edit_title.strip()
                            job.location = edit_location.strip()
                            job.url = edit_url.strip()
                            job.description = edit_description.strip()
                            job.status = edit_status
                            job.notes = edit_notes.strip()
                            job.tailoring_plan = edit_tailoring_plan.strip()
                            job.cover_letter = edit_cover_letter.strip()
                            update_current_job(job)
                            st.success("Job updated.")
                            st.rerun()

                    confirm_delete = st.checkbox(
                        "Confirm delete",
                        key=f"confirm_delete_{job.id}",
                    )
                    if st.button(
                        "Delete Job",
                        key=f"delete_{job.id}",
                        disabled=not confirm_delete,
                    ):
                        if delete_current_job(job.id):
                            st.success("Job deleted.")
                            st.rerun()
                        else:
                            st.warning("This job was already removed.")

                if st.button("Analyze Saved Job", key=f"analyze_{job.id}"):
                    if not st.session_state.get("last_resume_text"):
                        st.warning("Upload a resume in the Analyze Job tab first.")
                    elif not job.description:
                        st.warning("Add a job description before analyzing this job.")
                    else:
                        with st.spinner("Analyzing saved job..."):
                            try:
                                result = analyze_resume(
                                    st.session_state["last_resume_text"],
                                    job.description,
                                )
                            except LLMError as error:
                                st.error(str(error))
                                result = ""

                        if result:
                            try:
                                analysis = parse_analysis_result(result)
                                update_current_job(apply_analysis(job, analysis))
                                st.success("Saved job analyzed.")
                            except ValueError as error:
                                st.error(str(error))
                                st.write(result)

                material_col, letter_col = st.columns(2)

                if material_col.button("Generate Saved Tailored Resume", key=f"tailor_{job.id}"):
                    if not st.session_state.get("last_resume_text"):
                        st.warning("Upload a resume in the Analyze Job tab first.")
                    elif not job.description:
                        st.warning("Add a job description before generating materials.")
                    else:
                        with st.spinner("Writing tailored resume..."):
                            try:
                                plan = tailor_resume(
                                    st.session_state["last_resume_text"],
                                    job.description,
                                    build_profile_context(current_profile()),
                                )
                            except LLMError as error:
                                st.error(str(error))
                                plan = ""
                        if plan:
                            update_current_job(apply_tailoring_plan(job, plan))
                            st.success("Tailored resume saved.")
                            st.rerun()

                if letter_col.button("Generate Saved Cover Letter", key=f"letter_{job.id}"):
                    if not st.session_state.get("last_resume_text"):
                        st.warning("Upload a resume in the Analyze Job tab first.")
                    elif not job.description:
                        st.warning("Add a job description before generating materials.")
                    else:
                        with st.spinner("Writing cover letter..."):
                            try:
                                letter = generate_cover_letter(
                                    st.session_state["last_resume_text"],
                                    job.description,
                                    build_profile_context(current_profile()),
                                )
                            except LLMError as error:
                                st.error(str(error))
                                letter = ""
                        if letter:
                            update_current_job(apply_cover_letter(job, letter))
                            st.success("Cover letter saved.")
                            st.rerun()

                if job.tailoring_plan:
                    st.subheader("Saved Tailored Resume")
                    st.markdown(job.tailoring_plan)
                    file_stem = safe_file_stem(job.company, job.title)
                    st.download_button(
                        "Download Tailored Resume",
                        data=job.tailoring_plan,
                        file_name=f"{file_stem}_tailored_resume.md",
                        mime="text/markdown",
                        key=f"download_plan_{job.id}",
                    )

                if job.cover_letter:
                    st.subheader("Saved Cover Letter")
                    st.text_area(
                        "Cover letter",
                        value=job.cover_letter,
                        height=260,
                        key=f"cover_letter_text_{job.id}",
                    )
                    file_stem = safe_file_stem(job.company, job.title)
                    st.download_button(
                        "Download Cover Letter",
                        data=job.cover_letter,
                        file_name=f"{file_stem}_cover_letter.txt",
                        mime="text/plain",
                        key=f"download_letter_{job.id}",
                    )

                if job.missing_skills:
                    st.write("Missing skills:", ", ".join(job.missing_skills))
                if job.keyword_gaps:
                    st.write("Keyword gaps:", ", ".join(job.keyword_gaps))
                if job.improvement_suggestions:
                    st.write("Suggestions:")
                    for suggestion in job.improvement_suggestions:
                        st.write("-", suggestion)

                with st.expander("Application Checklist"):
                    for item in checklist:
                        st.checkbox(item.label, value=item.is_ready, disabled=True)
