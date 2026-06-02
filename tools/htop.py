import time
import requests
import psutil
from dotenv import load_dotenv
import os

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/htop/"

BLACKLIST_PIDS = {0}
BLACKLIST_NAMES = {"System Idle Process"}

def is_blacklisted(proc_info):
    """Проверка, находится ли процесс в черном списке"""
    pid = proc_info.get("pid")
    name = proc_info.get("name", "").lower()
    
    # Проверка по PID
    if pid in BLACKLIST_PIDS:
        return True
    
    # Проверка по имени процесса
    if name in BLACKLIST_NAMES:
        return True
    
    return False

# Предварительный проход для "прогрева"
for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
    try:
        proc.cpu_percent()
    except:
        pass

time.sleep(0.5)

while True:
    processes = []
    
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            proc_info = {
                "pid": proc.info["pid"],
                "name": proc.info["name"] or "",
                "cpu_percent": proc.info["cpu_percent"] or 0.0
            }
            
            # Пропускаем процессы из черного списка
            if is_blacklisted(proc_info):
                print(f"Пропущен процесс из черного списка: PID={proc_info['pid']}, Name={proc_info['name']}")
                continue
                
            processes.append(proc_info)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    data = {"processes": processes[:100]}
    
    # Отладочная информация
    # print(f"Всего процессов после фильтрации: {len(processes)}")
    if len(processes) > 0:
        print(f"Топ-3 процесса: {[(p['pid'], p['name'], p['cpu_percent']) for p in processes[:3]]}")
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={"Authorization": f"Api-Key {API_KEY}"},
            timeout=10
        )
        print(f"Статус: {response.status_code}, Отправлено процессов: {len(processes[:100])}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(3)