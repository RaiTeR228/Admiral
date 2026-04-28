#!/usr/bin/env python3
# type: ignore
import re
import sys
import time
import os
import django
from datetime import datetime
from pathlib import Path

models_path = Path(__file__).resolve().parent.parent / 'models'
sys.path.insert(0, str(models_path))

# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Настраиваем Django
import django
django.setup()

# Теперь импортируем модели (без models., так как мы уже в папке models)
from sshlog.models import SSHLogEntry
from server.models import Server

def parse_ssh_log_line(line):
    """
    Парсит строку лога SSH и возвращает словарь с данными
    """
    # Паттерн для timestamp: 2026-03-27T17:28:10.658373+00:00
    timestamp_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{2}:\d{2})'
    
    # Паттерн для Accepted/Failed password
    auth_pattern = r'(Accepted|Failed) password for (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port (\d+)'
    
    # Паттерн для Connection reset
    reset_pattern = r'Connection reset by authenticating user (\w+) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port (\d+)'
    
    # Паттерн для repeated messages
    repeated_pattern = r'message repeated (\d+) times: \[ (.*) \]'
    
    match = re.search(timestamp_pattern, line)
    if not match:
        return None
    
    timestamp_str = match.group(1)
    # Парсим timestamp (обрезаем микросекунды до 6 знаков)
    try:
        # Преобразуем ISO формат с timezone
        timestamp = datetime.fromisoformat(timestamp_str.replace('+00:00', '+00:00'))
    except:
        timestamp = datetime.now()
    
    # Проверяем на повторяющиеся сообщения
    repeated_match = re.search(repeated_pattern, line)
    if repeated_match:
        count = int(repeated_match.group(1))
        original_message = repeated_match.group(2)
        # Рекурсивно парсим оригинальное сообщение
        parsed = parse_ssh_log_line(original_message)
        if parsed:
            return {
                'timestamp': timestamp,
                'event_type': parsed['event_type'],
                'username': parsed['username'],
                'ip_address': parsed['ip_address'],
                'port': parsed['port'],
                'raw_log': line,
                'repeated_count': count
            }
        return None
    
    # Проверяем на успешный/неудачный вход
    auth_match = re.search(auth_pattern, line)
    if auth_match:
        status = auth_match.group(1)
        username = auth_match.group(2)
        ip_address = auth_match.group(3)
        port = int(auth_match.group(4))
        
        event_type = 'success' if status == 'Accepted' else 'failed'
        
        return {
            'timestamp': timestamp,
            'event_type': event_type,
            'username': username,
            'ip_address': ip_address,
            'port': port,
            'raw_log': line
        }
    
    # Проверяем на сброс соединения
    reset_match = re.search(reset_pattern, line)
    if reset_match:
        username = reset_match.group(1)
        ip_address = reset_match.group(2)
        port = int(reset_match.group(3))
        
        return {
            'timestamp': timestamp,
            'event_type': 'failed',
            'username': username,
            'ip_address': ip_address,
            'port': port,
            'raw_log': line
        }
    
    return None

def get_server_uuid():
    """
    Получает UUID сервера (первый в БД или создает новый)
    """
    server = Server.objects.first()
    if not server:
        # Создаем тестовый сервер, если его нет
        server = Server.objects.create(
            name='Local Server',
            api_key='test_key_123',
            SystemPC='Linux',
            Local_Name_PC='localhost'
        )
        print(f"✅ Создан новый сервер с UUID: {server.uuid}")
    return str(server.uuid)

def save_ssh_log_entry(parsed_data, server_uuid):
    """
    Сохраняет запись в БД
    """
    try:
        # Проверяем, нет ли уже такой записи (чтобы избежать дубликатов)
        existing = SSHLogEntry.objects.filter(
            timestamp=parsed_data['timestamp'],
            username=parsed_data['username'],
            ip_address=parsed_data['ip_address'],
            event_type=parsed_data['event_type']
        ).first()
        
        if existing:
            return False
        
        entry = SSHLogEntry.objects.create(
            UuidServer=server_uuid,
            event_type=parsed_data['event_type'],
            username=parsed_data['username'],
            ip_address=parsed_data['ip_address'],
            timestamp=parsed_data['timestamp'],
            raw_log=parsed_data['raw_log']
        )
        print(f"💾 Сохранено: {entry}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def monitor_ssh_logs(log_file='/var/log/auth.log', follow=True):
    """
    Мониторит SSH логи и сохраняет в БД
    """
    print(f"🔍 Начинаем мониторинг {log_file}")
    
    if not os.path.exists(log_file):
        print(f"❌ Файл {log_file} не найден!")
        return
    
    server_uuid = get_server_uuid()
    print(f"🆔 UUID сервера: {server_uuid}")
    
    # Для отслеживания позиции в файле
    file_position = 0
    
    # При первом запуске читаем последние 1000 строк
    with open(log_file, 'r') as f:
        # Перемещаемся в конец файла
        f.seek(0, os.SEEK_END)
        file_position = f.tell()
        
        # Если нужно прочитать последние строки
        if not follow:
            f.seek(0)
            lines = f.readlines()
            for line in lines[-1000:]:  # Последние 1000 строк
                parsed = parse_ssh_log_line(line)
                if parsed:
                    save_ssh_log_entry(parsed, server_uuid)
    
    if not follow:
        return
    
    # Режим слежения за файлом
    print(f"📡 Слежение за логами... (Ctrl+C для остановки)")
    
    try:
        while True:
            with open(log_file, 'r') as f:
                f.seek(file_position)
                new_lines = f.readlines()
                file_position = f.tell()
                
                for line in new_lines:
                    # Проверяем строки, связанные с SSH
                    if 'sshd' in line and ('Accepted' in line or 'Failed' in line or 'Connection reset' in line):
                        parsed = parse_ssh_log_line(line)
                        if parsed:
                            save_ssh_log_entry(parsed, server_uuid)
                            print(f"📝 {line.strip()}")
            
            time.sleep(1)  # Пауза между проверками
            
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен")

if __name__ == '__main__':
    log_file = sys.argv[1] if len(sys.argv) > 1 else '/var/log/auth.log'
    follow = len(sys.argv) < 3 or sys.argv[2] != '--once'
    
    monitor_ssh_logs(log_file, follow)