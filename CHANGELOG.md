# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-03-04

### Changed

- Modified output filename generation (`src/utils.py::get_website_name`) to include the first URL path segment (e.g., `domain_com_pathsegment_nav_map.md`). Handles URLs with and without paths.

## [1.0.0] - 2025-03-31

### Added

- **Core Functionality:**
  - CSV input processing with validation and error logging.
  - Command Line Interface (CLI) for selecting target URLs.
  - Website navigation crawling with configurable selectors (basic implementation).
  - Recursive sub-menu traversal.
  - Extraction of page name, URL, and last updated date (if available).
  - Markdown output generation in a tree structure (`<website_name>_nav_map.md`).
- **Concurrency & Robustness:**
  - Thread pool executor (`concurrent.futures.ThreadPoolExecutor`) for parallel crawling.
  - Atomic file writing using temporary files and `os.rename`.
  - Write-ahead logging (`.lock` files) for task state management.
  - Stale lock file cleanup mechanism.
  - Exponential backoff retry logic (max 3 attempts) for network errors.
  - Dead Letter Queue (DLQ) for persistently failed tasks.
- **Error Handling & Logging:**
  - Comprehensive logging (INFO, WARNING, ERROR) to console and structured JSON file (`dlq.log`).
  - Graceful handling of Network, Parsing, I/O, and Concurrency errors.
  - Thread-specific metadata in logs.
- **User Experience:**
  - `tqdm` progress bar during the crawling phase.
- **Project Setup & Documentation:**
  - Standard Python project structure (`src/`, `tests/`, `input_csvs/`, `output_maps/`, `logs/`).
  - `requirements.txt` for dependency management.
  - `.gitignore` and `.clineignore` files.
  - Initial unit tests (`pytest`) for utilities, CSV processing, and crawler functions.
  - Comprehensive Memory Bank documentation in `dev_docs/` (`project_brief.md`, `codebase_summary.md`, `tech_stack.md`, `current_task.md`, `project_tracker.md`, `implementation_plan.md`).
  - `README.md` with project overview, setup, and usage instructions.
  - `CHANGELOG.md` following Keep a Changelog format.

### Fixed

- Corrected crawler logic to prevent duplicate URL processing.
- Resolved indentation error (`continue` outside loop) in `src/crawler.py`.
- Updated deprecated `datetime.utcfromtimestamp` to `datetime.fromtimestamp(timestamp, timezone.utc)` in `src/logger_config.py`.
