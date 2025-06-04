from flask import Flask, request, jsonify, send_file
import os
import requests
from bs4 import BeautifulSoup
import json
import random

app = Flask(__name__)

# Константы
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36"
}
COOKIES = {
    "session-id": "144-0614288-0360755",
    "session-id-time": "2082787201l",
    "session-token": "w9sRj1a/SzTxTD1iGPCh2sBTbHATYWUiawXbLlpgb1ebkqhCUZ3y/gvddpOChDOHHX/OXhhNErMQ213dAH4fo5Q0txOndXzfBAfGgO2gybLv3hGgnkROKS+D4US5NxFHNQUFxoQ/p9aJCEObTdGkSuvxbhkr3haAf+0nVCzEi7/kT91Me1JN4mhj5Vr5v2803FFi2/B+tf+5COnVpOkx4XASIEkdnSk0E7zEKnT6FRBUiMbhskK98Z9H/hJHX8htYyUq781Elf24KnHMbkx5gg1bx0kuZRha7rrTh0kNonKvKOzjIairyEffudtlc77i9Lh3w08bkaFQiYPY4w7v4lvfVHH6RQC6"
}

TITLE_DIR = 'title'
PROXY_FILE = 'proxy.txt'

# Убедимся, что папка существует
os.makedirs(TITLE_DIR, exist_ok=True)

def get_random_proxy():
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
            return random.choice(proxies) if proxies else None
    except Exception as e:
        print("Ошибка при чтении proxy.txt:", e)
        return None

@app.route('/')
def index():
    imdb_id = request.args.get('id')
    if not imdb_id:
        return jsonify({"error": "Не указан параметр id"}), 400

    file_path = os.path.join(TITLE_DIR, f'{imdb_id}.json')
    print(f"Обработка запроса для ID: {imdb_id}")
    print(f"Путь к файлу: {file_path}")

    # Файл уже есть
    if os.path.exists(file_path):
        print("Файл найден. Отправляем...")
        return send_file(file_path, mimetype='application/json')

    # Иначе парсим
    print("Файл не найден. Начинаем парсинг IMDb...")

    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    proxy = get_random_proxy()
    proxies = {"http": proxy, "https": proxy} if proxy else None

    print(f"Используемый прокси: {proxy}")

    try:
        response = requests.get(imdb_url, headers=HEADERS, cookies=COOKIES, proxies=proxies, timeout=15)
        print(f"Ответ IMDb: {response.status_code}")
        if response.status_code != 200:
            return jsonify({"error": "Не удалось получить страницу IMDb"}), 500
    except Exception as e:
        print("Ошибка при подключении к IMDb:", e)
        return jsonify({"error": "Ошибка соединения с IMDb"}), 500

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find("script", {"type": "application/ld+json"})
        if not script_tag:
            print("JSON-тег не найден.")
            return jsonify({"error": "Не найдены метаданные фильма"}), 500

        movie_data = json.loads(script_tag.string)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(movie_data, f, ensure_ascii=False, indent=2)

        print("Файл успешно сохранён.")
        return jsonify(movie_data)

    except Exception as e:
        print("Ошибка при парсинге страницы IMDb:", e)
        return jsonify({"error": "Ошибка обработки данных IMDb"}), 500

if __name__ == '__main__':
    app.run(host='http://www.imdbapi.work.gd/', port=80)

