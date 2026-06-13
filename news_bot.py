import feedparser
import requests
import hashlib
import os
import time
from deep_translator import GoogleTranslator

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = "@FILCOMPUTERNEWS"

RSS_FEEDS = [
    "https://www.tomshardware.com/feeds/rss2/all.xml",
    "https://www.techpowerup.com/rss/news",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/rss/",
    "https://techcrunch.com/feed/",
    "https://www.anandtech.com/rss/",
]

def smart_translate(text):
    if not text or len(text.strip()) < 10:
        return text
    try:
        translator = GoogleTranslator(source='en', target='fa')
        translated = translator.translate(text)
        
        # اصلاحات خیلی قوی برای اخبار سخت‌افزار و کامپیوتر
        corrections = {
            "پردازنده": "CPU",
            "کارت گرافیک": "GPU",
            "واحد پردازش گرافیکی": "GPU",
            "لپ تاپ": "لپ‌تاپ",
            "مادربرد": "مادربورد",
            "رم": "RAM",
            "حافظه دسترسی تصادفی": "RAM",
            "اس اس دی": "SSD",
            "هارد": "HDD",
            "هارد دیسک": "HDD",
            "ویندوز": "Windows",
            "لینوکس": "Linux",
            "اینتل": "Intel",
            "ای ام دی": "AMD",
            "انویدیا": "NVIDIA",
            "کیوای": "Qualcomm",
            "اسنپدراگون": "Snapdragon",
            "رایزن": "Ryzen",
            "کور": "Core",
            "آی": "i",
            "نسل": "Gen",
        }
        
        for wrong, correct in corrections.items():
            translated = translated.replace(wrong, correct)
        
        # اصلاحات جمله‌ای رایج
        translated = translated.replace(" .", ".").replace(" ،", "،").replace(" ؟", "؟")
        
        return translated.strip()
    except Exception as e:
        print("خطا در ترجمه:", e)
        return text

# ================== اجرا ==================
seen = set()
if os.path.exists("seen_posts.txt"):
    with open("seen_posts.txt") as f:
        seen = set(line.strip() for line in f)

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:
        post_id = hashlib.md5(entry.link.encode()).hexdigest()
        if post_id in seen:
            continue

        try:
            title_fa = smart_translate(entry.title)
            summary_en = entry.get('summary', entry.get('description', ''))[:550]
            summary_fa = smart_translate(summary_en)

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
            
            time.sleep(3)
            
        except:
            continue

print("✅ اخبار ارسال شد!")
