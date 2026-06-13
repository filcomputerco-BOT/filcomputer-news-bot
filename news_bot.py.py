import feedparser
import requests
import time
import hashlib
from deep_translator import GoogleTranslator
import os

# تنظیمات
TELEGRAM_TOKEN = "توکن_بات_اینجا"          # ← اینجا توکن رو بذار
CHANNEL_ID = "@FILCOMPUTERNEWS"             # یا -100xxxxxxxxxx
SEEN_FILE = "seen_posts.txt"

# لیست RSSهای خوب سخت‌افزار و نرم‌افزار
RSS_FEEDS = [
    "https://www.tomshardware.com/feeds/rss2/all.xml",      # Tom's Hardware
    "https://www.techpowerup.com/rss/news",                 # TechPowerUp
    "https://www.theverge.com/rss/index.xml",               # The Verge
    "https://arstechnica.com/rss/",                         # Ars Technica
    "https://techcrunch.com/feed/",                         # TechCrunch
    # می‌تونی بعداً بیشتر اضافه کنی
]

translator = GoogleTranslator(source='en', target='fa')

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_seen(post_id):
    with open(SEEN_FILE, 'a') as f:
        f.write(post_id + '\n')

seen = load_seen()

def send_to_telegram(title, summary, link, image_url=None):
    text = f"📰 **{title}**\n\n{summary}\n\n🔗 [ادامه مطلب]({link})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data = {
        'chat_id': CHANNEL_ID,
        'caption': text,
        'parse_mode': 'Markdown'
    }
    if image_url:
        data['photo'] = image_url
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    try:
        requests.post(url, data=data)
        print("✅ پست ارسال شد:", title[:50])
    except Exception as e:
        print("خطا:", e)

for feed_url in RSS_FEEDS:
    print(f"در حال خواندن: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    for entry in feed.entries[:5]:  # فقط ۵ تا جدیدترین هر فید
        post_id = hashlib.md5(entry.link.encode()).hexdigest()
        if post_id in seen:
            continue
            
        try:
            title_en = entry.title
            summary_en = entry.get('summary', entry.get('description', ''))[:500]
            
            title_fa = translator.translate(title_en)
            summary_fa = translator.translate(summary_en) if summary_en else ""
            
            image = None
            if 'media_content' in entry:
                image = entry.media_content[0]['url']
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image = entry.enclosures[0].get('href')
            
            send_to_telegram(title_fa, summary_fa, entry.link, image)
            save_seen(post_id)
            time.sleep(2)  # جلوگیری از اسپم
            
        except Exception as e:
            print("خطا در ترجمه یا ارسال:", e)

print("✅ تمام اخبار امروز ارسال شد!")