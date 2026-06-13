import feedparser
import requests
import hashlib
import os
import time
from deep_translator import GoogleTranslator

# ================== تنظیمات ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")   # بعداً در GitHub Secrets می‌ذاریم
CHANNEL_ID = "@FILCOMPUTERNEWS"

RSS_FEEDS = [
    "https://www.tomshardware.com/feeds/rss2/all.xml",
    "https://www.techpowerup.com/rss/news",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/rss/",
    "https://techcrunch.com/feed/",
    "https://www.anandtech.com/rss/",
]

translator = GoogleTranslator(source='en', target='fa')
SEEN_FILE = "seen_posts.txt"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(line.strip() for line in f)
    return set()

seen = load_seen()

def send_to_telegram(title, summary, link, image=None):
    text = f"📰 **{title}**\n\n{summary}\n\n🔗 [ادامه مطلب]({link})"
    
    if image:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        data = {'chat_id': CHANNEL_ID, 'caption': text, 'parse_mode': 'Markdown', 'photo': image}
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': CHANNEL_ID, 'text': text, 'parse_mode': 'Markdown'}
    
    requests.post(url, data=data)

# ================== اجرا ==================
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:6]:   # حداکثر ۶ خبر از هر منبع
        post_id = hashlib.md5(entry.link.encode()).hexdigest()
        if post_id in seen:
            continue
            
        try:
            title_fa = translator.translate(entry.title)
            summary_en = entry.get('summary', entry.get('description', ''))[:400]
            summary_fa = translator.translate(summary_en) if summary_en else "خلاصه خبر در دسترس نیست."
            
            # پیدا کردن عکس
            image = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image = entry.media_content[0]['url']
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image = entry.enclosures[0].get('href')
            
            send_to_telegram(title_fa, summary_fa, entry.link, image)
            seen.add(post_id)
            with open(SEEN_FILE, 'a') as f:
                f.write(post_id + '\n')
            time.sleep(3)
            
        except:
            continue   # اگر یک خبر مشکل داشت، بقیه ادامه پیدا کنن

print("✅ اخبار با موفقیت ارسال شد!")
