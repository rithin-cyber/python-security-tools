import io
import unittest
from contextlib import redirect_stdout

from header_checker import check_headers, has_frame_ancestors


class HeaderCheckerTests(unittest.TestCase):
    def test_detects_frame_ancestors(self):
        csp = "default-src 'self'; frame-ancestors 'none'"
        self.assertTrue(has_frame_ancestors(csp))

    def test_frame_ancestors_is_case_insensitive(self):
        csp = "default-src 'self'; Frame-Ancestors 'self'"
        self.assertTrue(has_frame_ancestors(csp))

    def test_returns_false_when_directive_is_missing(self):
        csp = "default-src 'self'; object-src 'none'"
        self.assertFalse(has_frame_ancestors(csp))

    def test_rejects_unsupported_url_scheme(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = check_headers("ftp://example.com")

        self.assertEqual(result, 1)
        self.assertIn("http:// or https://", output.getvalue())

    def test_rejects_invalid_url(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = check_headers("not-a-url")

        self.assertEqual(result, 1)
        self.assertIn("http:// or https://", output.getvalue())


if __name__ == "__main__":
    unittest.main()
