import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        import django
        django.setup()
        
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        call_command('runserver', '127.0.0.1:8000')
        
    except ImportError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()