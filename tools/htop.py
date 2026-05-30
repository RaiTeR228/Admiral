import time
import requests
import psutil

API_URL = "http://127.0.0.1:8000/api/htop/"
API_KEY = "31fae73538bd56225e08417f62d7c874c8c2c578f8afb24651dacb5b691cb442"

# Предварительный проход для "прогрева"
print("Прогрев CPU счетчиков...")
for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
    try:
        proc.cpu_percent()  # Первый вызов для всех процессов
    except:
        pass

time.sleep(0.5)  # Пауза для накопления данных

while True:
    processes = []
    
    # Теперь cpu_percent() будет возвращать реальные значения
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            processes.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"] or "",
                "cpu_percent": proc.info["cpu_percent"] or 0.0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    data = {"processes": processes[:100]}
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={"Authorization": f"Api-Key {API_KEY}"},
            timeout=10
        )
        print(f"Статус: {response.status_code}, Процессов: {len(processes)}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(3)