# Project Outline: RSS Feed Processor

## Overview
The RSS Feed Processor is a Python application that ingests a private podcast RSS feed, parses its XML content, and stores episode data in a SQLite database. In addition, the application supports AI-powered processing for:
- Cleaning episode descriptions (removing promotional content via regex and OpenAI API)
- Tagging episodes with thematic categories and curated tracks based on a predefined taxonomy

This document provides a detailed explanation of the updated codebase, its structure, and the intent of each component.

## Directory Structure

dougvk-trih-rss-ingest/
├── README.md                         # Project overview, features, installation, usage, and deployment tips.
├── DEVELOPMENT_PLAN.md               # Roadmap of past and future development phases.
├── IDEAS.md                          # Ideas for future enhancements.
├── PRD.md                            # Comprehensive Product Requirements Document covering feed ingestion, cleaning, tagging, and validation.
├── requirements.txt                  # Python dependencies.
├── .env.template                     # Template for environment variables (e.g. RSS_FEED_URL).
├── scripts/                          # Utility scripts for testing and individual operations.
│   ├── init.py
│   ├── clean_single.py               # Script to clean a single episode (by GUID).
│   ├── export_content.py             # Exports all episode content to a text file.
│   ├── tag_single.py                 # Script to tag a single episode (by GUID).
│   ├── test_cleaning.py              # Test script for the cleaning functionality.
│   ├── test_fetch.py                 # Test script for RSS feed fetching.
│   ├── test_parse.py                 # Test script for RSS feed parsing.
│   ├── test_tagging.py               # Test script for batch tagging.
│   └── validate_tags.py              # Script to validate that episode tags conform to taxonomy rules.
├── src/                              # Core application modules.
│   ├── init.py
│   ├── cleaning.py                   # Implements content cleaning using regex and OpenAI API.
│   ├── config.py                     # Loads environment variables, sets up base paths, and manages configuration (including DB settings).
│   ├── feed_ingest.py                # Fetches the RSS feed and parses it using lxml.
│   ├── main.py                       # Main orchestration module that ties together ingestion, parsing, and storage.
│   ├── models.py                     # Defines the Episode dataclass and other data models.
│   ├── storage.py                    # Handles SQLite database operations (initialization, CRUD, and indexing).
│   └── tagging/                      # AI-based tagging submodule.
│       ├── Tagging-Episodes-Framework.md  # Tag taxonomy and curated track suggestions.
│       ├── init.py
│       ├── processor.py              # Batch processing for tagging episodes.
│       ├── prompt.py                 # Constructs prompts by loading and parsing the taxonomy.
│       └── tagger.py                 # Integrates with the OpenAI API to generate and validate tags.
├── tests/                            # Automated test suite (unit, integration, and performance tests).
│   ├── init.py
│   ├── conftest.py                   # Shared test fixtures.
│   ├── test_config.py                # Tests for configuration and environment variable handling.
│   ├── test_feed_ingest.py           # Tests for feed fetching and parsing.
│   ├── test_integration.py           # End-to-end integration tests using a mock feed.
│   ├── test_main.py                  # Tests for main orchestration.
│   ├── test_storage.py               # Tests for database operations.
│   └── test_tagging.py               # Tests for tagging functionality.
└── .cursor/                          # Coding standards and implementation rules.
└── rules/
├── feed-ingestion.mdc        # Guidelines for feed ingestion implementation.
├── general.mdc               # General coding, configuration, and testing guidelines.
└── storage.mdc               # Rules for SQLite storage and schema management.

## Detailed Component Explanations

- **README.md:**  
  Provides a high-level overview, including features (fast processing, robust error handling, comprehensive test coverage), installation instructions, usage examples, and deployment tips.

- **DEVELOPMENT_PLAN.md:**  
  Outlines completed and upcoming development phases.

- **IDEAS.md:**  
  Contains future ideas such as integrating additional data sources or refining thematic tagging.

- **PRD.md:**  
  The unified Product Requirements Document that describes all core functionalities:
  - **Feed Processing:** Ingestion, XML parsing, and storage.
  - **Content Cleaning:** Removing promotional content using regex and AI.
  - **Episode Tagging:** AI-driven tagging based on a detailed taxonomy.
  - **Tag Validation:** Ensuring that generated tags conform to predefined rules.

- **Scripts Folder:**  
  Contains standalone scripts:
  - **clean_single.py** and **tag_single.py** let you run cleaning or tagging on individual episodes by GUID.
  - **export_content.py** exports episode data.
  - **validate_tags.py** checks that episode tags meet taxonomy and series rules.
  - Test scripts (test_cleaning.py, test_fetch.py, test_parse.py, test_tagging.py) support development and debugging.

- **src Folder:**  
  Contains the core modules:
  - **config.py:** Handles environment variables and configuration. *(Future improvements will enable switching between production and development/test databases.)*
  - **feed_ingest.py:** Uses `requests` and `lxml` to fetch and parse the RSS feed.
  - **models.py:** Defines the Episode dataclass that encapsulates episode metadata.
  - **storage.py:** Manages all interactions with the SQLite database.
  - **cleaning.py:** Implements the two-step content cleaning process.
  - **tagging Submodule:**  
    - **Tagging-Episodes-Framework.md:** Contains the taxonomy for thematic tagging.
    - **processor.py:** Orchestrates batch tagging.
    - **prompt.py:** Constructs detailed prompts for the AI using the taxonomy.
    - **tagger.py:** Makes API calls to OpenAI to generate tags and updates the database.

- **Tests Folder:**  
  Includes unit and integration tests to validate each component of the application.

- **.cursor/rules Folder:**  
  Contains coding style and implementation guidelines to maintain consistency and quality.

## Database Environments
The current configuration uses a single SQLite database (default: `data/episodes.db`). Future updates will add support for two separate environments:
- **Production Database:** For live data and final verified results.
- **Development/Test Database:** For experimental changes and rapid testing without risk to production data.