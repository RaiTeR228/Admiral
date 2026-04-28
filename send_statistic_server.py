import time
import requests
from tools.Status_system import *

API_URL = "http://127.0.0.1:8000/api/stats/"
API_KEY = "710ba2edd7b855975aa9da0c0e6e1d37f208d00f3a5c82713b44836e3827dbb7"

def collect_stats():
    cpu = Cpu_Info()
    ram = Ram_Info()
    swap= Swap_Info()
    cpu_name = System_Info()
    return {
        "name": "server-1",
        # "server_id": '1',
        "install_token": "710ba2edd7b855975aa9da0c0e6e1d37f208d00f3a5c82713b44836e3827dbb7",
        "ip": get_local_ip(),

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