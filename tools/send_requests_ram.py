import time
import requests
import psutil
import platform
from tools.Status_system import *

API_URL = "http://127.0.0.1:8000/api/ram/"
API_KEY = "7c2d24de67d2dfb3bb8f2984ce15e374400025f659c133a66c70565eade366fe"


def collect_stats():
    ram = Ram_Info()
    return {
        "name": "тест",
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