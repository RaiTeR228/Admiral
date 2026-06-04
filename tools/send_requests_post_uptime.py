import os
import sys
from dotenv import load_dotenv
import requests
import time

if sys.platform == "win32":
    sys.exit(0)

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/uptime/"

def get_system_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        int_num = round(int(uptime_seconds) / 86400)
    return int_num

while True:
    data = get_system_uptime()
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={"Authorization": f"Api-Key {API_KEY}"},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"Успешно (статус: {response.status_code})")
        else:
            print(f"Статус: {response.status_code}, Ответ: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(10)