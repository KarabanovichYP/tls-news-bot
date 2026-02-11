import requests
from bs4 import BeautifulSoup
import json
import os

# Telegram настройки из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# файл для хранения последней новости
LAST_NEWS_FILE = "last_news.json"

# URL страницы новостей TLScontact
URL = "https://visas-it.tlscontact.com/en-us/country/by/vac/byMSQ2it/news"

def get_last_news():
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_last_news(news):
    with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False)

def fetch_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    resp = requests.get(URL, headers=headers, timeout=30)

    # Проверим, не вернул ли сайт страницу блокировки
    if "You are unable to access" in resp.text:
        print("Сайт блокирует запрос (anti-bot).")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    news_headers = soup.find_all("h2")
    if not news_headers:
        print("Новости не найдены.")
        return None

    title = news_headers[0].get_text(strip=True)

    date_elem = news_headers[0].find_next_sibling("h3")
    date = date_elem.get_text(strip=True) if date_elem else "нет даты"

    link_elem = date_elem.find_next("a") if date_elem else None
    link = "https://visas-it.tlscontact.com" + link_elem["href"] if link_elem else URL

    return {
        "title": title,
        "date": date,
        "link": link
    }

def send_telegram(news):
    text = f"📢 <b>Новая новость на TLScontact</b>\n\n" \
           f"🗓 {news['date']}\n" \
           f"📌 {news['title']}\n" \
           f"🔗 {news['link']}"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    )

def main():
    latest_news = fetch_latest_news()
    if not latest_news:
        print("Не удалось получить новости.")
        return

    last_saved = get_last_news()
    if not last_saved or last_saved["title"] != latest_news["title"]:
        send_telegram(latest_news)
        save_last_news(latest_news)
        print("Отправлено новое сообщение.")
    else:
        print("Новостей нет.")

if __name__ == "__main__":
    main()
