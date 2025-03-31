"""Unit tests for crawler functions in src.crawler."""

import unittest
import sys
import os
import logging  # Import logging unconditionally

# Adjust path to import from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from src.crawler import format_tree  # fetch_html, find_nav_links, crawl_navigation
    # Need logger_config for the module to load if it uses logger at module level
    from src.logger_config import setup_logging
    # Configure dummy logging for tests
    setup_logging(level=logging.CRITICAL)
except ImportError as e:
    print(f"Error importing src modules in tests: {e}. Ensure tests are run from project root or PYTHONPATH is set.")
    sys.exit(1)
except NameError:  # Handle case where logging hasn't been imported yet (should not happen now)
    # import logging # No longer needed here
    logging.basicConfig(level=logging.CRITICAL)


class TestCrawler(unittest.TestCase):

    def test_format_tree_simple(self):
        """Test formatting a simple nested structure."""
        nav_data = {
            "https://root.com": {
                "name": "https://root.com",
                "children": {
                    "https://root.com/page1": {"name": "Page 1", "children": {}},
                    "https://root.com/page2": {
                        "name": "Page 2",
                        "children": {
                            "https://root.com/page2/sub1": {"name": "Sub 1", "children": {}}
                        }
                    },
                    "https://root.com/page3": {"name": "Page 3", "children": {}},
                }
            }
        }
        expected_output = """
https://root.com
├── https://root.com/page1
├── https://root.com/page2
│   └── https://root.com/page2/sub1
└── https://root.com/page3
""".strip()  # Use strip to remove leading/trailing whitespace from multiline string
        self.assertEqual(format_tree(nav_data), expected_output)

    def test_format_tree_empty(self):
        """Test formatting an empty tree structure."""
        nav_data_empty_children = {
            "https://root.com": {"name": "https://root.com", "children": {}}
        }
        nav_data_none = None
        nav_data_empty_dict = {}

        self.assertEqual(format_tree(nav_data_empty_children), "https://root.com")
        self.assertEqual(format_tree(nav_data_none), "Navigation tree data is empty.")
        self.assertEqual(format_tree(nav_data_empty_dict), "Navigation tree data is empty.")

    def test_format_tree_deeper_nesting(self):
        """Test formatting a deeper nested structure."""
        nav_data = {
            "R": {
                "name": "R",
                "children": {
                    "A": {"name": "A", "children": {
                        "A1": {"name": "A1", "children": {}},
                        "A2": {"name": "A2", "children": {
                            "A2a": {"name": "A2a", "children": {}}
                        }}
                    }},
                    "B": {"name": "B", "children": {}}
                }
            }
        }
        expected_output = """
R
├── A
│   ├── A1
│   └── A2
│       └── A2a
└── B
""".strip()
        self.assertEqual(format_tree(nav_data), expected_output)

    # Add more complex tests later, potentially mocking crawler functions


if __name__ == '__main__':
    unittest.main()
