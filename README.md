# RSS Feed Processor

A Python application to ingest, parse, and store podcast RSS feed data in SQLite. Designed for private podcast feeds with robust error handling and performance optimizations.

## Features

- Fast feed processing (729 episodes in ~1.1 seconds)
- SQLite storage with efficient indexing
- Duplicate episode handling
- Timezone-aware datetime handling
- Comprehensive test coverage
- Support for iTunes podcast fields

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TRIH-rss-ingest.git
cd TRIH-rss-ingest
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.template` to `.env` and configure:
```bash
cp .env.template .env
# Edit .env and add your RSS feed URL
```

## Configuration

Required environment variables in `.env`:
- `RSS_FEED_URL`: URL of the RSS feed to process (including any auth tokens)

## Usage

### Basic Usage

Run the feed processor:
```bash
python -m src.main
```

This will:
1. Fetch the RSS feed
2. Parse all episodes
3. Store them in SQLite (`data/episodes.db`)
4. Display the 5 most recent episodes

### Performance

Typical performance metrics:
- Feed fetching: ~1.0 seconds
- XML parsing: ~0.03 seconds
- Database storage: ~0.01 seconds
- Total processing: ~1.1 seconds for 729 episodes

### Database Schema

The SQLite database (`data/episodes.db`) contains:

**episodes table:**
- `id`: INTEGER PRIMARY KEY
- `guid`: TEXT UNIQUE - Unique episode identifier
- `title`: TEXT - Episode title
- `description`: TEXT - Episode description
- `link`: TEXT - Episode web link (optional)
- `published_date`: TIMESTAMP - Publication date with timezone
- `duration`: TEXT - Episode duration (optional)
- `audio_url`: TEXT - Direct URL to audio file
- `created_at`: TIMESTAMP - Record creation time
- `updated_at`: TIMESTAMP - Record last update time

**Indexes:**
- `idx_episodes_guid`: For fast lookups by GUID
- `idx_episodes_published_date`: For efficient date-based queries

### Error Handling

The application handles common errors:
- Network issues during feed fetch
- Invalid XML content
- Missing required fields
- Database connection problems
- Duplicate episodes

Error messages are logged with context for debugging.

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run specific test files:
```bash
python -m pytest tests/test_feed_ingest.py  # Feed ingestion tests
python -m pytest tests/test_storage.py      # Storage tests
python -m pytest tests/test_integration.py  # Integration tests
```

### Deployment Tips

1. **Cron Job Setup**
   ```bash
   # Example: Run every hour
   0 * * * * cd /path/to/TRIH-rss-ingest && ./venv/bin/python -m src.main >> /var/log/feed-processor.log 2>&1
   ```

2. **Logging**
   - Logs are written to stdout/stderr
   - Redirect to files when running as a service
   - Consider log rotation for long-term deployment

3. **Database Maintenance**
   - Regular backups recommended
   - SQLite is self-contained, just copy `data/episodes.db`
   - Consider periodic VACUUM for space optimization

## Development

### Project Structure

```
TRIH-rss-ingest/
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

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request 