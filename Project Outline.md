# Project Outline: RSS Feed Processor

## Overview
The RSS Feed Processor is a Python application that ingests a private podcast RSS feed, parses its XML content, and stores episode data in a SQLite database. In addition, the application supports AI-powered processing for:
- Cleaning episode descriptions (removing promotional content via regex and OpenAI API)
- Tagging episodes with thematic categories and curated tracks based on a predefined taxonomy

The application now features a comprehensive CLI for all operations and robust safety measures to protect production data.

## Directory Structure

dougvk-trih-rss-ingest/
├── README.md                         # Project overview, features, installation, usage, and deployment tips.
├── DEVELOPMENT_PLAN.md               # Roadmap of past and future development phases.
├── IDEAS.md                          # Ideas for future enhancements.
├── PRD.md                            # Comprehensive Product Requirements Document covering feed ingestion, cleaning, tagging, and validation.
├── requirements.txt                  # Python dependencies.
├── .env.template                     # Template for environment variables (e.g. RSS_FEED_URL).
├── scripts/                          # Legacy utility scripts (now replaced by CLI).
├── src/                              # Core application modules.
│   ├── init.py
│   ├── cli.py                        # Command line interface for all operations.
│   ├── cleaning.py                   # Implements content cleaning using regex and OpenAI API.
│   ├── config.py                     # Loads environment variables, sets up base paths, and manages configuration.
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
│   ├── conftest.py                   # Shared test fixtures and database isolation.
│   ├── test_cli.py                   # Tests for CLI functionality.
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

### Command Line Interface (cli.py)
The new CLI module provides a unified interface for all operations:
- **Environment Control**: Switches between production and test databases
- **Commands**:
  - `ingest`: Fetch and store feed data with optional limits
  - `clean`: Remove promotional content from descriptions
  - `tag`: Apply taxonomy tags to episodes
  - `export`: Export episode data to JSON
- **Safety Features**:
  - Dry run mode for all data-modifying operations
  - Batch size limits for testing
  - Single episode processing by GUID
  - Environment validation
  - Error handling and logging

### Feed Processing (feed_ingest.py)
- **Performance**: Optimized for large feeds (729+ episodes)
- **Parsing**: Uses lxml for efficient XML processing
- **Fields**: Handles required and optional podcast fields
- **Safety**: Configurable timeouts and validation
- **Testing**: Supports episode limits for testing

### Content Cleaning (cleaning.py)
- **Two-Step Process**:
  1. Regex-based cleaning with 40+ patterns
  2. AI-powered cleaning using OpenAI
- **Pattern Categories**: Social media, live shows, credits, etc.
- **Data Tracking**: Status, timestamps, and modification flags
- **Safety**: Dry run mode and batch limits

### Episode Tagging (tagging/)
- **AI Integration**: Uses OpenAI for intelligent tagging
- **Taxonomy**: Structured categorization system
- **Categories**: Format, Theme, Track, Episode Number
- **Validation**: Tag verification before storage
- **Safety**: Dry run mode and batch processing

### Database Management (storage.py)
- **Environments**: Separate production and test databases
- **Schema**: Optimized for episode metadata and tags
- **Safety**: Transaction support and error handling
- **Performance**: Indexed queries and efficient storage

### Testing Framework (tests/)
- **Coverage**: Unit and integration tests for all modules
- **Database**: Test isolation with separate database
- **Fixtures**: Mock data and shared test utilities
- **Safety**: Prevents production data modification

## Database Environments
The application now fully supports separate environments:
- **Production Database**: For live data (`data/episodes.db`)
- **Test Database**: For testing and development (`data/test.db`)
- **Environment Selection**: Via `--env` flag in CLI
- **Data Protection**: Test operations cannot affect production data
- **Database Copying**: Test database can be initialized from production