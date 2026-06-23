import shutil
from pathlib import Path

from job_store import utc_now


DEFAULT_BACKUP_DIR = Path("backups")


def create_file_backup(source_path: str | Path, backup_dir: str | Path = DEFAULT_BACKUP_DIR) -> Path | None:
    source = Path(source_path)

    if not source.exists():
        return None

    destination_dir = Path(backup_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    timestamp = utc_now().replace(":", "-")
    destination = destination_dir / f"{source.stem}.{timestamp}{source.suffix}"
    shutil.copy2(source, destination)
    return destination


def backup_paths(paths: list[str | Path], backup_dir: str | Path = DEFAULT_BACKUP_DIR) -> list[Path]:
    backups = []

    for path in paths:
        backup = create_file_backup(path, backup_dir)
        if backup:
            backups.append(backup)

    return backups
