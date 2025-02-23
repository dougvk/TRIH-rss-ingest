# RSS Feed Processor Development Plan

## Phase 1: Project Setup & Configuration ✓
- Create directory structure ✓
- Setup virtual environment ✓
- Create initial requirements.txt with core dependencies ✓
- Implement config.py for environment variable handling ✓
- Create .env template ✓
- Add data directory management ✓
- Add configuration validation ✓

## Phase 2: Feed Ingestion ✓
- Implement feed_ingest.py:
  - HTTP request functionality with timeouts ✓
  - Support for URL-based authentication ✓
  - XML parsing with lxml ✓
  - iTunes namespace support ✓
  - Error handling for network/parsing issues ✓
- Create Episode model with dataclass ✓
- Add unit tests with requests-mock ✓
- Verify with real feed (729 episodes) ✓

## Phase 3: Storage Layer ✓
- Implement storage.py:
  - SQLite connection management ✓
  - Schema creation with indexes ✓
  - CRUD operations for episodes ✓
  - Transaction handling ✓
  - Datetime handling with timezone support ✓
  - Duplicate handling via GUID ✓
- Add database migration capability ✓
- Performance optimization (~0.01s for 729 episodes) ✓

## Phase 4: Integration ✓
- Implement main.py orchestration ✓
- Connect feed ingestion to storage ✓
- Add proper error handling ✓
- Implement logging with timing metrics ✓
- Performance testing:
  - Feed fetch: ~1.0s ✓
  - XML parse: ~0.03s ✓
  - DB storage: ~0.01s ✓
  - Total: ~1.1s ✓

## Phase 5: Testing & Hardening ✓
- Integration tests ✓
- Mock feed creation (729 episodes) ✓
- Error scenario testing ✓
- Edge case handling ✓
- Performance verification ✓
- Test independence (no network dependency) ✓

## Phase 6: Documentation & Deployment ✓
- Complete README with:
  - Installation steps ✓
  - Configuration guide ✓
  - Usage examples ✓
  - Performance metrics ✓
  - Deployment tips ✓
- Add comprehensive docstrings ✓
- Document error scenarios ✓
- Add deployment instructions ✓
- Include maintenance guidelines ✓

## Phase 7: Episode Content Cleaning (In Progress)
- Schema Updates: ✓
  - Add column for cleaned description ✓
  - Add column for cleaning timestamp ✓
  - Add column for cleaning status ✓

- OpenAI Integration: ✓
  - Create cleaning.py module ✓
  - Implement prompt construction with regex patterns ✓
  - Add OpenAI API integration ✓
  - Build test harness for API calls ✓
  - Include episode title in prompt for better context ✓

- Random Sampling: ✓
  - Implement episode sampling function ✓
  - Add tracking for cleaned episodes ✓
  - Create revert capability for cleaned episodes ✓

- Quality Control: ✓
  - Add dry-run mode for preview ✓
  - Implement progress tracking ✓
  - Add detailed before/after logging ✓
  - Create manual verification interface ✓
  - Build pause/resume capability ✓

- Testing:
  - Add tests for prompt construction ✓
  - Mock OpenAI API responses ✓
  - Test sampling functions ✓
  - Verify database updates ✓

- Deployment:
  - Start with 10 episode sample ✓
  - Manual verification step ✓
  - Progressive increase in batch size (In Progress)
  - Full database cleaning (729 episodes) (Pending)

## Phase 8: Episode Tagging (Complete) ✓
- Schema Updates: ✓
  - Add tags column to episodes table ✓
  - Add tagging timestamp column ✓

- Tagging Module: ✓
  - Create tagging/ package structure ✓
  - Implement prompt management from markdown ✓
  - Add OpenAI integration with GPT-3.5-turbo ✓
  - Build batch processing logic ✓

- Random Sampling: ✓
  - Reuse existing random sampling function ✓
  - Add logging for episode type diversity ✓

