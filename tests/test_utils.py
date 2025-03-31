"""Unit tests for utility functions in src.utils."""

import unittest
import sys
import os

# Adjust path to import from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from src.utils import get_website_name
    # retry_with_backoff (Decorator testing is more complex)
except ImportError as e:
    print(
        f"Error importing src modules in tests: {e}. Ensure tests are run from project root or PYTHONPATH is set."
    )
    sys.exit(1)


class TestUtils(unittest.TestCase):

    def test_get_website_name_valid_urls(self):
        """Test generating safe names from various valid URLs."""
        test_cases = {
            "https://www.example.com/path?query=1": "example_com",
            "http://test-site.org": "test_site_org",
            "https://sub.domain.co.uk:8080/another/page/": "sub_domain_co_uk",
            "http://192.168.1.1/admin": "192_168_1_1",
            "https://xn--bcher-kva.example/": "xn--bcher-kva_example",
            # Punycode
            "https://domain-with-hyphens.com": "domain_with_hyphens_com",
            "http://UPPERCASE.COM": "uppercase_com",
            # Should be lowercased
        }
        for url, expected_name in test_cases.items():
            with self.subTest(url=url):
                self.assertEqual(get_website_name(url), expected_name)

    def test_get_website_name_invalid_urls(self):
        """Test handling of invalid or edge-case URLs."""
        test_cases = {
            "invalid-url": "invalid_url",  # No scheme/netloc
            "": "invalid_url",
            None: "invalid_url",
            "ftp://example.com": "example_com",  # Still extracts domain if
            # parseable
            "http://": "invalid_url",  # Missing netloc
            "https://?query=1": "invalid_url",  # Missing netloc
            "http://...": "invalid_url_parsing_error",  # Likely parsing error
        }
        for url, expected_name in test_cases.items():
            with self.subTest(url=url):
                # Note: The exact output for "http://..." might vary based on
                #  urlparse behavior
                # We check against the expected error string or a generic
                #  invalid marker
                self.assertIn(
                    get_website_name(url),
                    [expected_name, "invalid_url_parsing_error"]
                )

    # Testing the retry decorator is more involved and often requires mocking
    #  time.sleep
    # and potentially the decorated function's behavior. Skipping for this
    #  basic setup.
    # def test_retry_decorator(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
