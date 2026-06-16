import time
import requests
from Status_system import *
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/post-stats/"


def collect_stats():
    mem = psutil.virtual_memory()
    
    return {
        "Use_Ram": mem.percent,                    # float (например, 42.3)
        "Use_Cpu": psutil.cpu_percent(),           # float (например, 73.8) — убрал int()
        "Use_Swap": psutil.swap_memory().percent,  # float (например, 0.0)
        "Procent_Ram": mem.percent,                # float (например, 42.3)
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