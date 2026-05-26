import time
import requests
from Status_system import *

API_URL = "http://127.0.0.1:8000/api/post-stats/"
API_KEY = "31fae73538bd56225e08417f62d7c874c8c2c578f8afb24651dacb5b691cb442"
NAME_SERVER = "zxc"


def collect_stats():
    cpu = Cpu_Info()
    ram = Ram_Info()
    swap= Swap_Info()
    cpu_name = System_Info()
    return {
        "name": NAME_SERVER,
        "install_token": API_KEY,

        "Use_Ram": ram['used'],
        "Use_Cpu":cpu['total_cpu_usage'],
        "Use_Swap": swap['used']
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