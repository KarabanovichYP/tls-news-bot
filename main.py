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
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    # новости в h2 (заголовок) и h3 (дата)
    news_headers = soup.find_all("h2")
    if not news_headers:
        return None

    # Берём первую (самую свежую) новость
    title = news_headers[0].get_text(strip=True)

    # Дата в следующем h3 после h2
    date_elem = news_headers[0].find_next_sibling("h3")
    date = date_elem.get_text(strip=True) if date_elem else "нет даты"

    # Ссылка на подробности — первый <a> после даты
    link_elem = date_elem.find_next("a") if date_elem else None
    link = "https://visas-it.tlscontact.com" + link_elem["href"] if link_elem else URL

    news = {
        "title": title,
        "date": date,
        "link": link
    }
    return news

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
