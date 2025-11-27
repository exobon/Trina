import requests
import feedparser
import re
from urllib.parse import urlparse

# ================== CONFIG ==================
BOT_TOKEN = "8563113452:AAEwcNSBRnEFNbrD1pgoYPjAtY9-r_AXcnU"
CHANNEL_ID = "@TokenTimes"  # apne channel ka @username

SEEN_FILE = "seen_news.txt"

NEWS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]
# ============================================


def clean_html(text: str) -> str:
    """HTML tags + common entities clean karta hai."""
    if not text:
        return ""
    text = re.sub("<.*?>", "", text)
    text = text.replace("&#038;", "&").replace("&amp;", "&")
    return text.strip()


def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(x.strip() for x in f.readlines())
    except Exception:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for x in seen:
            f.write(x + "\n")


def send_photo(photo_url: str, caption: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption,
    }
    return requests.post(url, data=payload, timeout=15)


def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
    }
    return requests.post(url, data=payload, timeout=15)


def get_source(link: str) -> str:
    try:
        return urlparse(link).netloc.replace("www.", "")
    except Exception:
        return "source"


def make_summary(raw_text: str, max_words: int = 100) -> str:
    """Approx 100-word summary generate karega."""
    text = clean_html(raw_text)
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def make_hashtags(title: str) -> str:
    """Rotating hashtag sets + topic based tags."""
    rotations = [
        ["#crypto", "#cryptonews", "#blockchain"],
        ["#crypto", "#defi", "#web3"],
        ["#bitcoin", "#btc", "#crypto"],
        ["#altcoins", "#trading", "#cryptomarket"],
        ["#ethereum", "#eth", "#crypto"],
        ["#solana", "#altcoins", "#cryptonews"],
    ]

    idx = abs(hash(title)) % len(rotations)
    tags = set(rotations[idx])

    low = title.lower()
    if "bitcoin" in low or "btc" in low:
        tags.update(["#bitcoin", "#btc"])
    if "ethereum" in low or "eth" in low:
        tags.update(["#ethereum", "#eth"])
    if "solana" in low:
        tags.add("#solana")
    if "tether" in low or "usdt" in low:
        tags.add("#usdt")
    if "stablecoin" in low:
        tags.add("#stablecoins")

    return " ".join(sorted(tags))


def extract_image(item):
    """RSS item se image URL nikalne ki koshish."""
    try:
        if "media_content" in item:
            return item.media_content[0].get("url")
        if "media_thumbnail" in item:
            return item.media_thumbnail[0].get("url")
        if "image" in item and hasattr(item.image, "get"):
            return item.image.get("href")
    except Exception:
        pass
    return None


def main():
    seen = load_seen()
    new_seen = set(seen)

    for feed in NEWS_FEEDS:
        entries = feedparser.parse(feed).entries

        # har feed se latest 5 news hi check karenge
        for item in entries[:5]:
            uid = item.get("id") or item.get("link")
            if not uid or uid in seen:
                continue

            title = clean_html(item.get("title"))
            link = item.get("link", "")
            raw_summary = item.get("summary", "") or item.get("description", "")
            summary = make_summary(raw_summary, max_words=100)
            image = extract_image(item)
            hashtags = make_hashtags(title)

            msg = f"""
📰 TokenTimes – Daily Crypto Market News 24/7 🟢 Crypto News

News : 🧾 {title}

📄 Summary:
{summary}

🔗 Read full article:
{link}

{hashtags}
━━━━━━━━━━━━
👤 Created by: @TokenTimes247
🛠 Support Team: @TokenTimesbot
━━━━━━━━━━━━
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
    main()        "caption": caption
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
