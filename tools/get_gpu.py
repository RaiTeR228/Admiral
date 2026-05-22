import time
import requests
import psutil
import platform
import GPUtil
from Status_system import *

API_URL = "http://127.0.0.1:8000/api/get-gpu/"
API_KEY = "d1045ccac017a6037c60d969434ab94044747c227c3c84938b6a3bc244a7da24"
NAME_SERVER = "тест"

def collect_stats():
    gpus = GPUtil.getGPUs()
    return {
        # "name": NAME_SERVER,
        "INSTALL_TOKEN": API_KEY,
        # "GPU": [
        #     {
        #         "id": gpu.id,
        #         "name": gpu.name,
        #         "load": gpu.load,
        #         "memoryUtil": gpu.memoryUtil,
        #         "temperature": gpu.temperature
        #     }
        #     for gpu in gpus
        # ]
    }

while True:
    data = collect_stats()
    print("Отправляем:", data)
    
    try:
        response = requests.get(
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