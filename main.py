# main.py
import os
import sys
import subprocess
from pathlib import Path

# Определяем пути
project_root = Path(__file__).parent
model_path = project_root / 'models'
tools_path = project_root / 'tools'

def run_command(cmd, wait=True):
    """Запуск команды"""
    print(f"▶️  Выполнение: {cmd}")
    
    if wait:
        # Обычный запуск с ожиданием
        result = subprocess.run(cmd, shell=True)
        return result
    else:
        # Запуск в фоне (для параллельной работы)
        process = subprocess.Popen(cmd, shell=True)
        return process

def run_ssh_monitor(log_file='/var/log/auth.log'):
    """Запуск SSH монитора"""
    # Используем Path объект для правильного пути
    ssh_script = tools_path / 'ssh_tools.py'
    
    if not ssh_script.exists():
        print(f"❌ Файл не найден: {ssh_script}")
        return None
    
    cmd = f"{sys.executable} {ssh_script} {log_file}"
    print(f"📡 Запуск SSH монитора...")
    
    # Запускаем в фоне
    process = run_command(cmd, wait=False)
    return process

def run_migrations():
    """Запуск миграций Django"""
    print("\n---------- Запуск миграций")
    os.chdir(model_path)
    
    run_command(f"{sys.executable} manage.py makemigrations")
    run_command(f"{sys.executable} manage.py migrate")
    
    # Возвращаемся обратно
    os.chdir(project_root)

def run_django_server(host='127.0.0.1', port='8000'):
    """Запуск Django сервера"""
    print(f"\n---------- Запуск Django сервера на {host}:{port}")
    os.chdir(model_path)
    
    try:
        # Запускаем сервер в фоне
        process = subprocess.Popen([sys.executable, 'manage.py', 'runserver', f'{host}:{port}'])
        return process
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        os.chdir(project_root)

def init_django():
    """Инициализация Django для доступа к моделям"""
    # Добавляем путь к папке models
    sys.path.insert(0, str(model_path))
    
    # Устанавливаем настройки Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Инициализируем Django
    import django
    django.setup()

