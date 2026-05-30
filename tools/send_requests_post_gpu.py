import time
import requests
import GPUtil
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = "http://127.0.0.1:8000/api/gpu/"
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")

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