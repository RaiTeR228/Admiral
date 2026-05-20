import time
import requests
from Status_system import *

API_URL = "http://127.0.0.1:8000/api/stats/"
API_KEY = "53076c29a60f29c76d7bd74cbe10a15c837bb3f7c7ba921d071c6cb5eeb96ce3"
NAME_SERVER = "тест"


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