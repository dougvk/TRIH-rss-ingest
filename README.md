# RSS Feed Processor

A Python application to ingest, parse, and store podcast RSS feed data.

## Setup

1. Clone the repository
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

4. Copy `.env.template` to `.env` and fill in your configuration:
```bash
cp .env.template .env
```

## Configuration

Required environment variables:
- `RSS_FEED_URL`: URL of the RSS feed to process

## Features

- Secure RSS feed fetching with proper error handling
- Robust XML parsing using lxml
- Structured episode data with dataclass models
- SQLite storage (coming soon)

## Development

- Code follows PEP 8 style guidelines
- Tests are written using pytest
- Run tests with: `pytest`

## Architecture

The application is structured into several key components:

1. **Feed Ingestion** (`src/feed_ingest.py`):
   - Fetches RSS feed content using requests
   - Parses XML using lxml
   - Converts feed entries to Episode objects

2. **Configuration** (`src/config.py`):
   - Manages environment variables
   - Validates required settings

3. **Data Models** (`src/models.py`):
   - Defines Episode dataclass
   - Handles data validation

4. **Storage** (`src/storage.py`) - Coming soon:
   - Will handle SQLite database operations
   - Will manage episode persistence 