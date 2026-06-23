import hmac
import os
from collections.abc import Mapping


ACCESS_CODE_ENV = "APP_ACCESS_CODE"
MANAGED_AUTH_HEADER_ENV = "APP_MANAGED_AUTH_HEADER"
REQUIRE_MANAGED_AUTH_ENV = "APP_REQUIRE_MANAGED_AUTH"


def configured_access_code() -> str:
    return os.getenv(ACCESS_CODE_ENV, "").strip()


def is_auth_enabled() -> bool:
    return bool(configured_access_code())


def access_code_matches(candidate: str) -> bool:
    expected = configured_access_code()

    if not expected:
        return True

    return hmac.compare_digest(candidate or "", expected)


def managed_auth_header_name() -> str:
    return os.getenv(MANAGED_AUTH_HEADER_ENV, "").strip()


def is_managed_auth_required() -> bool:
    return os.getenv(REQUIRE_MANAGED_AUTH_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def user_id_from_headers(headers: Mapping[str, str] | None) -> str:
    header_name = managed_auth_header_name()

    if not header_name or not headers:
        return ""

    for key, value in headers.items():
        if key.lower() == header_name.lower():
            return value.strip()

    return ""
