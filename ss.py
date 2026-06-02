import requests
import random
import time
from datetime import datetime
from typing import Optional, Union

api_url="http://83.143.112.253:8000/api/temp/"
api_key="005bcf529450236e9f6b62cb12c1a9012b4193b0bbab85e7667570727eff30a4"

class TempMetricsClient:
    """Клиент для отправки метрик температуры на сервер"""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Инициализация клиента
        
        Args:
            api_url: URL вашего API (например, http://localhost:8000/api/temp/)
            api_key: API ключ для аутентификации
        """
        # ВАЖНО: гарантируем, что URL заканчивается на слеш
        self.api_url = api_url.rstrip('/') + '/'  # Добавляем слеш, если его нет
        self.api_key = api_key
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        print(f"API URL будет использоваться: {self.api_url}")  # Для отладки
    
    def send_temperature(self, current_temp: Union[int, float], status_critical: Optional[bool] = None) -> dict:
        """
        Отправка данных о температуре
        
        Args:
            current_temp: Текущая температура
            status_critical: Критический статус (опционально)
        
        Returns:
            dict: Ответ от сервера
        """
        data = {
            'current_temp': current_temp
        }
        
        if status_critical is not None:
            data['status_critical'] = status_critical
        
        print(f"Отправка POST на {self.api_url}")  # Для отладки
        print(f"Данные: {data}")  # Для отладки
        
        try:
            response = requests.post(
                self.api_url,  # Теперь здесь гарантированно есть слеш
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            print(f"Статус ответа: {response.status_code}")  # Для отладки
            print(f"Ответ: {response.text}")  # Для отладки
            
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'response': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
            }
    
    def get_last_temperature(self) -> dict:
        """
        Получение последней температуры для сервера
        
        Returns:
            dict: Ответ от сервера
        """
        print(f"Отправка GET на {self.api_url}")  # Для отладки
        
        try:
            response = requests.get(
                self.api_url,
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            
            print(f"Статус ответа: {response.status_code}")  # Для отладки
            
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'response': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
            }


# Остальные функции остаются без изменений
def example_single_send():
    """Пример отправки одного значения"""
    client = TempMetricsClient(
        api_url,
        api_key
    )
    
    # Отправка только температуры
    result = client.send_temperature(25.5)
    print("Простая отправка:", result)
    
    # Отправка температуры с критическим статусом
    result = client.send_temperature(85.3, status_critical=True)
    print("С критическим статусом:", result)


def example_bulk_send():
    """Пример массовой отправки данных"""
    client = TempMetricsClient(
        api_url,
        api_key
    )
    
    # Симуляция отправки нескольких показаний
    temperatures = [22.5, 23.1, 24.8, 25.2, 26.0]
    critical_temps = [False, False, False, False, True]
    
    for i, (temp, critical) in enumerate(zip(temperatures, critical_temps), 1):
        print(f"\nОтправка #{i}: {temp}°C, critical={critical}")
        result = client.send_temperature(temp, critical)
        
        if result['success']:
            print(f"✓ Успешно: {result['data'].get('message')}")
            print(f"  ID сервера: {result['data'].get('server_id')}")
            print(f"  ID записи: {result['data'].get('temp_id')}")
        else:
            print(f"✗ Ошибка: {result['error']}")
            if result.get('response'):
                print(f"Детали: {result['response']}")
        
        time.sleep(1)


def example_monitoring_simulation():
    """Симуляция реального мониторинга"""
    client = TempMetricsClient(
        api_url,
        api_key
    )
    
    print("Начинаем мониторинг температуры...")
    print("Нажмите Ctrl+C для остановки\n")
    
    try:
        while True:
            # Генерируем случайную температуру (нормальная: 20-25, аномалии: >80)
            if random.random() < 0.05:  # 5% вероятность аномалии
                temp = random.uniform(80, 100)
                critical = True
                status = "КРИТИЧЕСКАЯ!"
            else:
                temp = random.uniform(20, 25)
                critical = False
                status = "нормальная"
            
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] Температура: {temp:.1f}°C - {status}")
            
            result = client.send_temperature(temp, critical)
            
            if result['success']:
                print(f"  → Данные сохранены (ID: {result['data'].get('temp_id')})")
            else:
                print(f"  → ОШИБКА: {result['error']}")
                if result.get('response'):
                    print(f"  → Ответ сервера: {result['response']}")
            
            print("-" * 40)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nМониторинг остановлен")


def example_get_last_data():
    """Пример получения последних данных"""
    client = TempMetricsClient(
        api_url,
        api_key
    )
    
    result = client.get_last_temperature()
    
    if result['success']:
        data = result['data']
        print("Последние данные о температуре:")
        print(f"  UUID сервера: {data.get('server_uuid')}")
        print(f"  Температура: {data['temperature']['current_temp']}°C")
        print(f"  Критический статус: {data['temperature']['status_critical']}")
        print(f"  Время создания: {data['temperature']['created_at']}")
    else:
        print(f"Ошибка получения данных: {result['error']}")
        if result.get('response'):
            print(f"Детали: {result['response']}")


# Скрипт для командной строки
if __name__ == "__main__":
    import sys
    
    # Конфигурация по умолчанию
    DEFAULT_URL = "http://83.143.112.253:8000/api/temp/"
    DEFAULT_KEY = "005bcf529450236e9f6b62cb12c1a9012b4193b0bbab85e7667570727eff30a4"
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python script.py send <температура> [critical]")
        print("  python script.py get")
        print("  python script.py monitor")
        print("  python script.py bulk")
        print("\nПримеры:")
        print("  python script.py send 25.5")
        print("  python script.py send 85.3 true")
        print("  python script.py get")
        print("  python script.py monitor")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    client = TempMetricsClient(DEFAULT_URL, DEFAULT_KEY)
    
    if command == "send":
        if len(sys.argv) < 3:
            print("Ошибка: укажите температуру")
            sys.exit(1)
        
        temp = float(sys.argv[2])
        critical = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else None
        
        result = client.send_temperature(temp, critical)
        
        if result['success']:
            print(f"✓ Успешно отправлено: {result['data']}")
        else:
            print(f"✗ Ошибка: {result['error']}")
            if result.get('response'):
                print(f"Ответ сервера: {result['response']}")
    
    elif command == "get":
        result = client.get_last_temperature()
        
        if result['success']:
            print(f"✓ Данные получены: {result['data']}")
        else:
            print(f"✗ Ошибка: {result['error']}")
            if result.get('response'):
                print(f"Ответ сервера: {result['response']}")
    
    elif command == "monitor":
        example_monitoring_simulation()
    
    elif command == "bulk":
        example_bulk_send()
    
    else:
        print(f"Неизвестная команда: {command}")