def generate_api_token():
    """Генерация API токена для сервера"""
    print("\n" + "=" * 50)
    print("🔐 ГЕНЕРАЦИЯ API ТОКЕНА")
    print("=" * 50)
    
    try:
        # Инициализируем Django
        init_django()
        
        # Импортируем модель Server из правильного места
        from server.models import Server
        import secrets
        
        print("\n📝 Введите данные сервера:")
        print("-" * 40)
        
        server_name = input("Имя сервера: ").strip()
        if not server_name:
            print("❌ Ошибка: Имя сервера обязательно!")
            return
        
        # Дополнительная информация (опционально)
        # add_extra = input("Добавить дополнительную информацию? (y/n): ").strip().lower()
        
        import psutil
        import platform
        import socket
        hostname = socket.gethostname()
        ip_address =  socket.gethostbyname(hostname)
        system_pc = platform.system()
        local_name_pc = platform.node()


        
        # Проверяем, существует ли сервер с таким именем
        existing_server = Server.objects.filter(name=server_name).first()
        
        if existing_server:
            print(f"\n⚠️  Сервер с именем '{server_name}' уже существует!")
            print(f"   ID: {existing_server.id}")
            print(f"   UUID: {existing_server.uuid}")
            print(f"   Создан: {existing_server.created_at}")
            
            regenerate = input("\nПерегенерировать API ключ? (y/n): ").strip().lower()
            
            if regenerate == 'y':
                new_api_key = secrets.token_hex(32)
                existing_server.api_key = new_api_key
                
                # Обновляем дополнительную информацию, если указана
                if ip_address:
                    existing_server.ip = ip_address
                if system_pc:
                    existing_server.SystemPC = system_pc
                if local_name_pc:
                    existing_server.Local_Name_PC = local_name_pc
                
                existing_server.save()
                
                print("\n" + "=" * 50)
                print("✅ API КЛЮЧ ПЕРЕГЕНЕРИРОВАН!")
                print("=" * 50)
                print(f"📌 Сервер: {existing_server.name}")
                print(f"🆔 Server ID: {existing_server.id}")
                print(f"🔑 UUID: {existing_server.uuid}")
                print(f"🔐 API KEY: {new_api_key}")
                print(f"🌐 IP: {existing_server.ip}")
                print(f"💻 Система: {existing_server.SystemPC}")
                print(f"🏠 Локальное имя: {existing_server.Local_Name_PC}")
                print("=" * 50)
                print("\n⚠️  ВНИМАНИЕ! Старый API ключ больше не действителен!")
                print("Сохраните новый ключ в безопасном месте!\n")
            else:
                # Показываем существующий ключ
                print("\n" + "=" * 50)
                print("📋 ИНФОРМАЦИЯ О СЕРВЕРЕ")
                print("=" * 50)
                print(f"📌 Сервер: {existing_server.name}")
                print(f"🆔 Server ID: {existing_server.id}")
                print(f"🔑 UUID: {existing_server.uuid}")
                print(f"🔐 API KEY: {existing_server.api_key}")
                if existing_server.ip:
                    print(f"🌐 IP: {existing_server.ip}")
                if existing_server.SystemPC:
                    print(f"💻 Система: {existing_server.SystemPC}")
                if existing_server.Local_Name_PC:
                    print(f"🏠 Локальное имя: {existing_server.Local_Name_PC}")
                print(f"📅 Создан: {existing_server.created_at}")
                print("=" * 50)
        else:
            # Создаем новый сервер
            api_key = secrets.token_hex(32)
            
            server = Server.objects.create(
                name=server_name,
                api_key=api_key,
                ip=ip_address,
                SystemPC=system_pc,
                Local_Name_PC=local_name_pc
            )
            
            print("\n" + "=" * 50)
            print("✅ НОВЫЙ СЕРВЕР УСПЕШНО ЗАРЕГИСТРИРОВАН!")
            print("=" * 50)
            print(f"📌 Имя сервера: {server.name}")
            print(f"🆔 Server ID: {server.id}")
            print(f"🔑 UUID: {server.uuid}")
            print(f"🔐 API KEY: {api_key}")
            if ip_address:
                print(f"🌐 IP: {ip_address}")
            if system_pc:
                print(f"💻 Система: {system_pc}")
            if local_name_pc:
                print(f"🏠 Локальное имя: {local_name_pc}")
            print(f"📅 Создан: {server.created_at}")
            print("=" * 50)
            print("\n⚠️  СОХРАНИТЕ API КЛЮЧ! Он понадобится для настройки мониторинга.")
            print("Используйте его в заголовке X-API-Key для запросов к API\n")
        
        # Дополнительные опции
        print("\n📋 ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ:")
        print("1. Показать все серверы")
        print("2. Удалить сервер")
        print("3. Вернуться в главное меню")
        
        action = input("Выберите действие (1-3): ").strip()
        
        if action == '1':
            show_all_servers()
        elif action == '2':
            delete_server(server_name)
        elif action == '3':
            return
        
    except Exception as e:
        print(f"\n❌ Ошибка при генерации API токена: {e}")
        import traceback
        traceback.print_exc()
        print("\nУбедитесь, что:")
        print("1. Django проект настроен правильно")
        print("2. Модель Server существует в server/models.py")
        print("3. Выполнены миграции базы данных")
        print("4. Файл настроек находится в config/settings.py")

