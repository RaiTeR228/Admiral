import time
import requests
from tools.Status_system import *

API_URL = "http://127.0.0.1:8000/api/stats/"
API_KEY = "f03cbdecb1b228b5ab020adad9f3263efbc21c8a2ee0f0c8d381dcf5e360ca95"

def collect_stats():
    cpu = Cpu_Info()
    ram = Ram_Info()
    swap= Swap_Info()
    cpu_name = System_Info()
    return {
        "name": "server-1",
        # "server_id": '1',
        "install_token": "SUPER_SECRET_123",
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