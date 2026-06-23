import os
import unittest
from unittest.mock import patch

from auth import (
    ACCESS_CODE_ENV,
    MANAGED_AUTH_HEADER_ENV,
    REQUIRE_MANAGED_AUTH_ENV,
    access_code_matches,
    is_auth_enabled,
    is_managed_auth_required,
    user_id_from_headers,
)


class AuthTest(unittest.TestCase):
    def test_auth_is_disabled_when_access_code_is_empty(self):
        with patch.dict(os.environ, {ACCESS_CODE_ENV: ""}, clear=False):
            self.assertFalse(is_auth_enabled())
            self.assertTrue(access_code_matches(""))

    def test_access_code_matches_configured_secret(self):
        with patch.dict(os.environ, {ACCESS_CODE_ENV: "secret"}, clear=False):
            self.assertTrue(is_auth_enabled())
            self.assertTrue(access_code_matches("secret"))
            self.assertFalse(access_code_matches("wrong"))

    def test_user_id_from_headers_reads_configured_header_case_insensitively(self):
        with patch.dict(os.environ, {MANAGED_AUTH_HEADER_ENV: "X-User-Email"}, clear=False):
            user_id = user_id_from_headers({"x-user-email": "aarav@example.com"})

        self.assertEqual(user_id, "aarav@example.com")

    def test_managed_auth_requirement_uses_boolean_env(self):
        with patch.dict(os.environ, {REQUIRE_MANAGED_AUTH_ENV: "true"}, clear=False):
            self.assertTrue(is_managed_auth_required())


if __name__ == "__main__":
    unittest.main()
