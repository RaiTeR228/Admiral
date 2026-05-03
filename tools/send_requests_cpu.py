import time
import requests
import psutil
import platform
from cpuinfo import get_cpu_info  # Добавьте эту библиотеку
from tools.Status_system import *

# API_URL = "http://127.0.0.1:8000/api/stats/"
API_URL = "http://127.0.0.1:8000/api/cpu/"
API_KEY = "7e55123c9a4d7790185774094b73e44aeaecdd1e5f74bbc3856bed7ec5a9b694"
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
        "MAX_CPU_CORES": str(cpu["physical_cores"]),
        "MAX_CPU_THREADS":  str(cpu["total_cores"]), 
        "CPU_NAME": get_cpu_name(),
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