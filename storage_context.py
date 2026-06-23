import os
import re
from pathlib import Path


MULTI_USER_ENV = "APP_MULTI_USER_MODE"
STORAGE_BACKEND_ENV = "APP_STORAGE_BACKEND"
DATABASE_PATH_ENV = "APP_DATABASE_PATH"
DEFAULT_DATA_DIR = Path("data")
DEFAULT_PROFILE_PATH = DEFAULT_DATA_DIR / "profile.json"
DEFAULT_JOBS_PATH = DEFAULT_DATA_DIR / "jobs.json"
DEFAULT_DATABASE_PATH = DEFAULT_DATA_DIR / "app.sqlite3"
USER_DATA_DIR = DEFAULT_DATA_DIR / "users"


def is_multi_user_mode() -> bool:
    return os.getenv(MULTI_USER_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def storage_backend() -> str:
    backend = os.getenv(STORAGE_BACKEND_ENV, "json").strip().lower()
    return backend if backend in {"json", "sqlite"} else "json"


def database_path() -> Path:
    return Path(os.getenv(DATABASE_PATH_ENV, "") or DEFAULT_DATABASE_PATH)


def sanitize_workspace_id(value: str) -> str:
    cleaned_value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return cleaned_value[:64]


def profile_path_for_workspace(workspace_id: str, base_dir: Path = USER_DATA_DIR) -> Path:
    return base_dir / sanitize_workspace_id(workspace_id) / "profile.json"


def jobs_path_for_workspace(workspace_id: str, base_dir: Path = USER_DATA_DIR) -> Path:
    return base_dir / sanitize_workspace_id(workspace_id) / "jobs.json"


def resolve_storage_paths(workspace_id: str = "") -> tuple[Path, Path]:
    if not is_multi_user_mode():
        return DEFAULT_PROFILE_PATH, DEFAULT_JOBS_PATH

    sanitized_workspace_id = sanitize_workspace_id(workspace_id)
    if not sanitized_workspace_id:
        raise ValueError("Workspace ID is required when APP_MULTI_USER_MODE is enabled.")

    return (
        profile_path_for_workspace(sanitized_workspace_id),
        jobs_path_for_workspace(sanitized_workspace_id),
    )