def show_all_servers():
    """Показать все зарегистрированные серверы"""
    try:
        init_django()
        
        from server.models import Server
        
        servers = Server.objects.all().order_by('-created_at')
        
        if not servers:
            print("\n📭 Нет зарегистрированных серверов")
            return
        
        print("\n" + "=" * 60)
        print("📋 СПИСОК ВСЕХ СЕРВЕРОВ")
        print("=" * 60)
        
        for i, server in enumerate(servers, 1):
            print(f"\n{i}. 📌 {server.name}")
            print(f"   🆔 ID: {server.id}")
            print(f"   🔑 UUID: {server.uuid}")
            print(f"   🔐 API Key: {server.api_key[:20]}...")
            if server.ip:
                print(f"   🌐 IP: {server.ip}")
            if server.SystemPC:
                print(f"   💻 Система: {server.SystemPC}")
            print(f"   📅 Создан: {server.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
        
        print(f"\n📊 Всего серверов: {servers.count()}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def delete_server(server_name=None):
    """Удалить сервер"""
    try:
        init_django()
        
        from server.models import Server
        
        if not server_name:
            server_name = input("Введите имя сервера для удаления: ").strip()
        
        if not server_name:
            print("❌ Имя сервера не указано")
            return
        
        try:
            server = Server.objects.get(name=server_name)
            
            print(f"\n⚠️  ВНИМАНИЕ! Вы собираетесь удалить сервер:")
            print(f"   📌 Имя: {server.name}")
            print(f"   🆔 ID: {server.id}")
            print(f"   🔑 UUID: {server.uuid}")
            
            confirm = input(f"\nУдалить сервер '{server_name}'? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                server.delete()
                print(f"✅ Сервер '{server_name}' успешно удален!")
            else:
                print("❌ Удаление отменено")
                
        except Server.DoesNotExist:
            print(f"❌ Сервер с именем '{server_name}' не найден")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def run_all():
    """Запуск всех компонентов"""
    print("=" * 50)
    print("🚀 ЗАПУСК ВСЕХ КОМПОНЕНТОВ")
    print("=" * 50)
    
    processes = []
    
    # 1. Выполняем миграции
    run_migrations()
    
    # 2. Запускаем SSH монитор в фоне
    ssh_process = run_ssh_monitor()
    if ssh_process:
        processes.append(('SSH Monitor', ssh_process))
        print("✅ SSH монитор запущен")
    
    # 3. Запускаем Django сервер
    django_process = run_django_server()
    if django_process:
        processes.append(('Django Server', django_process))
        print("✅ Django сервер запущен")
    
    print(f"\n✅ Запущено {len(processes)} сервисов")
    print("Нажмите Ctrl+C для остановки всех сервисов\n")
    
    # Ждем завершения
    try:
        for name, process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Остановка всех сервисов...")
        for name, process in processes:
            print(f"Останавливаем {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ Все сервисы остановлены")

def show_menu():
    """Показать меню выбора"""
    print("\n" + "=" * 50)
    print("📋 ГЛАВНОЕ МЕНЮ")
    print("=" * 50)
    print("1. Запустить все (миграции + SSH + Django)")
    print("2. Запустить только SSH монитор")
    print("3. Запустить только Django с миграциями")
    print("4. Запустить только Django сервер")
    print("5. Запустить миграции + Django сервер")
    print("6. Запустить SSH монитор + Django сервер (без миграций)")
    print("7. 🔐 Сгенерировать API токен для сервера")
    print("8. 📋 Показать все серверы")
    print("9. 🗑️  Удалить сервер")
    print("0. Выход")
    print("=" * 50)

def main():
    """Главная функция"""
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Режим командной строки
        command = sys.argv[1]
        
        if command == 'all':
            run_all()
        elif command == 'ssh':
            log_file = sys.argv[2] if len(sys.argv) > 2 else '/var/log/auth.log'
            run_ssh_monitor(log_file)
        elif command == 'django':
            run_migrations()
            run_django_server()
        elif command == 'django-only':
            run_django_server()
        elif command == 'migrate':
            run_migrations()
        elif command == 'generate-token':
            generate_api_token()
        elif command == 'list-servers':
            show_all_servers()
        elif command == 'delete-server':
            server_name = sys.argv[2] if len(sys.argv) > 2 else None
            delete_server(server_name)
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды:")
            print("  all              - Запустить все компоненты")
            print("  ssh              - Запустить SSH монитор")
            print("  django           - Запустить Django с миграциями")
            print("  django-only      - Запустить только Django сервер")
            print("  migrate          - Выполнить миграции")
            print("  generate-token   - Сгенерировать API токен")
            print("  list-servers     - Показать все серверы")
            print("  delete-server    - Удалить сервер")
    else:
        # Интерактивный режим
        while True:
            show_menu()
            choice = input("Ваш выбор: ").strip()
            
            if choice == '1':
                run_all()
                break
            
            elif choice == '2':
                log_file = input("Путь к log файлу (Enter для /var/log/auth.log): ").strip()
                if not log_file:
                    log_file = '/var/log/auth.log'
                run_ssh_monitor(log_file)
                break
            
            elif choice == '3':
                run_migrations()
                run_django_server()
                break
            
            elif choice == '4':
                run_django_server()
                break
            
            elif choice == '5':
                run_migrations()
                run_django_server()
                break
            
            elif choice == '6':
                ssh_process = run_ssh_monitor()
                django_process = run_django_server()
                
                if ssh_process and django_process:
                    print("\n✅ Оба сервиса запущены")
                    print("Нажмите Ctrl+C для остановки")
                    try:
                        ssh_process.wait()
                        django_process.wait()
                    except KeyboardInterrupt:
                        print("\n🛑 Остановка...")
                        ssh_process.terminate()
                        django_process.terminate()
                break
            
            elif choice == '7':
                generate_api_token()
                # После генерации токена не выходим, показываем меню снова
                input("\nНажмите Enter для продолжения...")
            
            elif choice == '8':
                show_all_servers()
                input("\nНажмите Enter для продолжения...")
            
            elif choice == '9':
                delete_server()
                input("\nНажмите Enter для продолжения...")
            
            elif choice == '0':
                print("👋 До свидания!")
                break
            
            else:
                print("❌ Неверный выбор! Попробуйте снова.")

if __name__ == '__main__':
    main()
    