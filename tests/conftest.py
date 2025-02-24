"""Test configuration and fixtures."""
import os
import pytest
from pathlib import Path

# Set test environment BEFORE any imports
os.environ["APP_ENV"] = "test"

@pytest.fixture
def test_db():
    """Use the test database copy at tests/test_episodes.db.
    
    This uses the real database copy from production.
    """
    # Import config here after environment is set
    from src import config
    
    test_db_path = Path(__file__).parent / "test_episodes.db"
    if not test_db_path.exists():
        raise FileNotFoundError(f"Test database not found at {test_db_path}. Please copy production database first.")
    
    # Set environment variable for test database
    os.environ["TEST_DB_PATH"] = str(test_db_path)
    
    # Force config to reload DB_PATH
    config.DB_PATH = test_db_path
    
    yield test_db_path

@pytest.fixture(autouse=True)
def openai_test_config():
    """Configure OpenAI API for testing.
    
    This fixture:
    1. Validates API key is present
    2. Sets shorter timeouts for tests
    3. Uses cheaper model for testing
    4. Restores original config after tests
    """
    import openai
    from src import config
    
    # Store original values
    original_timeout = config.API_TIMEOUT
    original_model = config.OPENAI_MODEL
    
    # Set test values
    config.API_TIMEOUT = 10  # Shorter timeout for tests
    config.OPENAI_MODEL = "gpt-3.5-turbo"  # Cheaper model for tests
    
    # Verify API key is set
    api_key = config.get_openai_api_key()
    if not api_key:
        pytest.skip("OpenAI API key not configured")
    
    # Configure client
    openai.api_key = api_key
    
    yield
    
    # Restore original values
    config.API_TIMEOUT = original_timeout
    config.OPENAI_MODEL = original_model 