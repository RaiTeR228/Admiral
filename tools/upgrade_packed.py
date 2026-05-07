#!/usr/bin/env python3
import subprocess
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='/var/log/apt_auto_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def run_apt_update():
    """Выполняет apt update && apt upgrade -y"""
    try:
        # Выполняем update
        logging.info("Начинаю apt update...")
        result_update = subprocess.run(
            ['apt', 'update', '-y'],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"apt update выполнен успешно: {result_update.stdout}")
        
        # Выполняем upgrade
        logging.info("Начинаю apt upgrade...")
        result_upgrade = subprocess.run(
            ['apt', 'upgrade', '-y'],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"apt upgrade выполнен успешно: {result_upgrade.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении: {e}")
        logging.error(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        return False

    # print(f"{datetime.now()}: Запуск обновления системы...")
    # if run_apt_update():
    #     print("Обновление завершено успешно")
    # else:
    #     print("Ошибка при обновлении. Проверьте лог.")