import time
import requests
import psutil
import platform
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/disk/"

def disk_stats():
    """Возвращает статистику для каждого диска"""
    disks_stats = []
    
    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            
            disk_data = {
                "DISK_NAME": partition.device,
                "MAX_SWAP": psutil.swap_memory().total,
                "MAX_DISK": partition_usage.total,
                "Free_DISK": partition_usage.free
            }
            disks_stats.append(disk_data)
            
        except PermissionError:
            continue
    
    return disks_stats

while True:
    all_disks = disk_stats()
    
    # Отправляем каждый диск отдельно
    for disk_data in all_disks:
        try:
            response = requests.post(
                API_URL,
                json=disk_data,  # ← отправляем плоский словарь
                headers={"Authorization": f"Api-Key {API_KEY}"},
                timeout=5
            )
            print(f"Диск {disk_data['DISK_NAME']}: статус {response.status_code}")
            print("Ответ:", response.text)
        except Exception as e:
            print(f"Ошибка: {e}")
    
    time.sleep(10)