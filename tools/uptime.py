import sys
import os
import requests
from dotenv import load_dotenv
load_dotenv()

if sys.platform == "win32":
    pass

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/uptime/"


def get_system_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        int_num = round(int(uptime_seconds) / 86400)
    return int_num
try:
    response = requests.post(
        API_URL,
        json = {"uptime": get_system_uptime()},
        headers = {"Authorization": f"Api-Key {os.getenv('API_TOKEN')}"},
        timeout=5
    )
except Exception as e:
    print("Ошибка при отправке данных:", e)