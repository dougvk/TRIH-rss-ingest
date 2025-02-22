"""Test script to fetch the RSS feed."""
from src.feed_ingest import fetch_rss_feed

def main():
    """Fetch and display feed content."""
    try:
        content = fetch_rss_feed()
        print("Successfully fetched feed!")
        print("\nFirst 500 characters of content:")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        print(f"\nTotal content length: {len(content)} characters")
    except Exception as e:
        print(f"Error fetching feed: {e}")

if __name__ == "__main__":
    main() 