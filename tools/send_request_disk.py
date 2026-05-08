import time
import requests
import psutil
import platform

API_URL = "http://127.0.0.1:8000/api/disk/"
API_KEY = "7c2d24de67d2dfb3bb8f2984ce15e374400025f659c133a66c70565eade366fe"
NAME_SERVER = "тест"

def disk_stats():
    """Возвращает статистику для каждого диска"""
    disks_stats = []
    
    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            
            # Формируем данные в нужном серверу формате
            disk_data = {
                "DISK_NAME": partition.device,  # или partition.mountpoint
                "MAX_SWAP": psutil.swap_memory().total,  # если не собираете - отправьте 0
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