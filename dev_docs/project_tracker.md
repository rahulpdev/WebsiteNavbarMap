# Project Tracker

## Overview

This document tracks the progress of the Website Navigation Map generator project against the goals defined in `project_brief.md`.

## Goals & Key Features/Tasks

### Goal 1: Core Functionality - Generate Navigation Maps

- [ ] **Feature: CSV Input Processing**
  - [ ] Implement script to read CSV files from a designated input folder.
  - [ ] Implement URL validation logic (format, whitespace).
  - [ ] Implement non-blocking validation (process valid rows even if others fail).
  - [ ] Implement error logging for invalid rows (including line numbers).
- [ ] **Feature: Command Line Interface (CLI)**
  - [ ] Display numbered list of validated URLs (domain only) from CSVs.
  - [ ] Prompt user for numerical input corresponding to a URL.
  - [ ] Validate user input (must be a valid number in the list or "exit").
  - [ ] Handle invalid input and re-prompt.
  - [ ] Handle "exit" command.
  - [ ] Trigger crawling process upon valid selection.
- [ ] **Feature: Website Navigation Crawling**
  - [ ] Implement function to fetch website HTML content.
  - [ ] Implement logic to identify navigation menu elements (requires robust selectors).
  - [ ] Implement recursive traversal of sub-menus.
  - [ ] Extract page details: name, full URL, last updated (if available).
  - [ ] Handle network errors gracefully (retry logic, logging).
  - [ ] Handle HTML parsing errors gracefully (logging).
- [ ] **Feature: Markdown Output Generation**
  - [ ] Implement logic to format extracted data into the specified tree structure.
  - [ ] Implement function to write the tree structure to a `<website_name>_nav_map.md` file.
  - [ ] Ensure output files are saved to a designated output folder.
  - [ ] Ensure file naming convention is followed.
- [ ] **Feature: Concurrency**
  - [ ] Implement thread-per-row processing for CSV validation/crawling.
  - [ ] Implement a write queue for atomic markdown file generation.
  - [ ] Implement file locking (`fcntl` or alternative) for output files.
- [ ] **Feature: Error Handling & Logging**
  - [ ] Implement comprehensive logging (info, warning, error) in a structured format.
  - [ ] Ensure all specified error types (Network, Parsing, I/O) are handled.

### Goal 2: Documentation & Setup

- [x] **Task: Initialize Memory Bank**
  - [x] Create `dev_docs` directory.
  - [x] Create `project_brief.md` (User provided).
  - [x] Create `codebase_summary.md`.
  - [x] Create `tech_stack.md`.
  - [x] Create `current_task.md`.
  - [x] Create `project_tracker.md`.
- [ ] **Task: Set up Project Structure**
  - [ ] Create input folder for CSV files.
  - [ ] Create output folder for markdown map files.
  - [ ] Initialize Git repository.
- [ ] **Task: Complete Documentation**
  - [ ] Review and refine all Memory Bank documents.
  - [ ] Add comments to code where necessary.
  - [ ] Create README.md for GitHub.
- [ ] **Task: GitHub Repository**
  - [ ] Create public GitHub repository.
  - [ ] Push initial project structure and Memory Bank.
  - [ ] Ensure at least one example `_nav_map.md` file is present upon completion.

## Completed Tasks

- Initialize Memory Bank (`project_brief.md`, `codebase_summary.md`, `tech_stack.md`, `current_task.md`, `project_tracker.md`).

## Memory Bank Document Versions

- `project_brief.md`: v1.0 (Initial) - 2025-03-30
- `codebase_summary.md`: v1.0 (Initial) - 2025-03-30
- `tech_stack.md`: v1.0 (Initial) - 2025-03-30
- `current_task.md`: v1.0 (Initial) - 2025-03-30
- `project_tracker.md`: v1.0 (Initial) - 2025-03-30
