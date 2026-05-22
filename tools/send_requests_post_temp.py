import time
import requests
import sys
import psutil

API_URL = "http://127.0.0.1:8000/api/post-temp/"
API_KEY = "82569fbbdbae3cc71725cbdd58943127e0a58ad47c2f7aad7c454f865a6b31c9"
NAME_SERVER = "тест"

def collect_stats():

        # return {
        #             "name": NAME_SERVER,
        #             "INSTALL_TOKEN": API_KEY,
        #             # "sensor_name": "Unknown Sensor",
        #             # "label": "",
        #             "temp": "25.0"  
        #         }

    if sys.platform == "win32":
        sys.exit(1)

    temps = psutil.sensors_temperatures()

    if temps:
        for sensor_name, entries in temps.items():
            for entry in entries:
                # print(f"{sensor_name} - {entry.label}: {entry.current}°C")
                return {
                    "name": NAME_SERVER,
                    "INSTALL_TOKEN": API_KEY,
                    # "sensor_name": sensor_name,
                    # "label": entry.label,
                    "temperature": entry.current
                }
    else:
        return {
                    "name": NAME_SERVER,
                    "INSTALL_TOKEN": API_KEY,
                    "temperature": "1"
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