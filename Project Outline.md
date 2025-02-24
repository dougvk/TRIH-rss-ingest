# Project Outline – Podcast RSS Feed Processor

## Overview

The Podcast RSS Feed Processor is a modular Python application that ingests, cleans, tags, and stores podcast RSS feed data. It leverages AI to clean and tag episode content and provides a robust command-line interface (CLI) to control these operations. The system is designed for rapid processing, reliable error handling, and easy extensibility.

## Directory Structure

dougvk-trih-rss-ingest/
├── README.md                   # Overview, installation, usage, and deployment instructions.
├── IDEAS.md                    # Future enhancement ideas.
├── PRD.md                      # Detailed Product Requirements Document.
├── Project Outline.md          # This document.
├── requirements.txt            # Python dependencies.
├── .env.template               # Template for environment configuration.
├── src/                        # Core application source code.
│   ├── init.py             # Package initializer.
│   ├── config.py               # Configuration management.
│   ├── feed_ingest.py          # RSS feed fetching and parsing.
│   ├── cleaning.py             # Two-stage cleaning (regex and AI-based).
│   ├── models.py               # Data models (Episode dataclass, etc.).
│   ├── storage.py              # SQLite database operations.
│   ├── openai_client.py        # OpenAI API integration.
│   ├── cli.py                  # Primary CLI entry point.
│   ├── cli/                    # CLI submodule.
│   │   ├── init.py         # CLI package initializer.
│   │   ├── main.py             # CLI application entry point.
│   │   ├── utils.py            # CLI utility functions.
│   │   └── commands/           # Individual CLI command implementations.
│   │       ├── base.py         # Base class for CLI commands.
│   │       ├── ingest.py       # Command for feed ingestion.
│   │       ├── clean.py        # Command for cleaning episode descriptions.
│   │       ├── tag.py          # Command for tagging episodes.
│   │       ├── export.py       # Command for exporting episode data.
│   │       ├── validate.py     # Command for validating episode tags.
│   │       └── registry.py     # Registry for CLI commands.
│   └── tagging/                # AI-based tagging modules.
│       ├── init.py         # Tagging package initializer.
│       ├── processor.py        # Batch processing for tagging.
│       ├── prompt.py           # Prompt construction for OpenAI.
│       ├── tagger.py           # Integration with OpenAI for generating tags.
│       ├── taxonomy.py         # Taxonomy management (tag definitions and validation).
│       └── taxonomy/           # Detailed taxonomy submodule.
│           ├── init.py
│           ├── constants.py    # Taxonomy constants.
│           ├── schema.py       # Tag set type definitions and schema.
│           ├── structure.py    # Structured taxonomy with validation rules.
│           ├── taxonomy.py     # Core taxonomy logic and singleton instance.
│           └── testing.py      # Taxonomy testing utilities.
├── tests/                      # Automated tests (unit, integration, CLI, and performance).
│   ├── init.py             # Test package initializer.
│   ├── conftest.py            # Shared fixtures and test configuration.
│   ├── test_config.py         # Tests for configuration management.
│   ├── test_feed_ingest.py    # Tests for RSS feed ingestion.
│   ├── test_storage.py        # Tests for SQLite database operations.
│   ├── test_tagging.py        # Tests for AI tagging functionality.
│   ├── test_integration.py    # End-to-end integration tests.
│   └── cli/                   # CLI command tests.
│       ├── test_base.py
│       ├── test_clean.py
│       ├── test_export.py
│       ├── test_ingest.py
│       ├── test_main.py
│       ├── test_tag.py
│       └── test_validate.py
└── .cursor/                    # Coding rules and guidelines.
├── rules/
│   ├── feed-ingestion.mdc # Guidelines for RSS feed ingestion.
│   ├── general.mdc        # Coding style, configuration, and testing guidelines.
│   └── storage.mdc        # Guidelines for SQLite storage operations.

## Detailed Component Breakdown

### 1. Feed Ingestion
- **Module:** `src/feed_ingest.py`
- **Description:**  
  - Fetches RSS feed content via HTTP (or local files) and parses XML using `lxml`.  
  - Extracts required episode data such as GUID, title, description, link, publication date, duration, and audio URL.  
  - Includes robust error handling for network or XML parsing errors.

