"""Script to export all episode content to a file."""
from src.storage import get_episodes
import re

def clean_text(text: str) -> str:
    """Remove Twitter handles and producer credits section."""
    # Remove production credits, privacy notices, and contact info
    patterns = [
        r'\n*(?:Twitter:|A Goalhanger Films|Producer:|Executive Producer|Produced by|Exec Producer|Assistant|Editor:).*?$',
        r'\n*See acast\.com/privacy.*?$',
        r'\n*Email:.*?$',
        r'\n+_+\n*$',  # Remove underscores at the end
        r'\n*LIVE SHOWS.*?Tickets.*?$',  # Remove live show announcements
        r'\n*\*The Rest Is History LIVE.*?$',  # Remove show promos
        r'\n*\*The Rest Is History Live Tour \d{4}\*:.*?$',  # Remove tour announcements
        r'\n*Buy your tickets here:.*?$',  # Remove ticket links
        r'\n*Tickets on sale now at.*?$',  # Remove ticket sale announcements
        r'(?:^|\n)Tom and Dominic are (?:going on|back on) (?:a |an )?(?:U\.?S\.|international )?tour.*?$',  # Remove tour announcements
        r'\n*Tom and Dominic are back onstage.*?$',  # Remove show announcements
        r'\n*TRIH LIVE SHOW TICKETS.*?$',  # Remove ticket headers
        r'\n*We\'re giving you, our members,.*?tickets.*?$',  # Remove member ticket info
        r'(?s)\n*If you live in the States.*?Tickets on sale now.*?$',  # Remove US tour info
        r'book tickets now.*?$',  # Remove ticket booking instructions
        r'\n*Description: \*The Rest Is History Live Tour.*?$',  # Remove tour descriptions
        r'.*?live show on Wagner and Tchaikovsky at The Royal Albert Hall.*?$',  # Remove specific show references
        r'.*?Royal Albert Show on Mozart and Beethoven.*?$',  # Remove specific show references
        r'.*?their recent Athelstan party and live shows.*?$',  # Remove show references
        r'.*?last night\'s live show in audio form.*?$',  # Remove show references
        r'.*?live show recorded in Leicester Square.*?$',  # Remove show references
        r'.*?live show on cinema and history.*?$',  # Remove show references
        r'.*?our first overseas live show.*?$',  # Remove show references
        r'.*?pre-match nerves before a podcast, a live show.*?$',  # Remove show references
        r'.*?Catch up on last night\'s live show.*?$',  # Remove show references
        r'.*?our live show.*?$',  # Remove show references
        r'.*?their first overseas live show.*?$',  # Remove show references
        r'.*?our recent Dublin trip.*?$',  # Remove trip references
        r'.*?their U\.?S\. tour.*?$',  # Remove tour references
        r'.*?Tom\'s tour of Britain.*?$',  # Remove tour references
        r'.*?upcoming series.*?$',  # Remove upcoming content references
        r'.*?EXCLUSIVE NordVPN.*?$',  # Remove VPN ads
        r'\n*\*The Rest Is History Live Tour.*?$',  # Remove more tour announcements
        r'.*?robomagiclive\.com.*?$',  # Remove ticket site links
        r'.*?RESTISHISTORY22.*?$',  # Remove promo codes
        r'.*?link\.dice\.fm.*?$',  # Remove ticket links
        r'.*?Join The Rest Is History Club.*?$',  # Remove club promotions
        r'.*?www\.restishistorypod\.com.*?$',  # Remove website links
        r'.*?restishistorypod\.com.*?$',  # Remove website links
        r'.*?Please check your welcome email.*?Discord.*?$',  # Remove Discord references
        r'Description: Tom and Dominic are going on.*?$',  # Remove tour descriptions
        r'.*?live streamed shows.*?$',  # Remove streaming references
        r'.*?exclusive chatroom community.*?$',  # Remove community references
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.MULTILINE)
    # Remove any remaining Twitter handles
    text = re.sub(r'@\w+', '', text)
    # Clean up any extra newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove special characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def main():
    """Export all episode content to a file."""
    episodes = get_episodes()
    
    with open('episode_content.txt', 'w', encoding='utf-8') as f:
        for episode in episodes:
            f.write(f"Title: {clean_text(episode.title)}\n")
            f.write(f"Date: {episode.published_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Description: {clean_text(episode.description)}\n")
            f.write("-" * 80 + "\n")

if __name__ == "__main__":
    main() 