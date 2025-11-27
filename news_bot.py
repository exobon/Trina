import requests
import feedparser
import re
from urllib.parse import urlparse

BOT_TOKEN = "8133853195:AAGyPgvjCvTmwCnaZlJoMoKjF4QS4gmUen0"
CHANNEL_ID = "@goblincointg"   # apna channel username

SEEN_FILE = "seen_news.txt"

NEWS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

def clean_html(text):
    return re.sub('<.*?>', '', text or "")

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(x.strip() for x in f.readlines())
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for x in seen:
            f.write(x + "\n")

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption
    }
    return requests.post(url, data=payload, timeout=15)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    return requests.post(url, data=payload, timeout=15)

def get_source(link):
    try:
        return urlparse(link).netloc.replace("www.", "")
    except:
        return "source"

def make_hashtags(title):
    tags = ["#crypto", "#cryptonews", "#blockchain"]
    low = title.lower()

    if "bitcoin" in low or "btc" in low:
        tags += ["#bitcoin", "#btc"]
    if "ethereum" in low or "eth" in low:
        tags += ["#ethereum", "#eth"]
    if "solana" in low:
        tags.append("#solana")
    if "sec" in low:
        tags.append("#regulation")

    return " ".join(set(tags))

def extract_image(item):
    if "media_content" in item:
        return item.media_content[0].get("url")
    if "media_thumbnail" in item:
        return item.media_thumbnail[0].get("url")
    if "image" in item:
        return item.image.get("href")
    return None

def main():
    seen = load_seen()
    new_seen = set(seen)

    for feed in NEWS_FEEDS:
        entries = feedparser.parse(feed).entries

        for item in entries[:5]:
            uid = item.get("id") or item.get("link")
            if not uid or uid in seen:
                continue

            title = clean_html(item.get("title"))
            link = item.get("link", "")
            summary = clean_html(item.get("summary", ""))[:300] + "..."
            image = extract_image(item)
            source = get_source(link)
            hashtags = make_hashtags(title)

            msg = f"""
📰 Crypto News Update

🧾 {title}

📄 Summary:
{summary}

🔗 Read full article:
{link}

━━━━━━━━━━━━
🔔 Curated by: @goblincointg
📩 For promotions & features: @goblin_admin

{hashtags}
⚠️ Not Financial Advice | DYOR
""".strip()

            try:
                if image:
                    send_photo(image, msg)
                else:
                    send_message(msg)

                print("Posted:", title)
                new_seen.add(uid)

            except Exception as e:
                print("Post error:", e)

    save_seen(new_seen)

if __name__ == "__main__":
    main()
