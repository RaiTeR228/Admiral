import re
import time
from datetime import datetime

AUTH_LOG = "/var/log/auth.log"  # Стандартный путь для Ubuntu

def monitor_ssh_log():
    """Мониторинг SSH логов в реальном времени"""
    with open(AUTH_LOG, 'r') as f:
        # Переходим в конец файла
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                # Успешный вход
                if 'Accepted' in line and 'ssh' in line:
                    username = re.search(r'for (.*?) from', line)
                    ip = re.search(r'from (.*?) port', line)
                    print(f"✅ УСПЕХ - {username.group(1)} с {ip.group(1)}")
                
                # Неуспешный вход
                elif 'Failed password' in line:
                    username = re.search(r'for (.*?) from', line)
                    ip = re.search(r'from (.*?) port', line)
                    print(f"❌ НЕУСПЕХ - {username.group(1)} с {ip.group(1)}")
            
            time.sleep(0.1)

# Запуск
monitor_ssh_log()