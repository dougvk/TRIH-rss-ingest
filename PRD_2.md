# Podcast Feed Processor – Episode Cleaning PRD

## Overview

The goal of this project phase is to extend the existing RSS Feed Processor so that it cleans each episode's description by removing promotional content (e.g., tour ads, live show promotions, ticket sales). This will be achieved by integrating an OpenAI API call that leverages provided regular expressions as context. Initially, the cleaning process will be applied to a small random sample of episodes for manual verification. Once verified, the process will scale up to clean the entire database.

## Objectives

- **Clean Episode Descriptions:** Remove promotional content from each episode's description while preserving the show's topic.
- **Leverage AI for Text Cleaning:** Use GPT-4O Mini model for efficient cleaning, with a prompt that includes episode title and regex patterns.
- **Random Sampling for Verification:** Process a small, random sample of episodes (initially 10) for manual review, with the option to progressively increase the sample size.
- **Test API Call Structure:** Implement a test suite that verifies that API calls to OpenAI are correctly constructed without incurring actual API costs.
- **Progressive Rollout:** Provide a mechanism to gradually increase the number of episodes processed until the entire database (729 episodes) is cleaned.

## Implementation Details

### Actual Changes from Original Plan

1. **Model Selection:**
   - Originally planned: GPT-3.5-turbo
   - Implemented: GPT-4O Mini for better efficiency and content preservation

2. **Prompt Enhancement:**
   - Added: Episode title included in prompt for better context
   - Added: Specific instruction to preserve content related to episode title
   - Result: More accurate content preservation and better handling of episode-specific details

3. **Quality Control:**
   - Added: Character count tracking for before/after comparison
   - Added: Modification status tracking
   - Added: Cleanup of old result files
   - Added: Text wrapping at 120 characters for better readability

4. **Database Schema:**
   - Added: cleaning_status column with states (pending, cleaned, no_changes_needed)
   - Added: cleaning_timestamp for tracking when episodes were processed

5. **Results Format:**
   - Added: Detailed before/after comparisons
   - Added: Length statistics
   - Added: Timestamp tracking
   - Added: Modification status

### Successful Outcomes

1. **Content Preservation:**
   - Historical content accurately preserved
   - Episode-specific details maintained
   - Better context maintenance between paragraphs

2. **Promotional Content Removal:**
   - All social media links removed
   - Production credits cleaned
   - Tour dates and ticket information removed
   - Website links and promotional content eliminated

3. **Quality Metrics:**
   - Average reduction in description length: ~30-40%
   - Preservation of historical content: ~100%
   - Removal of promotional content: ~100%

## Next Steps

1. **Progressive Rollout:**
   - Continue with larger batch sizes (25, 50, 100)
   - Monitor cleaning quality across larger samples
   - Prepare for full database cleaning

2. **Potential Improvements:**
   - Add automated quality metrics
   - Implement batch processing for efficiency
   - Add rollback capability for batch operations

3. **Documentation:**
   - Update technical documentation
   - Add usage examples
   - Document cleaning patterns and results

## User Stories

- **As a developer,** I want a function that accepts an episode title and description, calls OpenAI with the correct prompt (including regex examples), and returns a cleaned description.
- **As a developer,** I want to randomly sample a subset of episodes from the database so that my tests and manual verification are not biased by a fixed ordering.
- **As a developer,** I want a test suite that verifies the OpenAI API call's structure without making actual API calls.
- **As a user,** I want to progressively clean more episodes after verifying that the initial sample's cleaning results are satisfactory.
- **As a user,** I want the database to be updated with the cleaned descriptions once I'm confident in the cleaning process.

## Requirements

### Functional Requirements

1. **Cleaning Functionality:**
   - Create a function (`clean_description`) that:
     - Constructs a prompt incorporating:
       - The episode title and original description.
       - A list of regex patterns that represent promotional content.
     - Calls the OpenAI API (using the `gpt-3.5-turbo` model) with proper parameters.
     - Returns the cleaned description.

2. **Random Sampling:**
   - Develop a helper function (`get_random_episodes`) that randomly selects a sample of episodes from the database.
   - Initially set the sample size to 10 episodes, with configuration to increase this number.

3. **Database Update:**
   - Update the relevant episode records in the SQLite database with the cleaned description.
   - Ensure proper logging and error handling.

4. **Test Suite:**
   - Write unit tests that verify:
     - The cleaning function constructs the OpenAI API call correctly (using monkeypatching or a fake response).
     - The prompt includes the regex examples.
   - Avoid actual API calls during testing to prevent incurring cost.

### Non-Functional Requirements

- **Scalability:**  
  - The solution should be easily adjustable to scale from a 10-episode sample to the full set of 729 episodes.
