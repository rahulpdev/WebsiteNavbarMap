# Implementation Plan

This document outlines the step-by-step plan for developing the Website Navigation Map generator, based on `project_brief.md` and `project_tracker.md`.

## Phase 1: Project Setup & Foundation

1.  **Initialize Project Structure:**
    - Create root-level directories:
      - `input_csvs/` (for user-provided CSV files)
      - `output_maps/` (for generated markdown navigation maps)
      - `src/` (for Python source code)
      - `logs/` (for log files)
    - Create `src/__init__.py` to mark `src` as a package.
    - Create placeholder files: `src/main.py`, `src/csv_processor.py`, `src/crawler.py`, `src/file_writer.py`, `src/logger_config.py`, `src/utils.py`.
2.  **Setup Environment & Dependencies:**
    - Initialize Git repository: `git init`
    - Create `.gitignore` file (e.g., for `__pycache__`, `.env`, `logs/`, potentially `input_csvs/`, `output_maps/`).
    - Create `requirements.txt` and add initial dependencies:
      ```
      requests
      beautifulsoup4
      ```
3.  **Configure Logging (`src/logger_config.py`):**
    - Set up a reusable logging configuration function.
    - Configure logging to output to both console and a rotating file in `logs/`.
    - Use a structured format (JSON) for file logging as specified in the brief.
    - Define standard log levels (INFO, WARNING, ERROR).
    - Include thread-specific metadata (e.g., thread ID/name) in log records.

## Phase 2: Core Modules Development

4.  **CSV Processing Module (`src/csv_processor.py`):**
    - **`find_csv_files(directory)`:** Function to locate all `.csv` files within the `input_csvs/` directory.
    - **`validate_url(url_string)`:** Function using regex or `urllib.parse` to validate URL format. Returns `True/False`.
    - **`process_csv_file(filepath)`:** Function to read a single CSV file.
      - Use Python's `csv` module.
      - Iterate through rows, skipping header if present.
      - Trim whitespace from URL cell.
      - Call `validate_url` for each URL.
      - Log errors for invalid rows (including filename and line number) but continue processing.
      - Return a list of valid URLs found in the file.
    - **`load_all_valid_urls(directory)`:** Orchestrator function calling `find_csv_files` and `process_csv_file` for each found CSV. Returns a consolidated list of unique, valid URLs.
5.  **Utility Functions (`src/utils.py`):**
    - **`get_website_name(url)`:** Function to derive a filesystem-safe name from a URL (e.g., `www.example.com` -> `example_com`). This will be used for filenames.
    - Implement retry logic decorator/function (e.g., exponential backoff with jitter, max 3 attempts) for network requests (`fetch_html`). This will form part of the Retry Circuit Breaker.
6.  **Crawler Module (`src/crawler.py`):**

    - **`fetch_html(url)`:** Function using `requests.get()` to fetch HTML.
      - Apply retry logic from `utils`.
      - Include appropriate headers (e.g., User-Agent).
      - Handle `requests.exceptions.RequestException` and log errors. Return `None` on failure.
    - **`find_nav_links(html_content, base_url)`:** Function using `BeautifulSoup` to parse HTML.
      - Identify primary navigation elements (e.g., `<nav>`, specific IDs/classes - **needs refinement/configurability**).
      - Extract `<a>` tags within the navigation.
      - Resolve relative URLs to absolute URLs using `base_url`.
      - Handle parsing errors (`try-except`) and log issues.
      - Return a list of tuples: `(link_text, absolute_url)`.
    - **`crawl_navigation(start_url)`:** Main crawling logic.
      - Maintain a set of visited URLs to avoid loops.
      - Use a queue or recursion for traversal (depth-first or breadth-first).
      - Start with `fetch_html` and `find_nav_links` for the `start_url`.
      - Recursively/iteratively process links found in navigation menus.
      - **Challenge:** Accurately determining menu hierarchy and structure solely from links requires careful heuristics or assumptions about common HTML structures (e.g., nested `<ul>`/`<li>`).
      - Store results in a nested structure (e.g., dictionary or custom node class) representing the hierarchy.
      - Extract last updated timestamp if available (e.g., from HTTP headers or meta tags - often unreliable).
    - **`format_tree(nav_data)`:** Function to convert the crawled data structure into the specified markdown tree string format.

