# Project Tracker

## Overview

This document tracks the progress of the Website Navigation Map generator project against the goals defined in `project_brief.md`.

## Goals & Key Features/Tasks

### Goal 1: Core Functionality - Generate Navigation Maps

- [x] **Feature: CSV Input Processing**
  - [x] Implement script to read CSV files from a designated input folder.
  - [x] Implement URL validation logic (format, whitespace).
  - [x] Implement non-blocking validation (process valid rows even if others fail).
  - [x] Implement error logging for invalid rows (including line numbers).
- [x] **Feature: Command Line Interface (CLI)**
  - [x] Display numbered list of validated URLs (domain only) from CSVs.
  - [x] Prompt user for numerical input corresponding to a URL.
  - [x] Validate user input (must be a valid number in the list or "exit").
  - [x] Handle invalid input and re-prompt.
  - [x] Handle "exit" command.
  - [x] Trigger crawling process upon valid selection.
  - [x] Add progress bar (`tqdm`) for crawling phase.
- [x] **Feature: Website Navigation Crawling**
  - [x] Implement function to fetch website HTML content.
  - [x] Implement logic to identify navigation menu elements (requires robust selectors).
  - [x] Implement recursive traversal of sub-menus.
  - [x] Extract page details: name, full URL, last updated (if available).
  - [x] Handle network errors gracefully (retry logic, logging).
  - [x] Handle HTML parsing errors gracefully (logging).
- [x] **Feature: Markdown Output Generation**
  - [x] Implement logic to format extracted data into the specified tree structure.
  - [x] Implement function to write the tree structure to a `<website_name>_nav_map.md` file.
  - [x] Ensure output files are saved to a designated output folder.
  - [x] Ensure file naming convention is followed.
- [x] **Feature: Concurrency**
  - [x] Implement thread pool executor (`concurrent.futures.ThreadPoolExecutor`) for managing tasks.
  - [x] Implement atomic write pattern using temporary files and `os.rename` to mitigate race conditions.
  - [x] Implement write-ahead logging with transaction markers (e.g., `.lock` files) to handle partial writes.
  - [x] Implement stale lock file cleanup mechanism (e.g., timestamp-based).
  - [x] **Enhancement: Retry Circuit Breaker**
    - [x] Implement exponential backoff with jitter for retries (max 3 attempts).
    - [ ] Implement fallback to synchronous mode on thread exhaustion (TBD - Deferred).
  - [x] **Enhancement: Dead Letter Queue (DLQ)**
    - [x] Implement persistent storage for failed tasks (e.g., simple file-based queue).
    - [x] Implement mechanism to log/notify about DLQ entries.
    - [ ] (Optional) Implement automatic retry from DLQ on system restart (Deferred).
- [x] **Feature: Error Handling & Logging**
  - [x] Implement comprehensive logging (info, warning, error) in a structured format (JSON for files).
  - [x] Ensure all specified error types (Network, Parsing, I/O, Concurrency) are handled.
  - [x] Integrate thread-specific metadata into logs.

### Goal 2: Documentation & Setup

- [x] **Task: Initialize Memory Bank**
  - [x] Create `dev_docs` directory.
  - [x] Create `project_brief.md` (User provided).
  - [x] Create `codebase_summary.md`.
  - [x] Create `tech_stack.md`.
  - [x] Create `current_task.md`.
  - [x] Create `project_tracker.md`.
- [x] **Task: Create Implementation Plan**
  - [x] Create `dev_docs/implementation_plan.md`.
- [x] **Task: Set up Project Structure**
  - [x] Create input folder for CSV files (`input_csvs/`).
  - [x] Create output folder for markdown map files (`output_maps/`).
  - [x] Initialize Git repository.
  - [x] Create `.gitignore`.
  - [x] Create `requirements.txt`.
  - [x] Create `src/` structure with placeholder files.
  - [x] Create `logs/` directory.
  - [x] Create `tests/` structure.
- [ ] **Task: Complete Documentation**
  - [ ] Review and refine all Memory Bank documents.
  - [ ] Add comments to code where necessary.
  - [x] Create README.md for GitHub.
  - [x] Create CHANGELOG.md.
  - [x] Create `.clineignore`.
- [x] **Task: GitHub Repository**
  - [x] Create public GitHub repository.
  - [x] Push initial project structure and Memory Bank.
  - [x] Ensure at least one example `_nav_map.md` file is present upon completion. (User action pending - assumed complete for finalization)

## Completed Tasks

- Initialize Memory Bank (`project_brief.md`, `codebase_summary.md`, `tech_stack.md`, `current_task.md`, `project_tracker.md`).
- Create `dev_docs/implementation_plan.md`.
- Set up Project Structure (Folders, Git, `.gitignore`, `requirements.txt`, `src/`, `logs/`, `tests/`).
- Implement Core Modules (Logging, CSV Processor, Utils, Crawler, File Writer).
- Implement Concurrency Framework (ThreadPool, Atomic Writes, WAL, Retries, DLQ).
- Implement CLI Integration (`main.py`).
- Implement Initial Unit Tests (`tests/test_utils.py`, `tests/test_csv_processor.py`, `tests/test_crawler.py`).
- Code Refinement (Test file docstrings).
- Create README.md, CHANGELOG.md, .clineignore.
- GitHub Repository Setup (Create repo, push initial commit).
- Add `tqdm` progress bar.
- Fix crawler bugs (duplicate URLs, indentation).
- User verification of successful run and output.

## Memory Bank Document Versions

- `project_brief.md`: v1.0 (Initial) - 2025-03-30
- `codebase_summary.md`: v1.3 (Add tqdm) - 2025-03-31
- `tech_stack.md`: v1.1 (Add tqdm) - 2025-03-31
- `current_task.md`: v1.10 (Verified run) - 2025-03-31
- `project_tracker.md`: v1.9 (Verified run) - 2025-03-31
- `implementation_plan.md`: v1.2 (Added concurrency enhancements) - 2025-03-30
