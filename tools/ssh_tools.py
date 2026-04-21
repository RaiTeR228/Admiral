import re
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from config.SSHLog.models import SSHLogEntry  # Замените your_app на имя вашего приложения

class Command(BaseCommand):
    help = 'Мониторинг SSH логов и сохранение в БД'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--log-file',
            type=str,
            default='/var/log/auth.log',
            help='Путь к файлу лога'
        )
    
    def handle(self, *args, **options):
        log_file = options['log_file']
        self.stdout.write(f"Начинаю мониторинг {log_file}")
        
        try:
            with open(log_file, 'r') as f:
                # Переходим в конец файла
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        self.process_line(line)
                    else:
                        time.sleep(0.1)
        except FileNotFoundError:
            self.stderr.write(f"Файл {log_file} не найден!")
        except KeyboardInterrupt:
            self.stdout.write("\nМониторинг остановлен")
    
    def process_line(self, line):
        """Обработка одной строки лога"""
        # Успешный вход
        if 'Accepted' in line and 'ssh' in line:
            match = re.search(r'for (.*?) from (.*?) port', line)
            if match:
                username = match.group(1)
                ip = match.group(2)
                
                SSHLogEntry.objects.create(
                    event_type='success',
                    username=username,
                    ip_address=ip,
                    raw_log=line.strip(),
                    timestamp=timezone.now()
                )
                self.stdout.write(f"Сохранен успешный вход: {username} с {ip}")
        
        # Неуспешный вход
        elif 'Failed password' in line:
            match = re.search(r'for (.*?) from (.*?) port', line)
            if match:
                username = match.group(1)
                ip = match.group(2)
                
                SSHLogEntry.objects.create(
                    event_type='failed',
                    username=username,
                    ip_address=ip,
                    raw_log=line.strip(),
                    timestamp=timezone.now()
                )
                self.stdout.write(f"Сохранена неудачная попытка: {username} с {ip}")