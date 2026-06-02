import time
import requests
import sys
import psutil
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/temp/"

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