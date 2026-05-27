import time
import requests
import sys
import psutil
[]
API_URL = "http://192.168.1.219:8000/api/temp/"
API_KEY = "82569fbbdbae3cc71725cbdd58943127e0a58ad47c2f7aad7c454f865a6b31c9"
NAME_SERVER = "zxc"

def collect_stats():

    return {
        "name": NAME_SERVER,
        "INSTALL_TOKEN": API_KEY,
        "current":3000,
    }

    # if sys.platform == "win32":
    #     sys.exit(1)

    # fan = psutil.sensors_fans()

    # if fan:
    #     for fans, entries in fan.items():
    #         for entry in entries:
    #             acpitz_data = fans['asus'][1]

    #             return {
    #                 "name": NAME_SERVER,
    #                 "INSTALL_TOKEN": API_KEY,
    #                 "current":3000
    #             }
    # else:
    #     return {
    #                 "name": NAME_SERVER,
    #                 "INSTALL_TOKEN": API_KEY,
    #                 "current":0
    #             }
        

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