# Podcast RSS Feed Processor – Product Requirements Document (PRD)

## Overview

The Podcast RSS Feed Processor is a high-performance, Python‐based application designed to ingest private podcast RSS feeds, parse and clean episode content, and automatically tag episodes using AI. It stores the processed data in a local SQLite database and provides a comprehensive command-line interface (CLI) to control each operation. The system emphasizes reliability, speed, and extensibility while leveraging AI (via OpenAI models) for advanced content cleaning and taxonomy-based tagging.

## Problem Statement

Many podcasters and private feed curators need a robust solution that:
- Efficiently ingests and parses large RSS feeds.
- Removes unwanted promotional material and formatting inconsistencies from episode descriptions.
- Automatically categorizes and tags episodes based on historical themes and content—reducing manual curation.
- Provides an auditable, high-performance storage mechanism for rapid querying and future integrations.

## Goals

1. **Reliable Feed Ingestion**
   - Securely fetch RSS feed content (supporting both remote and local sources).
   - Parse the feed with robust error handling using the `lxml` library.
   - Extract essential fields (title, description, link, publication date, duration, audio URL, etc.).

2. **Content Cleaning**
   - Remove promotional content and extraneous formatting via a two-step cleaning process:
     - Regex-based filtering for known patterns.
     - AI-based content cleaning using OpenAI’s API for context-sensitive removal.
   - Track cleaning status, timestamps, and preserve both original and cleaned versions.

3. **Episode Tagging**
   - Utilize a predefined taxonomy to assign tags for Format, Theme, and Track.
   - Automatically extract episode numbers from titles when applicable.
   - Validate and enforce tagging rules to ensure consistency across episodes.

4. **Data Storage & Performance**
   - Store episodes in a SQLite database with well-designed indexes for fast retrieval.
   - Provide mechanisms to update episodes on duplicate detection.
   - Achieve rapid processing even for feeds with hundreds of episodes.

5. **Command-Line Interface (CLI)**
   - Support operations for feed ingestion, cleaning, tagging, exporting, and tag validation.
   - Offer dry-run modes, batch processing, and single-episode operations.
   - Allow switching safely between production and test environments.

6. **Testing & Maintainability**
   - Include a comprehensive test suite (unit, integration, and performance tests).
   - Follow strict coding standards and guidelines to ensure consistent implementation.
   - Facilitate future enhancements with minimal friction.

## Core Features

- **Feed Ingestion:** Securely fetch and parse RSS feeds (including iTunes-specific fields) with robust error handling.
- **Content Cleaning:** Apply a two-stage cleaning process (regex and OpenAI API) to remove promotional and irrelevant content.
- **Episode Tagging:** Automatically assign taxonomy-based tags (Format, Theme, Track) and extract episode numbers when needed.
- **Database Storage:** Use SQLite to store and index episode data with duplicate handling and efficient queries.
- **CLI Operations:** Provide commands for ingestion, cleaning, tagging, exporting data (JSON/CSV), and validating tag integrity.
- **Performance & Reliability:** Achieve high processing speed with detailed logging and error handling for both production and test environments.

## Database Schema

The SQLite database (typically at `data/episodes.db`) contains an `episodes` table with fields such as:

- **id:** INTEGER PRIMARY KEY AUTOINCREMENT  
- **guid:** TEXT UNIQUE – a unique identifier for each episode  
- **title:** TEXT – episode title  
- **description:** TEXT – original episode description  
- **cleaned_description:** TEXT – cleaned version of the description  
- **link:** TEXT – episode web link  
- **published_date:** TIMESTAMP – publication date (timezone-aware)  
- **duration:** TEXT – episode duration  
- **audio_url:** TEXT – URL to the audio file  
- **cleaning_timestamp:** TIMESTAMP – when cleaning was performed  
- **cleaning_status:** TEXT – status of the cleaning process (e.g., “pending”, “cleaned”)  
- **tags:** TEXT – JSON string storing taxonomy tags  
- **tagging_timestamp:** TIMESTAMP – when tagging was applied  
- **episode_number:** INTEGER – extracted episode number (if applicable)  
- **created_at / updated_at:** TIMESTAMP – record creation and update timestamps  

Indexes are defined on fields such as `guid`, `published_date`, `cleaning_status`, `tags`, and `episode_number` to ensure fast lookups.

## Tagging Taxonomy

The system uses a strict taxonomy to standardize tagging. The taxonomy is divided into three main categories:

### Format Tags
- **Series Episodes**
- **Standalone Episodes**
- **RIHC Series**

### Theme Tags
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

### Track Tags
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

*Note:* Specific rules (e.g., if an episode is tagged as "RIHC Series" it must also have "Series Episodes") ensure consistency across the dataset.

## CLI Command Overview

The application exposes a rich CLI with the following commands:

- **ingest:**  
  - **Purpose:** Fetch and store RSS feed data.
  - **Details:** Retrieves feed content using HTTP (or from a file), parses the XML to extract episode information, and stores episodes into the SQLite database. Supports optional limits for testing.

- **clean:**  
  - **Purpose:** Clean episode descriptions.
  - **Details:** Uses a two-stage cleaning process. First, it applies regex patterns to remove known promotional text and extraneous data; then it calls the OpenAI API for context-sensitive cleaning. Supports single-episode cleaning by GUID as well as batch processing with a limit.

- **tag:**  
  - **Purpose:** Tag episodes using the predefined taxonomy.
  - **Details:** Constructs a prompt from the episode title and (cleaned) description, sends it to the OpenAI API, and processes the returned JSON to update the episode’s tags in the database. Can tag a single episode by GUID or process multiple episodes in a batch.

- **export:**  
  - **Purpose:** Export episode data.
  - **Details:** Extracts episodes from the database and exports them to a file in JSON or CSV format. Allows selecting specific fields to include and supports both dry-run and live export modes.

- **validate:**  
  - **Purpose:** Validate episode tags against the taxonomy.
  - **Details:** Checks that all episodes (or a subset via limit or GUID) have tags that conform to the taxonomy rules. Optionally generates a detailed JSON report listing any invalid or missing tags.

## Technology Stack

- **Language:** Python 3.13+
- **Core Libraries:** 
  - `requests` for HTTP operations
  - `lxml` for XML parsing
  - `sqlite3` for database operations
  - `openai` for AI-driven cleaning and tagging
  - `pytest` for testing
  - `python-dotenv` for configuration management
- **AI Integration:** GPT-4O Mini (for cleaning) and GPT-3.5-turbo (for tagging)
- **CLI Tools:** Built-in `argparse` for command-line management

## Configuration & Deployment

- **Environment Variables:** Use a `.env` file (based on `.env.template`) to configure variables such as `RSS_FEED_URL`, `OPENAI_API_KEY`, etc.
- **Deployment:**  
  - Run via the CLI (e.g., `python -m src.main` or individual CLI commands).
  - Schedule using cron for regular updates.
- **Logging & Monitoring:** Detailed logging to stdout/stderr and optional file logging for production; error reporting and performance tracking are built in.