import feedparser
import requests
import hashlib
import os
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = "@FILCOMPUTERNEWS"

# LibreTranslate سرور عمومی (رایگان)
LT_URL = "https://libretranslate.de/translate"   # یا https://libretranslate.com اگر اولی کار نکرد

RSS_FEEDS = [
    "https://www.tomshardware.com/feeds/rss2/all.xml",
    "https://www.techpowerup.com/rss/news",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/rss/",
    "https://techcrunch.com/feed/",
    "https://www.anandtech.com/rss/",
]

def libre_translate(text):
    if not text or len(text.strip()) < 5:
        return text
    try:
        payload = {
            "q": text,
            "source": "en",
            "target": "fa",
            "format": "text"
        }
        response = requests.post(LT_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("translatedText", text)
        else:
            print("LibreTranslate Error:", response.text)
            return text
    except:
        return text

# ================== اجرا ==================
seen = set()
if os.path.exists("seen_posts.txt"):
    with open("seen_posts.txt") as f:
        seen = set(line.strip() for line in f)

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:   # حداکثر ۵ خبر از هر منبع
        post_id = hashlib.md5(entry.link.encode()).hexdigest()
        if post_id in seen:
            continue

        try:
            title_fa = libre_translate(entry.title)
            summary_en = entry.get('summary', entry.get('description', ''))[:600]
            summary_fa = libre_translate(summary_en)

            # پیدا کردن عکس
            image = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image = entry.media_content[0]['url']
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image = entry.enclosures[0].get('href')

            text = f"📰 **{title_fa}**\n\n{summary_fa}\n\n🔗 [ادامه مطلب]({entry.link})"

            if image:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                data = {'chat_id': CHANNEL_ID, 'caption': text, 'parse_mode': 'Markdown', 'photo': image}
            else:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                data = {'chat_id': CHANNEL_ID, 'text': text, 'parse_mode': 'Markdown'}

            requests.post(url, data=data)
            
            seen.add(post_id)
            with open("seen_posts.txt", "a") as f:
                f.write(post_id + "\n")
            
            time.sleep(4)
            
        except:
            continue

print("✅ اخبار با LibreTranslate ارسال شد!")