- **Cost Efficiency:**  
  - Tests must avoid making live API calls.
- **Maintainability:**  
  - Code should be modular, with separate modules for cleaning, random sampling, and database operations.
- **Logging & Monitoring:**  
  - Log each cleaning operation for debugging and manual review.
- **User Control:**  
  - Allow the user to run cleaning on a sample, manually inspect the output, then progressively increase the sample size.

## Architecture & Design

### Folder Structure (Updated)

podcast_feed_processor/
├── README.md
├── requirements.txt
├── .env
├── data/
│   └── episodes.db
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── feed_ingest.py      # RSS feed fetching and parsing
│   ├── models.py           # Data models (e.g., Episode dataclass)
│   ├── storage.py          # SQLite database operations
│   ├── cleaning.py         # New module for cleaning episode descriptions using OpenAI
│   ├── helpers.py          # Contains helper functions (e.g., random sampling)
│   └── run_cleaning.py     # Script to run the cleaning process on a random sample of episodes
└── tests/
    ├── __init__.py
    ├── test_cleaning.py    # Tests for the cleaning function and API call construction
    └── ...                 # Other test files as needed

### Key Modules

- **src/cleaning.py:**  
  - Implements `clean_description()` which builds the prompt (including regex examples) and calls the OpenAI API.
  
- **src/helpers.py:**  
  - Implements `get_random_episodes()` to select a random subset of episodes.
  
- **src/run_cleaning.py:**  
  - Orchestrates the cleaning process by:
    - Retrieving all episodes.
    - Randomly selecting a sample (initially 10).
    - Calling `clean_description()` on each.
    - Updating the database with the cleaned descriptions.
  
- **tests/test_cleaning.py:**  
  - Verifies that `clean_description()` makes the correct API call (using a fake response) and that the prompt is properly constructed.

## Implementation Phases

### Phase 1: Develop the Cleaning Function
- **Task 1.1:** Create or update `src/cleaning.py` to implement `clean_description()` that:
  - Incorporates your regex patterns (loaded from `src/cleaning_helpers.py`).
  - Constructs the prompt properly.
  - Calls the OpenAI API with model `gpt-3.5-turbo` and returns the cleaned text.
- **Task 1.2:** Manually test the function with known inputs.

### Phase 2: Add Random Sampling
- **Task 2.1:** Implement `get_random_episodes()` in `src/helpers.py` to randomly sample a specified number of episodes.
- **Task 2.2:** Update `src/run_cleaning.py` to process a random sample (default 10 episodes) from the database.

### Phase 3: Database Update Integration
- **Task 3.1:** Modify the cleaning process to update each episode record in the SQLite database with the cleaned description.
- **Task 3.2:** Add logging for each update to support manual review.

### Phase 4: Test Suite Development
- **Task 4.1:** Write tests in `tests/test_cleaning.py` that:
  - Verify the API call is constructed with the correct model and parameters (using monkeypatch/fake response).
  - Ensure the prompt includes your regex examples.
- **Task 4.2:** Run the test suite to validate that the cleaning function meets the expected behavior.

### Phase 5: Manual Verification and Progressive Rollout
- **Task 5.1:** Run the `run_cleaning.py` script to process 10 randomly selected episodes.
- **Task 5.2:** Manually inspect the cleaned descriptions in the database.
- **Task 5.3:** Increase the sample size progressively (e.g., 25, 50, etc.) until confident.
- **Task 5.4:** Finally, run the cleaning process across the full database (729 episodes).

## Deliverables

- **Code Updates:**  
  - Updated `cleaning.py`, `helpers.py`, and `run_cleaning.py`.
- **Test Suite:**  
  - `tests/test_cleaning.py` covering API call construction and prompt correctness.
- **Documentation:**  
  - Updated README and inline comments documenting the new cleaning functionality and usage instructions.
- **Cleaned Database:**  
  - A fully cleaned `episodes.db` after full rollout.

## Timeline

- **Week 1:**  
  - Complete Phase 1 and Phase 2 (cleaning function and random sampling).
- **Week 2:**  
  - Integrate database updates (Phase 3) and develop the test suite (Phase 4).
- **Week 3:**  
  - Manual verification, progressive rollout, and final deployment (Phase 5).

## Final Notes

- **Iterative Development:**  
  Start with a small sample to validate that the cleaning function works as expected. Adjust prompts and regex examples as needed.
- **Cost Management:**  
  Use mocking for tests to avoid live API calls. Perform manual verification only on small random samples until satisfied.
- **Extensibility:**  
  The architecture should allow further refinements (e.g., additional cleaning logic, more sophisticated logging, integration with a UI).