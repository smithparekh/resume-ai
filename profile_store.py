import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path


DEFAULT_PROFILE_PATH = Path("data/profile.json")


class ProfileStoreError(Exception):
    pass


@dataclass
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    target_roles: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    experience_summary: str = ""
    links: dict[str, str] = field(default_factory=dict)


def parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def format_list(values: list[str]) -> str:
    return ", ".join(values)


def load_profile(path: str | Path = DEFAULT_PROFILE_PATH) -> CandidateProfile:
    profile_path = Path(path)

    if not profile_path.exists():
        return CandidateProfile()

    try:
        with profile_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        backup_path = _backup_corrupt_file(profile_path)
        raise ProfileStoreError(
            f"Could not read saved profile. The corrupt file was backed up to {backup_path}."
        ) from error

    if not isinstance(data, dict):
        backup_path = _backup_corrupt_file(profile_path)
        raise ProfileStoreError(
            f"Saved profile must be an object. The invalid file was backed up to {backup_path}."
        )

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
    path: str | Path = DEFAULT_PROFILE_PATH,
) -> None:
    profile_path = Path(path)
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    with profile_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(profile), file, indent=2)
        file.write("\n")


def _backup_corrupt_file(path: Path) -> Path:
    backup_path = path.with_suffix(f"{path.suffix}.corrupt")
    counter = 1

    while backup_path.exists():
        backup_path = path.with_suffix(f"{path.suffix}.corrupt.{counter}")
        counter += 1

    shutil.copy(path, backup_path)
    return backup_path
