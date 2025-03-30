# Tech Stack

## Runtime Environment

- **Language:** Python 3.10+
  - _Justification:_ Specified in the project brief. Provides robust libraries for web scraping, file handling, and concurrency.
  - _Consequences:_ Requires a compatible Python installation on the execution environment.

## Core Libraries

- **BeautifulSoup4:** For parsing HTML content from fetched webpages.
  - _Justification:_ Standard and effective library for HTML parsing in Python. Specified in the brief.
  - _Consequences:_ Adds a dependency that needs to be installed. Parsing robustness depends on website structure.
- **Requests:** For making HTTP requests to fetch website content.
  - _Justification:_ Simple and widely used library for HTTP requests in Python. Specified in the brief.
  - _Consequences:_ Adds a dependency. Network reliability and website response times can affect performance. Error handling for network issues is crucial.
- **Python `csv` module:** For reading and processing CSV files containing website URLs.
  - _Justification:_ Built-in Python module suitable for CSV operations, including validation as required by the brief.
  - _Consequences:_ Requires CSV files to be well-formatted. Validation logic needs to be implemented carefully.

## Concurrency & Resilience

- **`concurrent.futures.ThreadPoolExecutor`:** Manages a pool of threads for executing crawling tasks concurrently.
  - _Justification:_ Standard Python library for managing thread pools, simplifying concurrent task execution for I/O-bound operations. Replaces simpler "thread-per-row" concept.
  - _Consequences:_ Requires careful pool size configuration. Still necessitates thread-safe handling of shared resources.
- **Atomic Writes & Write-Ahead Logging (WAL):** Using `tempfile.NamedTemporaryFile` + `os.rename` and `.lock` files for safe file output.
  - _Justification:_ Prevents race conditions during file writes and provides a mechanism to detect/handle partial writes. Replaces simpler "Write Queue" concept.
  - _Consequences:_ Adds complexity to the file writing logic, requires handling of stale lock files.
- **Retry Circuit Breaker (Custom Logic):** Using exponential backoff with jitter for retrying failed tasks (e.g., network errors).
  - _Justification:_ Improves resilience against transient failures.
  - _Consequences:_ Increases complexity in task execution logic, requires defining retry limits and conditions.
- **Dead Letter Queue (DLQ) (Custom Logic):** Simple file-based queue for persistently failed tasks.
  - _Justification:_ Prevents loss of information about tasks that could not be completed after retries. Allows for later inspection or manual retry.
  - _Consequences:_ Requires implementation of DLQ writing and potentially reading/reprocessing logic. Adds another file to manage.

## Version Control

- **Git:** For source code management.
  - _Justification:_ Standard tool for version control. Specified in the brief.
  - _Consequences:_ Requires Git to be installed and used throughout the development process.

## Architecture Decisions

- **Modular Design:** Separating concerns into distinct components (CSV Processing, Crawling, Concurrency Management, CLI).
  - _Justification:_ Improves maintainability, testability, and allows for independent development/modification of parts.
  - _Consequences:_ Requires clear interfaces between components.
- **Folder Structure:** Using dedicated folders for input CSVs and output markdown files within the project root.
  - _Justification:_ Organizes project artifacts clearly as per the brief's requirements.
  - _Consequences:_ Scripts need to correctly reference these folder paths.
- **Error Handling Strategy:** Robust `try-except` blocks, structured logging (JSON), and specific handling for Network, Parsing, I/O, and Concurrency errors.
  - _Justification:_ Explicitly required by the brief and enhanced by the concurrency design to ensure resilience and observability.
  - _Consequences:_ Increases code complexity but improves reliability and diagnosability.
- **Enhanced Concurrency Model:** Incorporating atomic writes, WAL, retries, and DLQ.
  - _Justification:_ Addresses potential issues with simple threading and improves overall robustness and stability under load.
  - _Consequences:_ Increases the complexity of the concurrency implementation compared to basic threading. Requires careful testing.
