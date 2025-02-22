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
- `FEED_TOKEN`: Authentication token for the feed

## Development

- Code follows PEP 8 style guidelines
- Tests are written using pytest
- Run tests with: `pytest` 