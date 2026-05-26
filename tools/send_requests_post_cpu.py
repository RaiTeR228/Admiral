#send_requests_cpu.py
import time
import requests
import psutil
import platform
from cpuinfo import get_cpu_info
from Status_system import *

API_URL = "http://127.0.0.1:8000/api/cpu/"
API_KEY = "31fae73538bd56225e08417f62d7c874c8c2c578f8afb24651dacb5b691cb442"
NAME_SERVER = "zxc"

def get_cpu_name():
    """Получение названия процессора"""
    try:
        cpu_info = get_cpu_info()
        brand_raw = cpu_info.get('brand_raw', '')
        if brand_raw:
            return brand_raw
    except:
        pass
    
    try:
        processor = platform.processor()
        if processor:
            return processor
    except:
        pass
    
    try:
        return "Unknown CPU"
    except:
        return "Unknown CPU"

def collect_stats():
    cpu = Cpu_Info()
    
    return {
        "name": NAME_SERVER,
        "INSTALL_TOKEN": API_KEY,
        "MAX_CPU_CORES": str(cpu["physical_cores"]),
        "MAX_CPU_THREADS":  str(cpu["total_cores"]), 
        "CPU_NAME": get_cpu_name(),
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