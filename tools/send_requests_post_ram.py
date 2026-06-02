import time
import requests
import psutil
import platform
from Status_system import *
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/ram/"
def collect_stats():
    ram = Ram_Info()
    return {
        "INSTALL_TOKEN": API_KEY,
        "MAX_RAM": Ram_Info()["total"],
        # "PROCENT_RAM": psutil.virtual_memory().percent,
        # "RAM_CHARACTERISTICS": Ram_Info()["total"],
    }

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