import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from job_store import JobApplication, is_duplicate_job, utc_now
from profile_store import CandidateProfile


DEFAULT_DATABASE_PATH = Path("data/app.sqlite3")


def init_database(database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                workspace_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                workspace_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (workspace_id, job_id)
            )
            """
        )


def load_profile(workspace_id: str, database_path: str | Path = DEFAULT_DATABASE_PATH) -> CandidateProfile:
    init_database(database_path)

    with _connect(database_path) as connection:
        row = connection.execute(
            "SELECT payload FROM profiles WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchone()

    if not row:
        return CandidateProfile()

    data = json.loads(row["payload"])
    return CandidateProfile(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        target_roles=list(data.get("target_roles", [])),
        preferred_locations=list(data.get("preferred_locations", [])),
        skills=list(data.get("skills", [])),
        experience_summary=data.get("experience_summary", ""),
        links=dict(data.get("links", {})),
    )


def save_profile(
    profile: CandidateProfile,
    workspace_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    init_database(database_path)
    now = utc_now()

    with _connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO profiles (workspace_id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(workspace_id)
            DO UPDATE SET payload = excluded.payload, updated_at = excluded.updated_at
            """,
            (workspace_id, json.dumps(asdict(profile)), now),
        )


def load_jobs(workspace_id: str, database_path: str | Path = DEFAULT_DATABASE_PATH) -> list[JobApplication]:
    init_database(database_path)

    with _connect(database_path) as connection:
        rows = connection.execute(
            "SELECT payload FROM jobs WHERE workspace_id = ? ORDER BY updated_at DESC",
            (workspace_id,),
        ).fetchall()

    return [_job_from_payload(row["payload"]) for row in rows]


def save_jobs(
    jobs: list[JobApplication],
    workspace_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    init_database(database_path)

    with _connect(database_path) as connection:
        connection.execute("DELETE FROM jobs WHERE workspace_id = ?", (workspace_id,))
        for job in jobs:
            _upsert_job(connection, workspace_id, job)


def add_job_if_new(
    job: JobApplication,
    workspace_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> JobApplication | None:
    jobs = load_jobs(workspace_id, database_path)

    if is_duplicate_job(job, jobs):
        return None

    job.updated_at = utc_now()

    with _connect(database_path) as connection:
        _upsert_job(connection, workspace_id, job)

    return job


def update_job(
    updated_job: JobApplication,
    workspace_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> JobApplication:
    jobs = load_jobs(workspace_id, database_path)
    existing_job = next((job for job in jobs if job.id == updated_job.id), None)

    if not existing_job:
        raise ValueError(f"Job not found: {updated_job.id}")

    updated_job.created_at = existing_job.created_at
    updated_job.updated_at = utc_now()

    with _connect(database_path) as connection:
        _upsert_job(connection, workspace_id, updated_job)

    return updated_job


def delete_job(
    job_id: str,
    workspace_id: str,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> bool:
    init_database(database_path)

    with _connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM jobs WHERE workspace_id = ? AND job_id = ?",
            (workspace_id, job_id),
        )

    return cursor.rowcount > 0


def _connect(database_path: str | Path):
    connection = sqlite3.connect(Path(database_path))
    connection.row_factory = sqlite3.Row
    return connection


def _upsert_job(connection, workspace_id: str, job: JobApplication) -> None:
    connection.execute(
        """
        INSERT INTO jobs (workspace_id, job_id, payload, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(workspace_id, job_id)
        DO UPDATE SET payload = excluded.payload, updated_at = excluded.updated_at
        """,
        (
            workspace_id,
            job.id,
            json.dumps(asdict(job)),
            job.created_at,
            job.updated_at,
        ),
    )


def _job_from_payload(payload: str) -> JobApplication:
    data = json.loads(payload)
    return JobApplication(
        id=data.get("id", ""),
        company=data.get("company", ""),
        title=data.get("title", ""),
        location=data.get("location", ""),
        url=data.get("url", ""),
        source=data.get("source", ""),
        description=data.get("description", ""),
        status=data.get("status", "Saved"),
        match_percentage=data.get("match_percentage"),
        resume_score=data.get("resume_score"),
        missing_skills=list(data.get("missing_skills", [])),
        keyword_gaps=list(data.get("keyword_gaps", [])),
        improvement_suggestions=list(data.get("improvement_suggestions", [])),
        tailoring_plan=data.get("tailoring_plan", ""),
        cover_letter=data.get("cover_letter", ""),
        notes=data.get("notes", ""),
        created_at=data.get("created_at", utc_now()),
        updated_at=data.get("updated_at", utc_now()),
    )
