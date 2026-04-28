# client_register.py
import requests
import json
import os
from pathlib import Path

class ServerMonitorClient:
    def __init__(self, server_url, install_token):
        self.server_url = server_url.rstrip('/')
        self.install_token = install_token
        self.config_file = Path.home() / '.server_monitor_config.json'
        self.api_key = None
        self.load_config()
    
    def load_config(self):
        """Загрузка сохраненной конфигурации"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
    
    def save_config(self, server_name, server_id, api_key):
        """Сохранение конфигурации"""
        config = {
            'server_url': self.server_url,
            'server_name': server_name,
            'server_id': server_id,
            'api_key': api_key
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(self.config_file, 0o600)  # Только для чтения владельцем
    
    def register(self, server_name, system_info=None):
        """Регистрация сервера"""
        data = {
            'install_token': self.install_token,
            'name': server_name,
        }
        
        if system_info:
            data['system_pc'] = system_info.get('system')
            data['local_name_pc'] = system_info.get('hostname')
        
        print(f"📡 Регистрация сервера '{server_name}'...")
        
        try:
            response = requests.post(
                f"{self.server_url}/api/register/",
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    self.save_config(
                        result['name'],
                        result['server_id'],
                        result['api_key']
                    )
                    print(f"✅ {result['message']}")
                    print(f"🔑 API Key: {result['api_key']}")
                    print(f"🆔 Server ID: {result['server_id']}")
                    return True
                else:
                    print(f"❌ Ошибка: {result.get('error')}")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_api_key(self, server_name):
        """Получение существующего API ключа"""
        data = {
            'install_token': self.install_token,
            'name': server_name
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/get-api-key/",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.save_config(
                        result['name'],
                        result['server_id'],
                        result['api_key']
                    )
                    print(f"✅ API Key получен для {result['name']}")
                    return result['api_key']
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        return None
    
    def regenerate_api_key(self, server_name):
        """Перегенерация API ключа"""
        data = {
            'install_token': self.install_token,
            'name': server_name
        }
        
        confirm = input("⚠️  Вы уверены? Старый ключ перестанет работать! (yes/no): ")
        if confirm.lower() != 'yes':
            print("Операция отменена")
            return None
        
        try:
            response = requests.post(
                f"{self.server_url}/api/regenerate-api-key/",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.save_config(
                        server_name,
                        result['server_id'],
                        result['new_api_key']
                    )
                    print(f"✅ API Key перегенерирован: {result['new_api_key']}")
                    return result['new_api_key']
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        return None


def main():
    import platform
    
    print("=" * 50)
    print("🔐 РЕГИСТРАЦИЯ СЕРВЕРА В СИСТЕМЕ МОНИТОРИНГА")
    print("=" * 50)
    
    # Ввод данных
    server_url = input("URL сервера мониторинга (например, http://localhost:8000): ").strip()
    install_token = input("Install Token: ").strip()
    
    # Получение информации о системе
    server_name = input("Имя сервера (Enter для автоматического): ").strip()
    if not server_name:
        server_name = platform.node()
    
    # Создание клиента
    client = ServerMonitorClient(server_url, install_token)
    
    # Меню
    print("\nВыберите действие:")
    print("1. Зарегистрировать новый сервер")
    print("2. Получить API ключ для существующего")
    print("3. Перегенерировать API ключ")
    
    choice = input("Ваш выбор (1-3): ").strip()
    
    if choice == '1':
        system_info = {
            'system': platform.system() + " " + platform.release(),
            'hostname': platform.node()
        }
        client.register(server_name, system_info)
    
    elif choice == '2':
        api_key = client.get_api_key(server_name)
        if api_key:
            print(f"🔑 Ваш API ключ: {api_key}")
    
    elif choice == '3':
        client.regenerate_api_key(server_name)
    
    else:
        print("Неверный выбор")


if __name__ == '__main__':
    main()