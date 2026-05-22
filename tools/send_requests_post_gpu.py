import time
import requests
import GPUtil

API_URL = "http://127.0.0.1:8000/api/post-gpu/"
API_KEY = "82569fbbdbae3cc71725cbdd58943127e0a58ad47c2f7aad7c454f865a6b31c9"
NAME_SERVER = "тест"

def collect_stats():
    gpus = GPUtil.getGPUs()
    
    if gpus:
        gpu = gpus[0]
        return {
            "GPU_NAME": gpu.name,
            "MAX_GPU_THREADS": str(gpu.max_threads) if gpu.max_threads else "0",
            "GPU_SIZE_GB": f"{gpu.memoryTotal}GB"
        }
    else:
        return {
            "GPU_NAME": "No GPU Detected",
            "MAX_GPU_THREADS": "1",
            "GPU_SIZE_GB": "1"
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
    except Exception as e:
        print("Ошибка:", e)
    
    time.sleep(10)