7.  **File Output Module (`src/file_writer.py`):**
    - **`generate_filename(url)`:** Use `utils.get_website_name` to create the `<website_name>_nav_map.md` filename.
    - **`write_map_file(filepath, content)`:** Function to write the markdown string to the specified path in `output_maps/`.
      - Ensure the `output_maps/` directory exists.
      - Use `try-except` to handle `IOError` and log errors.
      - **Concurrency Mitigation:**
        - Implement atomic writes using `tempfile.NamedTemporaryFile` and `os.rename` to prevent race conditions.
        - Implement write-ahead logging using a `.lock` file (create before write, delete after successful rename).
        - Implement stale lock file cleanup (e.g., check timestamp on startup or periodically, remove locks older than a threshold like 5 minutes).

## Phase 3: Concurrency Implementation & Enhancements

8.  **Concurrency Framework (`src/concurrency_manager.py` or similar):**
    - Implement a thread pool executor (`concurrent.futures.ThreadPoolExecutor`) with configurable size (e.g., `min(32, os.cpu_count() + 4)`).
    - Define a worker function that encapsulates the task (URL -> crawl -> format -> write).
    - **Retry Circuit Breaker:**
      - Integrate the retry logic (from `utils.py`) into the worker function execution.
      - Handle retry exhaustion (log error, potentially move to DLQ).
      - (Optional) Implement fallback to synchronous processing if the pool is consistently overwhelmed (complex).
    - **Dead Letter Queue (DLQ):**
      - Implement a simple file-based queue (`dlq.log` or similar) to store details of tasks that failed permanently (after retries).
      - Log errors clearly when adding to the DLQ.
      - (Optional) Implement a separate utility or logic on startup to attempt reprocessing DLQ items.
    - **Task Submission & Result Handling:**
      - Design the main logic (`main.py` or `runner.py`) to submit crawling tasks to the thread pool via the concurrency manager.
      - Ensure results (success, failure, moved-to-DLQ) from threads are collected and logged appropriately.
    - **Testing:** Test the concurrency mechanism, including retry and DLQ logic, with mock tasks before integrating the actual crawler.

## Phase 4: Integration and CLI

9.  **Main Script (`src/main.py`):**
    - Import necessary modules and configure logging using `logger_config`.
    - Call `csv_processor.load_all_valid_urls` to get the list of target sites.
    - **CLI Interaction:**
      - If no valid URLs, print message and exit.
      - Display a numbered list of unique website domains/names derived from the valid URLs.
      - Loop prompt for user input (number or "exit").
      - Validate input against the list range. Handle invalid input and "exit".
    - **Trigger Concurrent Crawling:**
      - On valid selection, get the corresponding full URL.
      - Submit the selected URL to the concurrency framework (developed in Phase 3) for processing.
      - Provide feedback to the user (e.g., "Processing started for [URL]..."). The actual file writing happens asynchronously via the framework.

## Phase 5: Testing, Refinement & Documentation

10. **Testing:**
    - Develop unit tests for `validate_url`, `get_website_name`, `format_tree`.
    - Develop integration tests for CSV processing, crawling (mocking HTTP requests), file writing, and the concurrency framework (testing atomic writes and lock file behavior under load).
    - Test manually with various real websites to refine `find_nav_links` selectors and crawling logic.
11. **Refinement:**
    - Improve robustness of navigation link identification. Consider making selectors configurable.
    - Optimize performance if needed (e.g., thread pool size).
    - Ensure all error handling paths (including concurrency errors, retry failures) are covered and logged appropriately.
12. **Documentation:**
    - Update all Memory Bank documents (`project_tracker.md`, `current_task.md`, `codebase_summary.md`) to reflect progress and final structure.
    - Add docstrings and comments to the Python code, especially explaining the concurrency logic.
    - Create a comprehensive `README.md` for the GitHub repository, explaining setup, usage, concurrency model, and project structure.
13. **GitHub:**

    - Push final code and documentation to the public GitHub repository.
    - Ensure at least one example `_nav_map.md` is included or generated as part of a test/demo run.
    - Verify all completion criteria from `project_brief.md` are met.

14. **Post-Completion Modification (2025-03-04): Filename Generation Update:**
    - **Requirement:** Modify the output filename to include the first URL path segment after the domain (e.g., `domain_com_pathsegment_nav_map.md`). Handle cases with and without paths correctly.
    - **Action:** Update the `get_website_name` function in `src/utils.py` to parse the URL path, extract and sanitize the first segment, and combine it with the sanitized domain name.
