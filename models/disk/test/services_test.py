# test_disk_services.py
import os
import sys
import django
from pathlib import Path

# Настройка Django
project_root = Path(__file__).parent
model_path = project_root / 'models'
sys.path.insert(0, str(model_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'models.config.settings')
django.setup()

# Импортируем сервисы
from disk.services import (
    ServerAuthenticationService,
    DiskDataValidationService,
    DiskMetricsService,
    DiskAlertService,
    DiskAnalyticsService
)
from server.models import Server

def test_validation():
    """Тест валидации данных диска"""
    print("\n=== Тест 1: Валидация данных диска ===")
    
    # Правильные данные
    valid_data = {
        'MAX_SWAP': '8GB',
        'MAX_DISK': '500GB',
        'DISK_NAME': 'SSD Samsung 970 EVO',
        'Free_DISK': '250GB'
    }
    
    is_valid, errors, cleaned = DiskDataValidationService.validate_disk_data(valid_data)
    print(f"✓ Правильные данные: валидны = {is_valid}")
    if is_valid:
        print(f"  Очищенные данные: {cleaned}")
    
    # Неправильные данные
    invalid_data = {
        'MAX_SWAP': '-5GB',
        'MAX_DISK': '10000TB',  # слишком много
        'Free_DISK': '600GB'  # больше чем MAX_DISK
    }
    
    is_valid, errors, cleaned = DiskDataValidationService.validate_disk_data(invalid_data)
    print(f"✗ Неправильные данные: валидны = {is_valid}")
    print(f"  Ошибки: {errors}")

def test_save_metrics():
    """Тест сохранения метрик диска"""
    print("\n=== Тест 2: Сохранение метрик диска ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов в БД")
        return
    
    disk_data = {
        'MAX_SWAP': '16GB',
        'MAX_DISK': '1TB',
        'DISK_NAME': 'NVMe SSD',
        'Free_DISK': '750GB'
    }
    
    try:
        disk_instance, created = DiskMetricsService.save_or_update_disk_metrics(server, disk_data)
        
        if created:
            print(f"✓ Создана новая запись диска")
        else:
            print(f"✓ Обновлена существующая запись")
        
        print(f"  ID: {disk_instance.id}")
        print(f"  Disk: {disk_instance.DISK_NAME}")
        print(f"  Size: {disk_instance.MAX_DISK}")
        print(f"  Free: {disk_instance.Free_DISK}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_usage_percentage():
    """Тест расчета процента использования"""
    print("\n=== Тест 3: Расчет процента использования ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов")
        return
    
    usage = DiskMetricsService.get_disk_usage_percentage(server)
    if usage is not None:
        print(f"✓ Процент использования диска: {usage}%")
    else:
        print("❌ Не удалось рассчитать процент использования")

def test_anomalies():
    """Тест обнаружения аномалий"""
    print("\n=== Тест 4: Обнаружение аномалий диска ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов")
        return
    
    # Тест с критически малым свободным местом
    critical_data = {
        'MAX_DISK': '100GB',
        'Free_DISK': '5GB'  # всего 5% свободно
    }
    
    warnings = DiskAlertService.check_disk_anomalies(critical_data, server)
    if warnings:
        print(f"⚠ Обнаружены аномалии: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning['message']} (Severity: {warning['severity']})")

def test_statistics():
    """Тест статистики"""
    print("\n=== Тест 5: Статистика дисков ===")
    
    stats = DiskAnalyticsService.get_disk_statistics()
    print(f"✓ Статистика:")
    print(f"  Всего серверов с дисками: {stats['total_servers_with_disk']}")
    print(f"  Средний размер диска (GB): {stats['average_disk_size_gb']}")
    print(f"  Общий объем дисков (GB): {stats['total_disk_space_gb']}")
    print(f"  Серверов с SWAP: {stats['disks_with_swap']}")

def test_full_integration():
    """Полный тест интеграции"""
    print("\n" + "=" * 60)
    print("ПОЛНЫЙ ТЕСТ ИНТЕГРАЦИИ DISK")
    print("=" * 60)
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов. Сначала создайте сервер")
        return
    
    print(f"1. Сервер: {server.name}")
    
    # Имитируем данные от клиента
    disk_data = {
        'MAX_SWAP': '32GB',
        'MAX_DISK': '2TB',
        'DISK_NAME': 'Seagate Barracuda',
        'Free_DISK': '1.5TB'
    }
    
    print(f"2. Данные от клиента: {disk_data}")
    
    # Валидация
    is_valid, errors, cleaned = DiskDataValidationService.validate_disk_data(disk_data)
    if not is_valid:
        print(f"❌ Валидация не пройдена: {errors}")
        return
    
    print(f"3. Валидация пройдена ✓")
    
    # Проверка аномалий
    warnings = DiskAlertService.check_disk_anomalies(cleaned, server)
    if warnings:
        print(f"4. Обнаружены предупреждения: {len(warnings)}")
    else:
        print(f"4. Аномалий нет ✓")
    
    # Сохранение
    disk, created = DiskMetricsService.save_or_update_disk_metrics(server, cleaned)
    print(f"5. Данные сохранены (created={created}) ✓")
    
    # Проверка
    saved_metrics = DiskMetricsService.get_disk_metrics_for_server(server)
    print(f"6. Проверка сохраненных данных:")
    print(f"   Disk: {saved_metrics['disk_name']}")
    print(f"   Size: {saved_metrics['max_disk']}")
    print(f"   Free: {saved_metrics['free_disk']}")
    
    # Процент использования
    usage = DiskMetricsService.get_disk_usage_percentage(server)
    print(f"   Usage: {usage}%")
    
    print("\n✅ Полный тест интеграции пройден успешно!")

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ DISK СЕРВИСОВ")
    print("=" * 60)
    
    test_validation()
    test_save_metrics()
    test_usage_percentage()
    test_anomalies()
    test_statistics()
    test_full_integration()
    
    print("\n" + "=" * 60)
    print("ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)