# Phased Changes Plan for RSS Feed Processor

## Overview
This plan outlines incremental steps to further improve the codebase. The primary objectives are to:
- Refactor the codebase for API consistency and centralized configuration.
- Introduce a command-line interface (CLI) for running specific operations.
- Implement separate production and development/test databases to safeguard critical data.
- Update the test suite to support the new configuration and functionality (testing live API calls).

## Phase 1: Refactor Code Base for API Consistency
- **Objective:**  
  Standardize function signatures across modules and centralize configuration settings.
- **Actions:**
  - Move all hard-coded constants (e.g., sample sizes, timeouts) into `src/config.py` (or a dedicated constants module).
  - Refactor cleaning and tagging functions to uniformly accept parameters such as `dry_run`, `batch_size`, and `limit`.
  - Update logging and error handling to follow a consistent style throughout the codebase.
- **Outcome:**  
  A cleaner, more maintainable codebase that supports incremental testing and easy configuration.

## Phase 2: Introduce a Command-Line Interface (CLI)
- **Objective:**  
  Develop a CLI tool (e.g., `cli.py`) that allows you to run specific operations without affecting the entire system.
- **Actions:**
  - Implement command-line argument parsing (using argparse, for example) to support commands such as:
    - `ingest` – run feed fetching and parsing.
    - `clean` – execute content cleaning (or run `clean_single.py` for individual episodes).
    - `tag` – perform episode tagging (or run `tag_single.py` for a single episode).
    - `export` – export episode content.
  - Allow parameters (e.g., sample size, dry_run flags) to be passed via the CLI.
- **Outcome:**  
  Improved control over individual operations and the ability to verify each step in isolation.

## Phase 3: Implement Separate Production and Development/Test Databases
- **Objective:**  
  Protect critical production data from accidental updates during testing.
- **Actions:**
  - Update `src/config.py` (or create a new configuration module) to support an environment variable (e.g., `DB_ENV`) that distinguishes between `production` and `development`.
  - Configure two separate database paths:
    - **Production Database:** (e.g., `data/episodes_prod.db`) used only when changes are fully validated.
    - **Development/Test Database:** (e.g., `data/episodes_dev.db`) used for experimental changes and testing.
  - Modify database initialization (in `storage.py`) to use the correct DB path based on the active environment.
  - Add warnings or confirmation prompts when switching to production mode.
- **Outcome:**  
  A robust safeguard that ensures experimental features are tested on a separate database from your production data.

## Phase 4: Update and Expand Test Suite
- **Objective:**  
  Ensure all new changes are thoroughly tested.
- **Actions:**
  - Revise tests in the `tests/` folder to reflect the new unified API and configuration.
  - Configure tests to run against the development/test database.
  - We can run live API calls during testing since the cost is negligible. So you can remove mocks and use live API calls.
- **Outcome:**  
  A comprehensive test suite that validates all new functionality and configuration changes.

## Phase 5: Gradual Rollout and Production Promotion
- **Objective:**  
  Deploy changes to production only after thorough testing and manual verification.
- **Actions:**
  - Use the CLI with the `dry_run` flag and small batch sizes on the development/test database.
  - Manually verify the outputs for cleaning and tagging.
  - Gradually increase the batch size (e.g., from 10 → 25 → 50 → full dataset) on the development/test database.
  - Once fully validated, switch the configuration to use the production database and update it.
- **Outcome:**  
  A controlled and risk-mitigated rollout that protects production data.