- Quality Control: ✓
  - Add dry-run mode ✓
  - Implement progress tracking ✓
  - Add detailed before/after logging ✓
  - Build pause/resume capability ✓

- Testing: ✓
  - Add tests for prompt construction ✓
  - Mock OpenAI API responses ✓
  - Test tag format validation ✓
  - Verify database updates ✓

- Deployment: ✓
  - Start with 20 episode sample ✓
  - Manual verification step ✓
  - Progressive increase (50, 200, all) ✓
  - Full database tagging (729 episodes) ✓

## Phase 9: Tag Validation (Complete) ✓
- Validation Rules: ✓
  - RIHC episodes must have both "RIHC Series" and "Series Episodes" tags ✓
  - Non-RIHC series episodes must have episode numbers ✓
  - Series episode numbers must form complete sequences ✓
  - All tags must conform to taxonomy ✓

- Validation Tools: ✓
  - Create validate_tags.py script ✓
  - Add series name extraction ✓
  - Add sequence validation ✓
  - Add detailed error reporting ✓

- Testing: ✓
  - Verify all 729 episodes ✓
  - Check series number sequences ✓
  - Validate tag formats ✓
  - Test error reporting ✓

## Benefits of This Approach
- Reuse of existing random sampling code
- Progressive rollout with verification
- Comprehensive logging for review
- Flexible tagging framework
- Cost-efficient testing with mocks

## Technical Decisions

### Architecture ✓
- Modular design with clear separation of concerns ✓
- Dataclass for episode representation ✓
- Context managers for resource handling ✓
- Comprehensive logging ✓

### Database ✓
- SQLite for simplicity and performance ✓
- Efficient indexing strategy ✓
- Transaction-based operations ✓
- Automatic timestamp tracking ✓

### Testing ✓
- pytest for test framework ✓
- Mock feed for integration tests ✓
- Performance measurements ✓
- Error scenario coverage ✓

### Performance Optimizations ✓
- Batch database operations ✓
- Efficient XML parsing ✓
- Connection pooling ✓
- Index usage for queries ✓

### Content Cleaning
- Store both original and cleaned descriptions ✓
- Manual verification of cleaning results ✓
- Quality check step before committing changes ✓
- Gradual rollout with verification steps ✓
- Include episode title in prompt for better context ✓
- Use GPT-4O Mini model for efficient cleaning ✓

### Improvements Made
1. **Prompt Enhancement:**
   - Added episode title to context ✓
   - Improved preservation of historical content ✓
   - Better handling of episode-specific details ✓

2. **Cleaning Process:**
   - Added dry run capability ✓
   - Improved logging and result formatting ✓
   - Added cleanup of old result files ✓

3. **Quality Control:**
   - Added before/after comparison in results ✓
   - Implemented character count tracking ✓
   - Added modification status tracking ✓

## Benefits of This Approach
- Accurate content preservation ✓
- Efficient promotional content removal ✓
- Clear before/after comparisons ✓
- Reversible cleaning process ✓
- Title-aware content preservation ✓

## Detours and Improvements
1. **Feed Authentication:**
   - Switched from header-based to URL-based auth ✓
   - Simplified configuration needs ✓

2. **Link Field:**
   - Made optional with default empty string ✓
   - Adapted to feed structure ✓

3. **Testing Strategy:**
   - Added mock feed for integration tests ✓
   - Removed dependency on live feed ✓
   - Improved test speed (4.33s → 0.14s) ✓

4. **Performance Tracking:**
   - Added timing measurements ✓
   - Documented performance metrics ✓
   - Verified with real feed ✓

## Benefits of This Approach
- Independent component testing ✓
- No external dependencies in tests ✓
- Fast and reliable test suite ✓
- Clear performance metrics ✓
- Easy deployment ✓
- Maintainable codebase ✓
- Reversible content cleaning
- Quality-focused cleaning process 