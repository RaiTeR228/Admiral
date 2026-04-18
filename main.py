import os
import sys

def main():
    # ПРАВИЛЬНЫЙ путь - с двумя config
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        import django
        django.setup()
        
        from django.core.management import call_command
        
        print("✅ Django инициализирован")
        print("🔄 Применяю миграции...")
        call_command('migrate', interactive=False)
        
        print("🚀 Запускаю сервер на http://127.0.0.1:8000")
        call_command('runserver', '127.0.0.1:8000')
        
    except ImportError as e:
        print(f"❌ Ошибка: {e}")
        print(f"Путь к настройкам: config.settings")
        sys.exit(1)

if __name__ == '__main__':
    main()