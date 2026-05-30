import time
import requests
from Status_system import *
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = "http://127.0.0.1:8000/api/post-stats/"
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")


def collect_stats():
    cpu = Cpu_Info()
    ram = Ram_Info()
    swap= Swap_Info()
    return {
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

    time.sleep(5)