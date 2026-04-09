import time
import requests
from tools.Status_system import get_cpu_cores_info, Status_Server, System_Info, Cpu_Info, Ram_Info, Swap_Info

# API_URL = "http://127.0.0.1:8000/api/stats/"
API_URL = "http://127.0.0.1:8000/api/server_info/" 
API_KEY = "f03cbdecb1b228b5ab020adad9f3263efbc21c8a2ee0f0c8d381dcf5e360ca95"
# API_KEY = "SUPER_SECRET_123"

def collect_stats():
    cores_info = get_cpu_cores_info()
    return {
        "name": "server-1",
        "install_token": "SUPER_SECRET_123",
        "ip": "999.999.999.999",  # Здесь можно динамически получать IP, если нужно
        "cpu": Status_Server()["cpu"],
        "MAX_RAM": Status_Server()["ram"],                    # поле ram в БД
        "MAX_CPU_CORES": str(cores_info["total_cores"]), # поле MAX_CPU_CORES в БД
        # "ram": Status_Server()["MAX_RAM"],
        # "IO": Status_Server()["IO"],
        # "Cpu_Info": Cpu_Info()["total_cores"],

    }

while True:
    data = collect_stats()
    print("Отправляем:", data)  # Посмотрите, что отправляется
    
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