"""Unit tests for CSV processing functions in src.csv_processor."""

import unittest
import sys
import os
import csv
import tempfile
import logging  # Import logging unconditionally

# Adjust path to import from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from src.csv_processor import validate_url, process_csv_file
    # find_csv_files, load_all_valid_urls
    # Need logger_config for the module to load if it uses logger at module
    # level
    from src.logger_config import setup_logging
    # Configure dummy logging for tests to avoid errors if module logs
    # something
    setup_logging(level=logging.CRITICAL)  # Set level high to suppress output
    # during tests
except ImportError as e:
    print(f"Error importing src modules in tests: {e}. Ensure tests are run from project root or PYTHONPATH is set.")
    sys.exit(1)
except NameError:  # Handle case where logging hasn't been imported yet
    # (should not happen now)
    # import logging # No longer needed here
    logging.basicConfig(level=logging.CRITICAL)


class TestCsvProcessor(unittest.TestCase):

    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "http://example.com/path",
            "https://example.com?query=1",
            "https://example.co.uk",
            "http://192.168.0.1",
            "https://sub-domain.example.com",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(validate_url(url))

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "ftp://example.com",  # Invalid scheme
            "example.com",        # Missing scheme
            "http://",            # Missing domain
            "https://",           # Missing domain
            "",                   # Empty string
            None,                 # None value
            "just some text",
            "http:// example.com",  # Space in domain (urlparse might handle
            # this differently across versions)
            "http://.com",        # Invalid domain
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(validate_url(url))

    def test_process_csv_file_valid(self):
        """Test processing a valid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".csv", newline='') as temp_csv:
            writer = csv.writer(temp_csv)
            writer.writerow(["url", "css_selector"])  # Header
            writer.writerow(["https://valid1.com", ".nav"])
            writer.writerow([" http://valid2.org/path ", " #menu "])
            # With whitespace
            writer.writerow(["https://valid3.net?q=1", "nav ul"])
            temp_csv_path = temp_csv.name

        expected_result = [
            ("https://valid1.com", ".nav"),
            ("http://valid2.org/path", "#menu"),
            ("https://valid3.net?q=1", "nav ul"),
        ]
        result = process_csv_file(temp_csv_path)
        self.assertEqual(result, expected_result)
        os.remove(temp_csv_path)

    def test_process_csv_file_mixed_validity(self):
        """Test processing a CSV with valid, invalid, and missing data."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".csv", newline='') as temp_csv:
            writer = csv.writer(temp_csv)
            # No header this time
            writer.writerow(["https://valid1.com", ".nav"])
            writer.writerow(["invalid-url", ".selector"])  # Invalid URL
            writer.writerow(["https://valid2.com", ""])  # Missing selector
            writer.writerow(["", ".another-selector"])  # Missing URL
            writer.writerow(["https://valid3.com", "#main"])
            writer.writerow([])  # Empty row
            temp_csv_path = temp_csv.name

        expected_result = [
            ("https://valid1.com", ".nav"),
            ("https://valid3.com", "#main"),
        ]
        result = process_csv_file(temp_csv_path)
        self.assertEqual(result, expected_result)
        os.remove(temp_csv_path)

    def test_process_csv_file_no_selector(self):
        """Test processing a CSV where selector column might be missing."""
        with tempfile.NamedTemporaryFile(
            mode='w+',
            delete=False,
            suffix=".csv",
            newline=''
        ) as temp_csv:
            writer = csv.writer(temp_csv)
            writer.writerow(["url"])  # Only URL header
            writer.writerow(["https://valid1.com"])
            temp_csv_path = temp_csv.name

        expected_result = []  # Should skip rows without a selector
        result = process_csv_file(temp_csv_path)
        self.assertEqual(result, expected_result)
        os.remove(temp_csv_path)

    def test_process_csv_file_not_found(self):
        """Test processing a non-existent file."""
        result = process_csv_file("non_existent_file.csv")
        self.assertEqual(result, [])  # Should return empty list and log error

    # Add tests for find_csv_files and load_all_valid_urls later if needed,
    # mocking os functions


if __name__ == '__main__':
    unittest.main()
