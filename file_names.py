import re


def safe_file_stem(*parts: str, default: str = "job") -> str:
    raw_name = "_".join(part.strip() for part in parts if part and part.strip())
    cleaned_name = re.sub(r"[^A-Za-z0-9_-]+", "_", raw_name).strip("_")

    return cleaned_name or default
