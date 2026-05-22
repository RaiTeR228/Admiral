import time
import requests
import psutil
import platform
from Status_system import *

API_URL = "http://127.0.0.1:8000/api/ram/"
API_KEY = "53076c29a60f29c76d7bd74cbe10a15c837bb3f7c7ba921d071c6cb5eeb96ce3"
NAME_SERVER = "тест"

def collect_stats():
    ram = Ram_Info()
    return {
        "name": NAME_SERVER,
        "INSTALL_TOKEN": API_KEY,
        "MAX_RAM": Ram_Info()["total"],
        "RAM_CHARACTERISTICS": Ram_Info()["total"],
    }

while True:
    data = collect_stats()
    print("Отправляем:", data)
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={"Authorization": f"Api-Key {API_KEY}"},
            timeout=5
        )
        print("Статус:", response.status_code)
        print("Ответ:", response.text)
        print("sent:", data)
    except Exception as e:
        print("error:", e)

    time.sleep(10)