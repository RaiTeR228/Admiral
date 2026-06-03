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
    #  return {
    #      "name": NAME_SERVER,
    #      "INSTALL_TOKEN": API_KEY,
    #      "sensor_name": "asus",
    #      "status_critical": None,
    #      "current_temp": 67,
    #  }

    temps = psutil.sensors_temperatures()

    if temps:
        for sensor_name, entries in temps.items():
            for entry in entries:
                if entry.critical is not None and entry.current >= entry.critical:
                    status_critical = 1
                else:
                    status_critical = 0
                
                return {
                    # "name": NAME_SERVER,
                    "INSTALL_TOKEN": API_KEY,
                    "sensor_name": sensor_name,
                    "status_critical": status_critical,
                    "current_temp": entry.current
                }
    else:
        print("TempSensor - Температурные датчики не обнаружены.")

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