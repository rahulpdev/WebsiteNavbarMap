# Website Navigation Map Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/dependencies-up--to--date-brightgreen.svg)](requirements.txt) <!-- Placeholder: Consider requires.io or similar for dynamic checks -->
[![Build Status](https://github.com/rahulpdev/WebsiteNavbarMap/actions/workflows/ci.yml/badge.svg)](https://github.com/rahulpdev/WebsiteNavbarMap/actions/workflows/ci.yml) <!-- Assumes a workflow file named ci.yml -->
[![Coverage Status](https://img.shields.io/badge/coverage-unknown-lightgrey.svg)](https://github.com/rahulpdev/WebsiteNavbarMap) <!-- Placeholder: Integrate Codecov/Coveralls -->
[![Documentation Status](https://img.shields.io/badge/docs-active-orange.svg)](dev_docs/project_brief.md)
[![GitHub Issues](https://img.shields.io/github/issues/rahulpdev/WebsiteNavbarMap.svg)](https://github.com/rahulpdev/WebsiteNavbarMap/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/rahulpdev/WebsiteNavbarMap.svg)](https://github.com/rahulpdev/WebsiteNavbarMap/pulls)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/rahulpdev/WebsiteNavbarMap)](https://github.com/rahulpdev/WebsiteNavbarMap/releases/latest)

## Overview

This tool generates a markdown file containing a tree structure diagram representing a website's navigation menu. It reads website URLs and corresponding CSS selectors for the navigation element from CSV files, crawls the specified navigation menu, and outputs a map file for the selected website.

## Key Features

- Processes multiple websites from CSV files (`url,css_selector`).
- Validates input URLs and selectors.
- Crawls navigation menus, handling relative links and staying within the same domain.
- Generates a markdown tree diagram of the navigation structure.
- Uses concurrency to potentially handle multiple sites efficiently (currently processes one selected site at a time).
- Includes error handling for network issues, parsing errors, and file I/O.
- Provides basic file locking to prevent race conditions during output.
- Logs errors and progress to console and `logs/app.log` (JSON format).
- Failed tasks (after retries) are logged to `dlq.log`.

## Table of Contents

- [Website Navigation Map Generator](#website-navigation-map-generator)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [How it Works](#how-it-works)
  - [Usage](#usage)
  - [Project Structure](#project-structure)
  - [Dependencies](#dependencies)
  - [Contributing](#contributing)
  - [License](#license)
  - [FAQs](#faqs)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd WebsiteNavMap
    ```
2.  **Set up a Python environment:**
    It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How it Works

1.  **Input:** Place CSV files in the `input_csvs/` directory. Each CSV should contain at least two columns: `url` and `css_selector`. The first row can optionally be a header.
    - `url`: The full starting URL of the website (e.g., `https://www.example.com`).
    - `css_selector`: The CSS selector that uniquely identifies the main navigation container element on the website (e.g., `#main-nav`, `.primary-navigation ul`).
2.  **Processing:** The script reads all CSV files, validates the URLs and selectors, and presents a numbered list of unique, valid websites found.
3.  **Selection:** The user selects a website number from the list.
4.  **Crawling:** The script starts crawling from the selected URL, fetching HTML content and finding links within the element matching the provided CSS selector. It follows links within the same domain.
5.  **Output:** A markdown file named `<website_name>_nav_map.md` (e.g., `example_com_nav_map.md`) is generated in the `output_maps/` directory, containing the navigation tree.

## Usage

1.  Ensure you have prepared your CSV file(s) in the `input_csvs/` directory.
2.  Run the main script from the project root directory:
    ```bash
    python src/main.py
    ```
3.  Follow the on-screen prompts to select the website you want to map.
4.  Check the `output_maps/` directory for the generated markdown file.
5.  Check `logs/app.log` for detailed execution logs and `dlq.log` for any tasks that failed permanently.

## Project Structure

```
WebsiteNavMap/
├── dev_docs/           # Development documentation (Memory Bank)
├── input_csvs/         # Directory for input CSV files
├── logs/               # Directory for log files (app.log, dlq.log)
├── output_maps/        # Directory for generated markdown map files
├── src/                # Source code
│   ├── __init__.py
│   ├── concurrency_manager.py
│   ├── crawler.py
│   ├── csv_processor.py
│   ├── file_writer.py
│   ├── logger_config.py
│   ├── main.py
│   └── utils.py
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_csv_processor.py
│   └── test_utils.py
├── .gitignore
├── .clineignore        # Cline-specific ignores
├── CHANGELOG.md        # Project version history
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Dependencies

- Python 3.10+
- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML.

Install dependencies using `pip install -r requirements.txt`.

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflows. Ensure code includes relevant tests and documentation updates.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if one is added).

## FAQs

- **Q: Why did my website crawl fail?**
  - A: Check `logs/app.log` for specific errors. Common reasons include incorrect CSS selectors, network issues, website blocking crawlers (check `robots.txt`), or complex JavaScript-rendered navigation menus that this simple crawler cannot handle. Failed tasks may also appear in `dlq.log`.
- **Q: How do I find the right CSS selector?**
  - A: Use your browser's developer tools (usually by right-clicking on the navigation menu and selecting "Inspect" or "Inspect Element"). Find the main container element (like `<nav>`, `<ul>`, or a `<div>` with a specific ID or class) that holds all the primary navigation links. Construct a CSS selector (e.g., `#main-navigation`, `.menu-primary ul`) that uniquely targets this container.
