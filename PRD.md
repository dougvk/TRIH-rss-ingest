# Podcast Feed Processor - Complete PRD

## Overview

The Podcast Feed Processor is a comprehensive application designed to:
1. Ingest a private podcast RSS feed
2. Parse and store episode details
3. Clean episode descriptions by removing promotional content
4. Tag episodes with themes and tracks for content organization
5. Validate tag consistency and series numbering

The application focuses on performance, reliability, and maintainability, successfully handling feeds with hundreds of episodes.

## Core Features

### 1. Feed Processing
- **Data Ingestion:** Securely fetch private RSS feed with HTTP authentication
- **Data Parsing:** Extract episode metadata using `lxml`
- **Data Storage:** Persist data in SQLite with efficient indexing
- **Performance:** Process 729 episodes in ~1.1 seconds total

### 2. Content Cleaning
- **AI-Powered Cleaning:** Use GPT-4O Mini to remove promotional content
- **Content Preservation:** Maintain historical and episode-specific content
- **Quality Control:** Track changes and allow manual verification
- **Progressive Rollout:** Scale from small samples to full database

### 3. Episode Tagging
- **AI Tag Generation:** Use GPT-3.5-turbo with custom taxonomy
- **Structured Tags:** Format, Theme, and Track categorization
- **Series Management:** Handle episode numbering and series identification
- **Tag Validation:** Ensure consistency and completeness

## Database Schema

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
    cleaned_description TEXT,
    cleaning_timestamp TIMESTAMP,
    cleaning_status TEXT DEFAULT "pending",
    tags TEXT,
    tagging_timestamp TIMESTAMP,
    episode_number INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodes_guid ON episodes(guid);
CREATE INDEX idx_episodes_published_date ON episodes(published_date);
CREATE INDEX idx_episodes_cleaning_status ON episodes(cleaning_status);
CREATE INDEX idx_episodes_tags ON episodes(tags);
CREATE INDEX idx_episodes_episode_number ON episodes(episode_number);
```

## Tag Taxonomy

### Format Tags
- Series Episodes
- Standalone Episodes
- RIHC Series

### Theme Tags
- Ancient & Classical Civilizations
- Medieval & Renaissance Europe
- Empire, Colonialism & Exploration
- Modern Political History & Leadership
- Military History & Battles
- Cultural, Social & Intellectual History
- Science, Technology & Economic History
- Religious, Ideological & Philosophical History
- Historical Mysteries, Conspiracies & Scandals
- Regional & National Histories

### Track Tags
- Roman Track
- Medieval & Renaissance Track
- Colonialism & Exploration Track
- American History Track
- Military & Battles Track
- Modern Political History Track
- Cultural & Social History Track
- Science, Technology & Economic History Track
- Religious & Ideological History Track
- Historical Mysteries & Conspiracies Track
- British History Track
- Global Empires Track
- World Wars Track
- Ancient Civilizations Track
- Regional Spotlight: Latin America Track
- Regional Spotlight: Asia & the Middle East Track
- Regional Spotlight: Europe Track
- Regional Spotlight: Africa Track
- Historical Figures Track
- The RIHC Bonus Track
- Archive Editions Track
- Contemporary Issues Through History Track

## Tagging Rules

1. **Format Rules:**
   - Episodes must have exactly one Format tag
   - RIHC episodes must have both "RIHC Series" and "Series Episodes" tags
   - Episodes with part/episode numbers must be "Series Episodes"

2. **Series Rules:**
   - Non-RIHC series episodes must have an episode number
   - Episode numbers must form complete sequences without gaps
   - Episode numbers start from the lowest number in the series

3. **Theme & Track Rules:**
   - Episodes must have at least one Theme tag
   - Episodes must have at least one Track tag
   - All tags must match the taxonomy exactly

## Performance Metrics

### Feed Processing
- Feed Fetch: ~1.0 seconds
- XML Parse: ~0.03 seconds
- DB Storage: ~0.01 seconds
- Total Time: ~1.1 seconds

### Content Cleaning
- Average reduction in description length: ~30-40%
- Preservation of historical content: ~100%
- Removal of promotional content: ~100%

### Episode Tagging
- 729 episodes successfully tagged
- All series properly numbered
- No tag validation errors

## Technology Stack

- **Language:** Python 3.13
- **Core Libraries:**
  - `requests` for HTTP
  - `lxml` for XML parsing
  - `sqlite3` for database
  - `openai` for AI integration
  - `pytest` for testing
- **AI Models:**
  - GPT-4O Mini for content cleaning
  - GPT-3.5-turbo for episode tagging

## Deployment

### Requirements
- Python 3.13+
- Virtual environment
- `.env` file with:
  - Feed URL
  - OpenAI API key
  - Database path
- Write access for database

### Monitoring
- Logging to stdout/stderr
- Performance metrics logging
- Error tracking
- Content change tracking
- Tag validation reporting

### Maintenance
- Database backups
- Log rotation
- VACUUM optimization
- Regular tag validation checks
- Series sequence verification