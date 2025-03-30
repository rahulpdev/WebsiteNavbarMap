# Project Manual

Project Manual is a manual for software engineers that captures important patterns, preferences, and guidelines.

Project Manual instructions must be equally prioritised and strictly adhered to at all times.

## User interaction

- Ask follow-up questions when critical information is unclear or missing.
- Adjust approach based on user preferences.
- Strive for efficient task completion with minimal back-and-forth.
- Re-read conversation history to maintain context.
- Present key technical decisions concisely, allowing for user feedback.
- Don't fabricate solutions.
- Don't deviate into unrelated topics, modifications or enhancements.
- Restate your interpretation of key features and requirements to ensure alignment.
- Confirm relevant execution environment details.

## Problem-solving

- Exhaust all options before determining an action is impossible.
- When evaluating feasibility, check alternatives in all directions: up/down and left/right.
- Only conclude an action cannot be performed after all possibilities have been tested.

## Task breakdown and execution

- Break down all user instructions into clear, numbered steps.
- Include both actions and reasoning for each step.
- Flag potential issues before they arise.
- Verify the completion of each step before proceeding to the next.
- If errors occur, document them, return to previous steps, and retry as needed.

## Change management

- Review all changes to assess their impact across all other components of the project.
- Test changes thoroughly to ensure consistency and prevent conflicts.
- Before implementing code fixes, present a concise impact assessment on:

  - Project goals, requirements, scope and constraints.
  - Project structure, design, architecture and tech stack.

## Validation Protocol

- Pre-action validation: Match every planned action to exact requirement wording.
- Pre-action validation: Cross-reference all code actions with Project Manual.
- Post-action verification: Confirm output matches requirement spec.
- Deviation protocol: Stop and alert if any discrepancy emerges.

### Memory Bank Validation

1. After reading documents, create validation checklist in current_task.md
2. For each document:

- [ ] Verify requirements still match task
- [ ] Check for conflicting updates
- [ ] Confirm implementation constraints

3. Sign-off validation in project_tracker.md

## Assumption Prevention

1. Requirement cross-reference check for all decisions.
2. Three-way match between:
   a) Stated requirements
   b) Implementation plan
   c) Final code
3. Automated gap detection via:
   - Negative requirement analysis ("Must NOT" checks).
   - Boundary condition mapping.
