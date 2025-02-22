# Podcast Feed Processor - PRD

## Overview

The Podcast Feed Processor is a lean application designed to ingest a private podcast RSS feed, parse the episode details, and store the data for future search and analysis. The application focuses on performance, reliability, and maintainability, successfully handling feeds with hundreds of episodes.

## Objectives

- **Data Ingestion:** Securely fetch a private RSS feed using HTTP requests with appropriate authentication.
- **Data Parsing:** Extract episode metadata using robust XML parsing with `lxml`.
- **Data Storage:** Persist the parsed data in a SQLite database with efficient indexing.
- **Modular Architecture:** Clean, tested, and documented codebase with comprehensive test coverage.

## User Stories

- **As a user,** I want to run a script that automatically downloads and parses my private podcast RSS feed so that I have a local copy of all episode details.
- **As a user,** I need the tool to handle private feed URLs with embedded authentication.
- **As a user,** I want the parsed episode data to be stored efficiently for future search and categorization.
- **As a user,** I want to see the latest episodes after each update.

## Requirements

### Functional Requirements

1. **RSS Feed Ingestion:**
   - Fetch private RSS feed using HTTP GET request
   - Handle authentication via URL tokens
   - Support timeout and error handling
   - Performance: ~1.0s for feed fetch

2. **RSS Parsing:**
   - Parse XML feed using `lxml` for robust handling
   - Support iTunes podcast namespace fields
   - Extract fields:
     - Required: title, description, guid, published_date
     - Optional: link, duration, audio_url
   - Performance: ~0.03s for 729 episodes

3. **Data Storage:**
   - SQLite database with proper indexes
   - Efficient batch episode storage
   - Automatic duplicate handling via GUID
   - Performance: ~0.01s for 729 episodes

4. **Configuration:**
   - Environment variables via `.env` file
   - Feed URL configuration
   - Database path management
   - Validation of required settings

### Non-Functional Requirements

- **Performance:** Process 729 episodes in ~1.1 seconds total
- **Modularity:** Clean separation between feed ingestion, parsing, and storage
- **Error Handling:** Comprehensive error handling with logging
- **Documentation:** Detailed inline documentation and usage examples
- **Testing:** Unit tests, integration tests, and mock feed testing

## Architecture & Design

### Folder Structure

```
podcast_feed_processor/
├── README.md
├── requirements.txt
├── .env
├── data/
│   └── episodes.db
├── src/
│   ├── __init__.py
│   ├── config.py      # Configuration management
│   ├── feed_ingest.py # Feed fetching and parsing
│   ├── models.py      # Data models
│   ├── storage.py     # Database operations
│   └── main.py        # Main orchestration
└── tests/
    ├── __init__.py
    ├── conftest.py    # Test fixtures
    ├── test_config.py
    ├── test_feed_ingest.py
    ├── test_storage.py
    └── test_integration.py
```

### Technology Stack

- **Programming Language:** Python 3.13
- **Libraries:**
  - `requests` for HTTP requests
  - `lxml` for XML parsing
  - `python-dotenv` for configuration
  - `sqlite3` for database operations
  - `pytest` for testing
  - `requests-mock` for test mocking

### Key Modules and Their Roles

1. **src/config.py**
   - Environment variable management
   - Path configuration
   - Validation logic

2. **src/feed_ingest.py**
   - Feed fetching with error handling
   - XML parsing with `lxml`
   - iTunes namespace support

3. **src/models.py**
   - Episode dataclass
   - Field validation
   - Type hints

4. **src/storage.py**
   - SQLite connection management
   - Efficient batch operations
   - Transaction handling

5. **src/main.py**
   - Process orchestration
   - Performance logging
   - Error handling

## Implementation Details

### Database Schema

```sql
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    link TEXT NOT NULL,
    published_date TIMESTAMP NOT NULL,
    duration TEXT,
    audio_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodes_guid ON episodes(guid);
CREATE INDEX idx_episodes_published_date ON episodes(published_date);
```

### Performance Metrics

Measured with 729 episodes:
- Feed Fetch: ~1.0 seconds
- XML Parse: ~0.03 seconds
- DB Storage: ~0.01 seconds
- Total Time: ~1.1 seconds

### Error Handling

- Network timeouts and retries
- XML parsing recovery
- Database transaction rollback
- Comprehensive logging

### Testing Strategy

1. **Unit Tests:**
   - Individual component testing
   - Mock external dependencies

2. **Integration Tests:**
   - End-to-end workflow testing
   - Mock feed with 729 episodes
   - Database operations

3. **Performance Tests:**
   - Timing measurements
   - Resource usage monitoring

## Deployment

### Requirements

- Python 3.13+
- Virtual environment
- `.env` file with feed URL
- Write access for database

### Monitoring

- Logging to stdout/stderr
- Performance metrics logging
- Error tracking

### Maintenance

- Database backups
- Log rotation
- VACUUM optimization