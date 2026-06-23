from profile_store import CandidateProfile


def build_profile_context(profile: CandidateProfile) -> str:
    lines = [
        f"Name: {profile.name or 'Not provided'}",
        f"Email: {profile.email or 'Not provided'}",
        f"Phone: {profile.phone or 'Not provided'}",
        f"Target roles: {_join_or_default(profile.target_roles)}",
        f"Preferred locations: {_join_or_default(profile.preferred_locations)}",
        f"Skills: {_join_or_default(profile.skills)}",
        f"Experience summary: {profile.experience_summary or 'Not provided'}",
    ]

    links = [f"{name}: {url}" for name, url in profile.links.items() if url]

    if links:
        lines.append(f"Links: {', '.join(links)}")
    else:
        lines.append("Links: Not provided")

    return "\n".join(lines)


def _join_or_default(values: list[str]) -> str:
    return ", ".join(values) if values else "Not provided"
