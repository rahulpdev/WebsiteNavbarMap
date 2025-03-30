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

## Concurrency

- **Threading:** Thread-per-row processing for handling multiple URLs concurrently.
  - _Justification:_ Mentioned in the brief's component description. Suitable for I/O-bound tasks like web crawling.
  - _Consequences:_ Requires careful management of shared resources (like file writing) using mechanisms like queues and locks to prevent race conditions.
- **Write Queue:** To manage writing to markdown files atomically.
  - _Justification:_ Mentioned in the brief's component description. Ensures that concurrent threads do not corrupt output files.
  - _Consequences:_ Adds complexity to the writing process.

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
- **Error Handling Strategy:** Robust `try-except` blocks, logging, and retry logic for network/parsing issues. Non-blocking validation for CSV processing.
  - _Justification:_ Explicitly required by the brief to ensure resilience.
  - _Consequences:_ Increases code complexity but improves reliability.
