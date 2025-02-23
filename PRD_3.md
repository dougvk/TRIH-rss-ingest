# Podcast Feed Processor – Episode Tagging and Thematic Categorization PRD

## Overview

The objective of this phase is to extend the existing RSS Feed Processor by adding AI-driven tagging functionality for each episode. The solution will prompt an OpenAI model with a custom tagging prompt (stored in a markdown file) that guides the model to generate thematic tags based on each episode’s title and description. This will allow you to tag episodes and group them into curated thematic tracks for a website, enabling users to explore content by themes such as various periods of Roman history, American history, or cross-cutting historical topics.

## Objectives

- **AI Tag Generation:** Integrate an AI tagging module that uses your custom tagging prompt to generate a comma-separated list of thematic tags for each episode.
- **Database Update:** Modify the existing database schema to include a new field for tags, and update episode records with the generated tags.
- **Random Sampling for Verification:** Implement a mechanism to randomly select a subset of episodes (starting with 10) for manual review before processing the full dataset.
- **API Call Verification:** Ensure that the API calls to OpenAI are correctly constructed (using the desired model and parameters) through a dedicated test suite that uses mocks.
- **Progressive Rollout:** Allow for incremental scaling—begin with a small sample, verify the output, and then progressively process more episodes until the entire database (729 episodes) is updated.

## Functional Requirements

1. **Tag Generation:**
   - Develop a function that accepts an episode’s title and description.
   - Load the custom tagging prompt (approximately 400–1000 tokens) from a markdown file.
   - Combine the custom prompt with the episode details to instruct the AI to generate tags.
   - Use a lightweight model (e.g., GPT-3.5-turbo) to generate a comma-separated list of tags.
   
2. **Database Integration:**
   - Update the SQLite database schema to add a new column for storing generated tags.
   - Implement functionality to update each episode record with the generated tags, ensuring proper error handling and logging.

3. **Random Sampling:**
   - Create a helper function to randomly select a specified number of episodes from the database.
   - Initially process a small random sample (e.g., 10 episodes) to allow for manual verification of tag quality.
   - Allow configuration to progressively increase the sample size until full rollout.

4. **Testing API Call Structure:**
   - Develop unit tests to verify that the tagging function constructs the API call correctly (using the proper model and prompt).
   - Use mocking techniques in tests to simulate API responses and avoid incurring API costs during testing.

## Non-Functional Requirements

- **Scalability:** The solution must be easily scalable from processing a small sample to handling the full set of 729 episodes.
- **Cost Efficiency:** Tests should avoid live API calls by using mocks, ensuring that API usage is minimized during development.
- **Maintainability:** The code should be modular, with clear separation between the tagging logic, database operations, and random sampling.
- **Logging and Monitoring:** Implement logging for each tagging operation to facilitate manual review and debugging.
- **User Control:** Provide the ability to run the tagging process on a limited random sample for manual review before scaling up to the entire dataset.

## Architecture & Design

- **Database Schema:**  
  - Extend the existing schema by adding a new column (e.g., `tags`) in the episodes table to store the AI-generated tags.

- **Tagging Module:**  
  - Create a dedicated module for handling AI tagging, which loads the custom tagging prompt, combines it with episode details, and makes the API call to generate tags.

- **Random Sampling:**  
  - Develop helper functions to randomly select episodes from the database, ensuring that each run can process a different subset for verification.

- **Processing Script:**  
  - Build a script to retrieve episodes from the database, apply the tagging function to a random sample, and update the database with the generated tags.

- **Test Suite:**  
  - Implement tests that verify the construction of API calls and prompt integration, ensuring that the correct model and parameters are used. Tests should use mocks to simulate responses.

## Implementation Phases

### Phase 1: Develop the Tagging Module
- Create functionality to load the custom tagging prompt from a markdown file.
- Develop a function that accepts an episode’s title and description, combines these with the prompt, and calls the OpenAI API to generate tags.
- Ensure the function returns a well-formatted, comma-separated list of tags.

### Phase 2: Update the Database Schema and Integration
- Modify the database schema to add a `tags` column.
- Implement functionality to update each episode record with the generated tags.
- Add logging and error handling for database updates.

### Phase 3: Implement Random Sampling and Processing Script
- Develop a helper function to randomly select a specified number of episodes.
- Create a processing script that retrieves a random sample of episodes (initially 10), applies the tagging function, and updates the database.
- Allow configuration to increase the sample size progressively.

### Phase 4: Develop the Test Suite
- Write unit tests to verify that the tagging function constructs API calls correctly and uses the custom prompt.
- Use mocking to simulate API responses and ensure tests run cost-efficiently.
- Validate that the generated prompt includes the required regex examples.

### Phase 5: Manual Verification and Progressive Rollout
- Run the processing script on a small random sample (e.g., 10 episodes) and manually inspect the generated tags.
- Based on manual review, incrementally increase the sample size (e.g., 25, 50, etc.) until confident.
- Finally, process the entire dataset (729 episodes) to update all records.

## Deliverables

- Updated database schema with a new `tags` column.
- A tagging module that uses a custom markdown prompt to generate thematic tags via the OpenAI API.
- A random sampling mechanism and processing script to apply the tagging function to a configurable sample size.
- A test suite that verifies proper API call construction and prompt composition using mocks.
- A fully updated database with AI-generated tags for all episodes, ready for integration into a website with curated thematic tracks.

## Timeline

- **Week 1:** Develop the tagging module and update the database schema.
- **Week 2:** Implement random sampling and create the processing script.
- **Week 3:** Develop and run the test suite to verify API call construction.
- **Week 4:** Conduct manual verification on a small sample and progressively scale up to process the entire database.

## Final Notes

- **Iterative Testing:** Begin by processing a small random sample of episodes. Manually review the generated tags and adjust the custom prompt if necessary.
- **Cost Management:** Use mocking in the test suite to avoid live API calls, and process small batches for manual verification.
- **Extensibility:** The architecture should allow for future enhancements, such as refining the tagging prompt or integrating additional thematic tracks based on new requirements.