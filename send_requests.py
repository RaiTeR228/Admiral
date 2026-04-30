import time
import requests
import psutil
import platform
from cpuinfo import get_cpu_info  # Добавьте эту библиотеку
from tools.Status_system import *

# API_URL = "http://127.0.0.1:8000/api/stats/"
API_URL = "http://127.0.0.1:8000/api/server_info/" 
API_KEY = "710ba2edd7b855975aa9da0c0e6e1d37f208d00f3a5c82713b44836e3827dbb7"
# API_KEY = "SUPER_SECRET_123"



def get_cpu_name():
    """Получение названия процессора"""
    try:
        # Способ 1: через cpuinfo библиотеку
        cpu_info = get_cpu_info()
        brand_raw = cpu_info.get('brand_raw', '')
        if brand_raw:
            return brand_raw
    except:
        pass
    
    try:
        # Способ 2: через platform модуль
        processor = platform.processor()
        if processor:
            return processor
    except:
        pass
    
    try:
        # Способ 3: через psutil (не всегда работает)
        # Некоторые системы хранят инфу о процессоре здесь
        return "Unknown CPU"
    except:
        return "Unknown CPU"

def collect_stats():
    cpu = Cpu_Info()
    
    return {
        "name": "тест",
        "INSTALL_TOKEN": API_KEY,
        # "ip": get_local_ip(),

        # "cpu": Status_Server()["cpu"],
        "MAX_CPU_CORES": str(cpu["physical_cores"]),
        "MAX_CPU_THREADS":  str(cpu["total_cores"]), 
        "CPU_NAME": get_cpu_name(),  # Используем новую функцию
        "Local_Name_PC": platform.node(),  # Имя компьютера

        "MAX_RAM": Ram_Info()["total"],

        "MAX_SWAP": Swap_Info()["total"]
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