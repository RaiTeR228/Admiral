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

def run_django_server(host='0.0.0.0', port='8000'):
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
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: all, ssh, django, django-only, migrate")
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
            
            elif choice == '0':
                print("👋 До свидания!")
                break
            
            else:
                print("❌ Неверный выбор! Попробуйте снова.")

if __name__ == '__main__':
    main()