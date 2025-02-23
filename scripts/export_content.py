"""Script to export all episode content to a file."""
from src.storage import get_episodes

def main():
    """Export all episode content to a file."""
    episodes = get_episodes()
    
    with open('episode_content.txt', 'w', encoding='utf-8') as f:
        for episode in episodes:
            f.write(f"Title: {episode.title}\n")
            f.write(f"Date: {episode.published_date.strftime('%Y-%m-%d')}\n")
            # Use cleaned description if available, otherwise use original
            description = episode.cleaned_description if hasattr(episode, 'cleaned_description') and episode.cleaned_description else episode.description
            f.write(f"Description: {description}\n")
            f.write("-" * 80 + "\n")

if __name__ == "__main__":
    main() 