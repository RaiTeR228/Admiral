# test_gpu_services.py
import os
import sys
import django
from pathlib import Path

# Настройка Django
project_root = Path(__file__).parent
model_path = project_root / 'models'
sys.path.insert(0, str(model_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Импортируем сервисы
from gpu.services import (
    ServerAuthenticationService,
    GPUDataValidationService,
    GPUMetricsService,
    GPUAlertService,
    GPUAnalyticsService,
    GPURecommendationService
)
from server.models import Server

def test_validation():
    """Тест валидации данных GPU"""
    print("\n=== Тест 1: Валидация данных GPU ===")
    
    # Правильные данные
    valid_data = {
        'MAX_GPU_THREADS': '3584',
        'GPU_NAME': 'NVIDIA GeForce RTX 3070',
        'GPU_SIZE_GB': '8GB'
    }
    
    is_valid, errors, cleaned, warnings = GPUDataValidationService.validate_gpu_data(valid_data)
    print(f"✓ Правильные данные: валидны = {is_valid}")
    if is_valid:
        print(f"  Очищенные данные: {cleaned}")
    if warnings:
        print(f"  Предупреждения: {warnings}")
    
    # Неправильные данные
    invalid_data = {
        'MAX_GPU_THREADS': '-100',
        'GPU_SIZE_GB': '1000TB',  # слишком много
        'GPU_NAME': 'A' * 300  # слишком длинное
    }
    
    is_valid, errors, cleaned, warnings = GPUDataValidationService.validate_gpu_data(invalid_data)
    print(f"✗ Неправильные данные: валидны = {is_valid}")
    print(f"  Ошибки: {errors}")

def test_save_metrics():
    """Тест сохранения метрик GPU"""
    print("\n=== Тест 2: Сохранение метрик GPU ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов в БД. Сначала создайте сервер")
        return
    
    gpu_data = {
        'MAX_GPU_THREADS': '5888',
        'GPU_NAME': 'NVIDIA GeForce RTX 3080 Ti',
        'GPU_SIZE_GB': '12GB'
    }
    
    try:
        gpu_instance, created, warnings = GPUMetricsService.save_or_update_gpu_metrics(server, gpu_data)
        
        if created:
            print(f"✓ Создана новая запись GPU")
        else:
            print(f"✓ Обновлена существующая запись")
        
        print(f"  ID: {gpu_instance.id}")
        print(f"  GPU: {gpu_instance.GPU_NAME}")
        print(f"  Threads: {gpu_instance.MAX_GPU_THREADS}")
        print(f"  Memory: {gpu_instance.GPU_SIZE_GB}")
        if warnings:
            print(f"  Предупреждения: {warnings}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_performance_score():
    """Тест расчета производительности"""
    print("\n=== Тест 3: Расчет производительности GPU ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов")
        return
    
    score = GPUMetricsService.get_gpu_performance_score(server)
    if score is not None:
        print(f"✓ Производительность GPU: {score} баллов")
        
        # Интерпретация
        if score > 10000:
            print("  💪 Очень мощный GPU (High-End)")
        elif score > 5000:
            print("  👍 Хороший GPU (Mid-Range)")
        elif score > 1000:
            print("  👌 Базовый GPU (Entry-Level)")
        else:
            print("  💤 Слабый GPU (Legacy/Integrated)")
    else:
        print("❌ Не удалось рассчитать производительность")

def test_recommendations():
    """Тест рекомендаций"""
    print("\n=== Тест 4: Рекомендации по апгрейду ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов")
        return
    
    recommendations = GPURecommendationService.get_upgrade_recommendations(server)
    
    if recommendations['has_gpu']:
        print(f"✓ GPU найден: {recommendations['current_gpu']}")
        print(f"  Оценка производительности: {recommendations['performance_score']}")
        
        if recommendations['recommendations']:
            print(f"  Рекомендации ({len(recommendations['recommendations'])}):")
            for rec in recommendations['recommendations']:
                print(f"    - [{rec['priority']}] {rec['recommendation']}")
        else:
            print("  ✅ Рекомендаций по апгрейду нет")
    else:
        print(f"ℹ️ {recommendations['message']}")

def test_statistics():
    """Тест статистики"""
    print("\n=== Тест 5: Статистика GPU ===")
    
    stats = GPUAnalyticsService.get_gpu_statistics()
    print(f"✓ Статистика GPU:")
    print(f"  Всего GPU: {stats['total_gpus']}")
    print(f"  GPU с названиями: {stats['gpus_with_name']}")
    print(f"  Производители: {stats['manufacturers']}")
    print(f"  Всего потоков: {stats['total_threads']}")
    print(f"  Среднее потоков: {stats['average_threads_per_gpu']}")
    print(f"  Всего VRAM: {stats['total_memory_gb']} GB")
    print(f"  Средний VRAM: {stats['average_memory_gb']} GB")
    print(f"  Макс. VRAM: {stats['largest_gpu_memory_gb']} GB")

def test_powerful_gpus():
    """Тест поиска мощных GPU"""
    print("\n=== Тест 6: Мощные GPU ===")
    
    powerful = GPUAnalyticsService.get_powerful_gpus(threshold_threads=4000, threshold_memory=6)
    
    if powerful:
        print(f"✓ Найдено мощных GPU: {len(powerful)}")
        for i, gpu_data in enumerate(powerful[:5], 1):  # Показываем первые 5
            print(f"  {i}. {gpu_data['gpu_name']}")
            print(f"     Потоки: {gpu_data['threads']}, Память: {gpu_data['memory']}")
            print(f"     Причина: {gpu_data['reason']}")
    else:
        print("ℹ️ Мощных GPU не найдено")

def test_anomalies():
    """Тест обнаружения аномалий"""
    print("\n=== Тест 7: Обнаружение аномалий GPU ===")
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов")
        return
    
    # Тест с аномальными данными
    anomalous_data = {
        'MAX_GPU_THREADS': '50000',  # слишком много
        'GPU_SIZE_GB': '2GB',         # мало для такого количества потоков
        'GPU_NAME': 'Unknown GPU'
    }
    
    warnings = GPUAlertService.check_gpu_anomalies(anomalous_data, server)
    if warnings:
        print(f"⚠ Обнаружены аномалии: {len(warnings)}")
        for warning in warnings:
            print(f"  - [{warning['severity']}] {warning['message']}")
    else:
        print(f"✓ Аномалий не обнаружено")

def test_full_integration():
    """Полный тест интеграции"""
    print("\n" + "=" * 60)
    print("ПОЛНЫЙ ТЕСТ ИНТЕГРАЦИИ GPU")
    print("=" * 60)
    
    server = Server.objects.first()
    if not server:
        print("❌ Нет серверов. Сначала создайте сервер через generate_api_token")
        return
    
    print(f"1. Сервер: {server.name} (UUID: {server.uuid})")
    
    # Имитируем данные от клиента
    gpu_data = {
        'MAX_GPU_THREADS': '10752',
        'GPU_NAME': 'NVIDIA GeForce RTX 4090',
        'GPU_SIZE_GB': '24GB'
    }
    
    print(f"2. Данные от клиента: {gpu_data}")
    
    # Валидация
    is_valid, errors, cleaned, warnings = GPUDataValidationService.validate_gpu_data(gpu_data)
    if not is_valid:
        print(f"❌ Валидация не пройдена: {errors}")
        return
    
    print(f"3. Валидация пройдена ✓")
    if warnings:
        print(f"   Предупреждения валидации: {warnings}")
    
    # Сохранение
    gpu_instance, created, save_warnings = GPUMetricsService.save_or_update_gpu_metrics(server, cleaned)
    print(f"4. Данные сохранены (created={created}) ✓")
    
    # Проверка производительности
    score = GPUMetricsService.get_gpu_performance_score(server)
    print(f"5. Оценка производительности: {score} баллов")
    
    # Получение метрик
    saved_metrics = GPUMetricsService.get_gpu_metrics_for_server(server)
    print(f"6. Проверка сохраненных данных:")
    print(f"   GPU: {saved_metrics['gpu_name']}")
    print(f"   Потоки: {saved_metrics['max_threads']}")
    print(f"   Память: {saved_metrics['gpu_size_gb']}")
    
    # Рекомендации
    recommendations = GPURecommendationService.get_upgrade_recommendations(server)
    if recommendations['recommendations']:
        print(f"7. Есть рекомендации по улучшению")
    
    print("\n✅ Полный тест интеграции пройден успешно!")

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ GPU СЕРВИСОВ")
    print("=" * 60)
    
    test_validation()
    test_save_metrics()
    test_performance_score()
    test_recommendations()
    test_statistics()
    test_powerful_gpus()
    test_anomalies()
    test_full_integration()
    
    print("\n" + "=" * 60)
    print("ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)