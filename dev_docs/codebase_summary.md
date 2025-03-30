# Codebase Summary

## Overview

This project aims to generate navigation map markdown files for websites based on URLs provided in CSV files. It involves processing CSVs, validating URLs, crawling website navigation menus, and generating tree-structure diagrams in markdown format.

## Key Components

1.  **URL/CSV Processor:** Reads and validates URLs from CSV files located in a designated project root folder. Handles errors gracefully without blocking other valid entries.
2.  **Navigation Crawler:** Traverses website navigation menus recursively, extracts page details (name, URL, last updated), and generates the markdown tree diagram. Outputs files to a designated project root folder.
3.  **Concurrency System:** Manages concurrent processing of URLs using a thread pool (`concurrent.futures.ThreadPoolExecutor`). Mitigates file write conflicts using atomic writes (temporary file + `os.rename`) for race conditions and write-ahead logging (`.lock` files) for partial write detection. Parallel write data corruption is not actively prevented in the initial implementation.
4.  **User Interface (CLI):** Provides a command-line interface for users to select which validated URL from the CSV(s) to process, triggering the concurrent processing framework.

## Data Flow

```mermaid
flowchart LR
    A[CSV file] --> B[URL/CSV Processor]
    B -->|Valid| C[Navigation Crawler]
    B -->|Errors| D[Error Log]
    C --> E[Write Queue]
    E -->|Atomic Write| F[*_nav_map.md]
```

## External Dependencies

- See `tech_stack.md` for details on libraries and environment.

## Recent Significant Changes

- Initial project setup and Memory Bank initialization.
- Refined concurrency strategy: Adopted thread pool, atomic writes, and write-ahead logging; adjusted implementation plan phase order.

## User Feedback Integration

- N/A at this stage.

## Additional Documentation

- `implementation_plan.md`: Detailed step-by-step plan for project development.
