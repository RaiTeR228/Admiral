import time
import requests
import sys
import psutil
from dotenv import load_dotenv
import os

if sys.platform == "win32":
    pass

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/temp/"

def collect_stats():
    fans = psutil.sensors_fans()
    
    # Проверяем, есть ли данные о вентиляторах
    if not fans:
        return {
            "name": NAME_SERVER,
            "INSTALL_TOKEN": API_KEY,
            "current": None,
            "error": "No fan data available"
        }
    
    # Проходим по всем вентиляторам
    fan_data = []
    for fan_name, entries in fans.items():
        for entry in entries:
            fan_data.append({
                "fan_name": fan_name,
                "label": entry.label,
                "current_rpm": entry.current
            })
    
    # Возвращаем данные (можно выбрать первый вентилятор или все)
    if fan_data:
        return {
            "name": NAME_SERVER,
            "INSTALL_TOKEN": API_KEY,
            "current": fan_data[0]["current_rpm"],  # RPM первого вентилятора
            "all_fans": fan_data  # Все вентиляторы
        }
    else:
        return {
            "name": NAME_SERVER,
            "INSTALL_TOKEN": API_KEY,
            "current": None,
            "error": "No fan entries found"
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
    except Exception as e:
        print("Ошибка:", e)
    
    time.sleep(10)