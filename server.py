from flask import Flask, request, jsonify, send_file
import os
import requests
from bs4 import BeautifulSoup
import json
import random
import zipfile
from testip import check_ip

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36"
}
COOKIES = {
    "session-id": "144-0614288-0360755",
    "session-id-time": "2082787201l",
    "session-token": "w9sRj1a/SzTxTD1iGPCh2sBTbHATYWUiawXbLlpgb1ebkqhCUZ3y/gvddpOChDOHHX/OXhhNErMQ213dAH4fo5Q0txOndXzfBAfGgO2gybLv3hGgnkROKS+D4US5NxFHNQUFxoQ/p9aJCEObTdGkSuvxbhkr3haAf+0nVCzEi7/kT91Me1JN4mhj5Vr5v2803FFi2/B+tf+5COnVpOkx4XASIEkdnSk0E7zEKnT6FRBUiMbhskK98Z9H/hJHX8htYyUq781Elf24KnHMbkx5gg1bx0kuZRha7rrTh0kNonKvKOzjIairyEffudtlc77i9Lh3w08bkaFQiYPY4w7v4lvfVHH6RQC6"
}

PROXY_FILE = 'proxy.txt'
DATA_DIRS = {
    'movie': 'movie',
    'actor': 'actor',
    'company': 'company'
}

for path in DATA_DIRS.values():
    os.makedirs(path, exist_ok=True)

def get_random_proxy():
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
            return random.choice(proxies) if proxies else None
    except:
        return None

def parse_and_save(type_, imdb_id):
    if type_ not in DATA_DIRS:
        return False, "invalid_type"
    
    folder = DATA_DIRS[type_]
    url = f"https://www.imdb.com/{'title' if type_ == 'movie' else type_}/{imdb_id}/"
    proxy = get_random_proxy()
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        r = requests.get(url, headers=HEADERS, cookies=COOKIES, proxies=proxies, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return False, f"request_failed: {str(e)}"

    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        script_tag = soup.find("script", {"type": "application/ld+json"})
        if not script_tag:
            return False, "no_json_ld"

        data = json.loads(script_tag.string)
        zip_path = os.path.join(folder, f"{imdb_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{imdb_id}.json", json.dumps(data, ensure_ascii=False, indent=2))

        return True, "ok"
    except Exception as e:
        return False, f"parse_error: {str(e)}"

@app.before_request
def limit_by_ip():
    ip = request.remote_addr
    if not check_ip(ip):
        return jsonify({"error": "Rate limit exceeded"}), 429


@app.route('/upload')
def upload_route():
    type_ = request.args.get('type')
    imdb_id = request.args.get('id')
    if not type_ or not imdb_id:
        return jsonify({"error": "Missing type or id"}), 400

    ok, msg = parse_and_save(type_, imdb_id)
    if ok:
        return jsonify({"status": "success"})
        api_route()
    else:
        return jsonify({"error": msg}), 500

@app.route('/api')
def api_route():
    type_ = request.args.get('type')
    imdb_id = request.args.get('id')
    if not type_ or not imdb_id:
        return jsonify({"error": "Missing type or id"}), 400

    folder = DATA_DIRS.get(type_)
    if not folder:
        return jsonify({"error": "Invalid type"}), 400

    zip_path = os.path.join(folder, f"{imdb_id}.zip")

    # Если файл есть — отдаем
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open(f"{imdb_id}.json") as f:
                return jsonify(json.load(f))

    # Иначе — парсим тихо через /upload
    try:
        u = f"http://127.0.0.1:80/upload?type={type_}&id={imdb_id}"
        r = requests.get(u, timeout=10)
        if r.status_code == 200:
            return api_route()  # рекурсивно пробуем снова
        else:
            upload_route()
            return jsonify({"error": "Failed to parse data via /upload"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal request failed: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
