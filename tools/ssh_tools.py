# tools/ssh_tools.py
import re
import time
import sys
import os

# Добавляем пути к проекту
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Admiral/
config_path = os.path.join(project_root, 'config')  # Admiral/config/

# Добавляем оба пути в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if config_path not in sys.path:
    sys.path.insert(0, config_path)

# Указываем настройки Django (с учетом двойной вложенности)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
except ImportError as e:
    print(f"Ошибка импорта Django: {e}")
    print(f"Project root: {project_root}")
    print(f"Config path: {config_path}")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)

# Импортируем модель - пробуем разные варианты
try:
    # Пробуем прямой импорт
    from models.sshlog.models import SSHLogEntry
    print("Импорт через 'from sshlog.models import SSHLogEntry' успешен")
except ImportError:
    try:
        # Пробуем через config
        from models.sshlog.models import SSHLogEntry
        print("Импорт через 'from models.sshlog.models import SSHLogEntry' успешен")
    except ImportError:
        try:
            # Пробуем полный путь
            from models.sshlog.models import SSHLogEntry
            print("Импорт через 'from models.config.sshlog.models import SSHLogEntry' успешен")
        except ImportError as e:
            print(f"Не удалось импортировать модель: {e}")
            sys.exit(1)

from django.utils import timezone

class SSHMonitor:
    def __init__(self, log_file='/var/log/auth.log'):
        self.log_file = log_file
    
    def monitor(self):
        """Запуск мониторинга"""
        print(f"Начинаю мониторинг {self.log_file}")
        
        try:
            with open(self.log_file, 'r') as f:
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        self.process_line(line)
                    else:
                        time.sleep(0.1)
        except FileNotFoundError:
            print(f"Файл {self.log_file} не найден!")
        except KeyboardInterrupt:
            print("\nМониторинг остановлен")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def process_line(self, line):
        """Обработка строки лога"""
        # Успешный вход
        if 'Accepted' in line and 'ssh' in line:
            match = re.search(r'for (.*?) from (.*?) port', line)
            if match:
                username = match.group(1)
                ip = match.group(2)
                try:
                    SSHLogEntry.objects.create(
                        event_type='success',
                        username=username,
                        ip_address=ip,
                        raw_log=line.strip(),
                        timestamp=timezone.now()
                    )
                    print(f"✅ Сохранен успешный вход: {username} с {ip}")
                except Exception as e:
                    print(f"Ошибка сохранения (success): {e}")
        
        # Неуспешный вход
        elif 'Failed password' in line:
            match = re.search(r'for (.*?) from (.*?) port', line)
            if match:
                username = match.group(1)
                ip = match.group(2)
                try:
                    SSHLogEntry.objects.create(
                        event_type='failed',
                        username=username,
                        ip_address=ip,
                        raw_log=line.strip(),
                        timestamp=timezone.now()
                    )
                    print(f"❌ Сохранена неудачная попытка: {username} с {ip}")
                except Exception as e:
                    print(f"Ошибка сохранения (failed): {e}")

if __name__ == '__main__':
    log_file = sys.argv[1] if len(sys.argv) > 1 else '/var/log/auth.log'
    monitor = SSHMonitor(log_file)
    monitor.monitor()