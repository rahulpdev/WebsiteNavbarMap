# Codebase Summary

## Overview

This project aims to generate navigation map markdown files for websites based on URLs provided in CSV files. It involves processing CSVs, validating URLs, crawling website navigation menus, and generating tree-structure diagrams in markdown format.

## Key Components

1.  **URL/CSV Processor:** Reads and validates URLs from CSV files located in a designated project root folder. Handles errors gracefully without blocking other valid entries.
2.  **Navigation Crawler:** Traverses website navigation menus recursively, extracts page details (name, URL, last updated), and generates the markdown tree diagram. Outputs files to a designated project root folder.
3.  **Concurrency System:** Manages concurrent processing of URLs using a thread pool (`concurrent.futures.ThreadPoolExecutor`). Includes:
    - **Atomic Writes & WAL:** Mitigates file write conflicts using temporary files (`os.rename`) and `.lock` files (write-ahead logging) with stale lock cleanup.
    - **Retry Circuit Breaker:** Handles transient errors with exponential backoff (max 3 attempts).
    - **Dead Letter Queue (DLQ):** Stores persistently failed tasks for later inspection/retry.
4.  **User Interface (CLI):** Provides a command-line interface for users to select which validated URL from the CSV(s) to process, triggering the enhanced concurrent processing framework.

## Data Flow

```mermaid
graph LR
    A[CSV file] --> B(URL/CSV Processor);
    B -- Valid URLs --> C{Concurrency Manager};
    B -- Invalid Rows --> L(Log);
    C -- Submit Task --> P(Thread Pool Worker);
    P -- Success --> W(Atomic Write);
    P -- Retryable Error --> R(Retry Logic);
    R -- Still Fails --> DLQ(Dead Letter Queue);
    P -- Non-Retryable Error --> L;
    W -- Success --> F[*_nav_map.md];
    W -- Write Error --> L;
    DLQ --> L;

    subgraph Worker Task
        direction LR
        T1(Crawl) --> T2(Format);
    end

    P --> T1;
    T2 --> W;

    style DLQ fill:#f9f,stroke:#333,stroke-width:2px;
```

## External Dependencies

- See `tech_stack.md` for details on libraries and environment.

## Recent Significant Changes

- Initial project setup and Memory Bank initialization.
- Refined concurrency strategy: Adopted thread pool, atomic writes, and write-ahead logging; adjusted implementation plan phase order.
- Planned concurrency enhancements: Added Retry Circuit Breaker and Dead Letter Queue designs. Removed Resource Governor design.

## User Feedback Integration

- N/A at this stage.

## Additional Documentation

- `implementation_plan.md`: Detailed step-by-step plan for project development.
