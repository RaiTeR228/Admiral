#send_requests_cpu.py
import time
import requests
import psutil
import platform
from cpuinfo import get_cpu_info
from Status_system import *
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/cpu/"

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
