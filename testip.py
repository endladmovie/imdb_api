import json
import os
import time

# Пути к файлам
UNLIMITED_FILE = "unlimited.json"
LOG_FILE = "requests.log"
MAX_REQUESTS = 200

def is_unlimited(ip):
    """Проверяет, есть ли IP в unlimited.json"""
    if not os.path.exists(UNLIMITED_FILE):
        return False
    try:
        with open(UNLIMITED_FILE, 'r') as f:
            data = json.load(f)
            return ip in data
    except:
        return False

def log_request(ip):
    """Логирует IP и дату"""
    today = time.strftime("%Y-%m-%d")
    with open(LOG_FILE, "a") as f:
        f.write(f"{today} {ip}\n")

def get_request_count(ip):
    """Возвращает число запросов за сегодня по IP"""
    if not os.path.exists(LOG_FILE):
        return 0
    today = time.strftime("%Y-%m-%d")
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return sum(1 for line in lines if line.strip() == f"{today} {ip}")

def check_ip(ip):
    """Проверяет, можно ли пускать IP"""
    if is_unlimited(ip):
        return True
    count = get_request_count(ip)
    if count >= MAX_REQUESTS:
        return False
    log_request(ip)
    return True
