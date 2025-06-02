from flask import Flask, request, render_template
import os, json, requests
from bs4 import BeautifulSoup
from config import COOKIES, HEADERS
from proxy_manager import get_next_proxy

app = Flask(__name__)

@app.route("/")
def index():
    imdb_id = request.args.get("id")
    if not imdb_id:
        return "❗ Укажите ?id=ttXXXXXX", 400

    filepath = f"title/{imdb_id}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        html, data = fetch_imdb_data(imdb_id)
        if not data:
            return "❌ Не удалось спарсить страницу", 500
        os.makedirs("title", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return render_template("index.html", data=data)

def fetch_imdb_data(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}/"
    for _ in range(5):  # 5 попыток с разными прокси
        try:
            proxy = get_next_proxy()
            r = requests.get(url, headers=HEADERS, cookies=COOKIES, proxies=proxy, timeout=10)
            if "captcha" in r.text.lower():
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            json_ld = soup.find("script", type="application/ld+json")
            if json_ld:
                return r.text, json.loads(json_ld.string)
        except Exception:
            continue
    return None, None

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
