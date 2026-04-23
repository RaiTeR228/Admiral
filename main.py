# main_with_migrations.py
import os
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent
model_path = project_root / 'models'
os.chdir(model_path)

def run_command(cmd):
    print(f"▶️ {cmd}")
    subprocess.run(cmd, shell=True)

print("🚀 Запуск Admiral с миграциями...")

# Выполняем миграции
run_command(f"{sys.executable} manage.py makemigrations")
run_command(f"{sys.executable} manage.py migrate")

# Запускаем сервер
print("\n🌐 Запуск Django сервера...")
try:
    subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
except KeyboardInterrupt:
    print("\n✅ Остановлено")