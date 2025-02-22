"""Test script to fetch and parse the RSS feed."""
from src.feed_ingest import fetch_rss_feed, parse_rss_feed

def main():
    """Fetch, parse and display feed content."""
    try:
        print("Fetching feed...")
        content = fetch_rss_feed()
        print("Parsing feed...")
        episodes = parse_rss_feed(content)
        
        print(f"\nFound {len(episodes)} episodes!")
        print("\nFirst 5 episodes:")
        print("-" * 80)
        
        for episode in episodes[:5]:
            print(f"Title: {episode.title}")
            print(f"Published: {episode.published_date}")
            print(f"Duration: {episode.duration or 'Not specified'}")
            print(f"Audio URL: {episode.audio_url or 'Not available'}")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error processing feed: {e}")

if __name__ == "__main__":
    main() 