### 2. Content Cleaning
- **Module:** `src/cleaning.py`
- **Description:**  
  - Implements a two-stage cleaning process:  
    1. Regex-based filtering removes known promotional patterns (e.g., social media links, tour announcements).  
    2. An AI-based step (using OpenAI API) cleans remaining extraneous content while preserving historical information.
  - Supports both dry-run and batch cleaning modes.

### 3. Episode Tagging
- **Modules:** `src/tagging/` (including `tagger.py`, `prompt.py`, and `taxonomy.py`)
- **Description:**  
  - Constructs prompts based on episode title and description for use with the OpenAI API.  
  - Uses AI to generate a set of tags that conform to a strict taxonomy.  
  - Updates the database with the validated tags and extracts episode numbers when applicable.

### 4. Tagging Taxonomy

The tagging taxonomy is defined as follows:

#### Format Tags
- **Series Episodes**
- **Standalone Episodes**
- **RIHC Series**

#### Theme Tags
- **Ancient & Classical Civilizations**
- **Medieval & Renaissance Europe**
- **Empire, Colonialism & Exploration**
- **Modern Political History & Leadership**
- **Military History & Battles**
- **Cultural, Social & Intellectual History**
- **Science, Technology & Economic History**
- **Religious, Ideological & Philosophical History**
- **Historical Mysteries, Conspiracies & Scandals**
- **Regional & National Histories**

#### Track Tags
- **Roman Track**
- **Medieval & Renaissance Track**
- **Colonialism & Exploration Track**
- **American History Track**
- **Military & Battles Track**
- **Modern Political History Track**
- **Cultural & Social History Track**
- **Science, Technology & Economic History Track**
- **Religious & Ideological History Track**
- **Historical Mysteries & Conspiracies Track**
- **British History Track**
- **Global Empires Track**
- **World Wars Track**
- **Ancient Civilizations Track**
- **Regional Spotlight: Latin America Track**
- **Regional Spotlight: Asia & the Middle East Track**
- **Regional Spotlight: Europe Track**
- **Regional Spotlight: Africa Track**
- **Historical Figures Track**
- **The RIHC Bonus Track**
- **Archive Editions Track**
- **Contemporary Issues Through History Track**

*Note:* The taxonomy rules enforce that, for example, if an episode is tagged as "RIHC Series" then it must also have "Series Episodes" in its Format.

### 5. Data Storage
- **Module:** `src/storage.py`
- **Description:**  
  - Initializes and manages the SQLite database.  
  - Provides CRUD operations with transaction safety and rollback on errors.  
  - Creates indexes on key fields (e.g., GUID, publication date) for efficient querying.

### 6. Configuration
- **Module:** `src/config.py`
- **Description:**  
  - Loads environment variables from a `.env` file (using `python-dotenv`).  
  - Manages paths for data storage and validates required settings such as `RSS_FEED_URL` and `OPENAI_API_KEY`.

### 7. Command-Line Interface (CLI)
- **Modules:** `src/cli/` and `src/cli/commands/`
- **Description:**  
  - Provides a set of commands using Python’s `argparse` to perform key operations:
    - **ingest:** Fetches and stores RSS feed data.
    - **clean:** Cleans episode descriptions.
    - **tag:** Tags episodes using the AI-driven taxonomy.
    - **export:** Exports episode data in JSON or CSV format.
    - **validate:** Validates episode tags against the taxonomy and can generate a detailed report.
  - Supports global flags for environment selection, dry-run mode, and debug output.

### 8. Testing Framework
- **Directory:** `tests/`
- **Description:**  
  - Contains unit tests for each module, integration tests, and CLI command tests.  
  - Uses fixtures for temporary databases and mocks for external API calls to ensure reliable test runs.

### 9. Coding Guidelines & Standards
- **Directory:** `.cursor/rules/`
- **Description:**  
  - Provides implementation rules for feed ingestion, general coding standards (PEP 8), and SQLite storage best practices.