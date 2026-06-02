# tools/qrcode_generate.py
import io
import qrcode
import json
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Загружаем переменные из .env
load_dotenv()

def get_server_data_from_env() -> Dict[str, Any]:
    """
    Получает данные сервера из .env файла
    
    Returns:
        Dict с данными сервера
    """
    server_data = {
        "name": os.getenv("NAME_SERVER", "Мой сервер"),
        "ip": os.getenv("IP_ADDRESS", "127.0.0.1"),
        "port": int(os.getenv("PORT", "8000")),
        "api_token": os.getenv("API_TOKEN", ""),
        "protocol": os.getenv("PROTOCOL", "http"),
        "system_pc": os.getenv("SystemPC", "Unknown"),
        "local_name_pc": os.getenv("Local_Name_PC", "Unknown"),
        "server_uuid": os.getenv("SERVER_UUID", ""),
        "created_at": os.getenv("CREATED_AT", datetime.now().isoformat())
    }
    
    # Валидация обязательных полей
    if not server_data["api_token"]:
        raise ValueError("API_TOKEN не найден в .env файле!")
    
    if not server_data["ip"]:
        print("⚠️  Предупреждение: IP_ADDRESS не найден в .env, используется localhost")
        server_data["ip"] = "127.0.0.1"
    
    return server_data

def save_server_to_env(server_data: Dict[str, Any], env_path: Optional[Path] = None) -> None:
    """
    Сохраняет данные сервера в .env файл
    
    Args:
        server_data: Словарь с данными сервера
        env_path: Путь к .env файлу (по умолчанию в корне проекта)
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / '.env'
    
    # Читаем существующие переменные
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"\'')
    
    # Обновляем значения
    env_vars['NAME_SERVER'] = server_data.get('name', env_vars.get('NAME_SERVER', ''))
    env_vars['IP_ADDRESS'] = server_data.get('ip', env_vars.get('IP_ADDRESS', ''))
    env_vars['PORT'] = str(server_data.get('port', env_vars.get('PORT', '8000')))
    env_vars['API_TOKEN'] = server_data.get('api_token', env_vars.get('API_TOKEN', ''))
    env_vars['PROTOCOL'] = server_data.get('protocol', env_vars.get('PROTOCOL', 'http'))
    env_vars['SystemPC'] = server_data.get('system_pc', env_vars.get('SystemPC', ''))
    env_vars['Local_Name_PC'] = server_data.get('local_name_pc', env_vars.get('Local_Name_PC', ''))
    env_vars['SERVER_UUID'] = server_data.get('server_uuid', env_vars.get('SERVER_UUID', ''))
    env_vars['CREATED_AT'] = server_data.get('created_at', env_vars.get('CREATED_AT', datetime.now().isoformat()))
    
    # Сохраняем обратно
    with open(env_path, 'w') as f:
        # f.write("# Данные сервера для QR-кода\n")
        # f.write(f"# Обновлено: {datetime.now().isoformat()}\n\n")
        for key, value in env_vars.items():
            if value:
                # Экранируем кавычки и спецсимволы
                value_str = str(value).replace('"', '\\"')
                if ' ' in value_str or '"' in value_str or "'" in value_str:
                    f.write(f'{key}="{value_str}"\n')
                else:
                    f.write(f'{key}={value_str}\n')
    
    print(f"✅ Данные сервера сохранены в {env_path}")

def generate_qr_json(server_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Генерирует JSON для QR-кода (компактный формат)
    
    Args:
        server_data: Данные сервера (если не указаны, берутся из .env)
    
    Returns:
        Dict с JSON данными для QR-кода
    """
    if server_data is None:
        server_data = get_server_data_from_env()
    
    # Компактный формат для QR-кода (экономия места)
    qr_payload = {
        "v": 1,  # version
        "t": "sc",  # type: server_config
        "s": {
            "n": server_data.get('name'),  # name
            "i": server_data.get('ip'),     # ip
            "p": server_data.get('port'),   # port
            "k": server_data.get('api_token'),  # api_key
            "r": server_data.get('protocol', 'http'),  # protocol
            "sys": server_data.get('system_pc'),  # system
            "local": server_data.get('local_name_pc'),  # local_name
            "u": server_data.get('server_uuid')  # uuid
        }
    }
    
    return qr_payload

def generate_qr_code_ascii(server_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Генерирует QR-код в ASCII формате для отображения в терминале
    
    Args:
        server_data: Данные сервера (если не указаны, берутся из .env)
    
    Returns:
        str: ASCII представление QR-кода
    """
    qr_payload = generate_qr_json(server_data)
    json_string = json.dumps(qr_payload, separators=(',', ':'))
    
    # Создаем QR-код
    qr = qrcode.QRCode(
        box_size=10, border=4, version=1,
        # version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M
    )
    qr.add_data(json_string)
    qr.make(fit=True)
    
    # Генерируем ASCII представление
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    
    return f.read()

def generate_qr_code_image(server_data: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> bytes:
    """
    Генерирует QR-код как изображение
    
    Args:
        server_data: Данные сервера (если не указаны, берутся из .env)
        output_path: Путь для сохранения изображения (опционально)
    
    Returns:
        bytes: PNG изображение QR-кода
    """
    qr_payload = generate_qr_json(server_data)
    json_string = json.dumps(qr_payload, separators=(',', ':'))
    
    qr = qrcode.QRCode(
        box_size=10,
        border=4,
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M
    )
    qr.add_data(json_string)
    qr.make(fit=True)
    
    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")
    
    if output_path:
        img.save(output_path)
        print(f"✅ QR-код сохранен как {output_path}")
    
    # Возвращаем байты для отправки через API
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

def generate_qr_code(server_data: Optional[Dict[str, Any]] = None, save_image: bool = True):
    """
    Основная функция для генерации QR-кода (совместимость со старым кодом)
    
    Args:
        server_data: Данные сервера (если не указаны, берутся из .env)
        save_image: Сохранить ли изображение QR-кода
    """
    try:
        if server_data is None:
            server_data = get_server_data_from_env()
        
        # print("\n" + "=" * 60)
        print("ГЕНЕРАЦИЯ QR-КОДА ДЛЯ ПОДКЛЮЧЕНИЯ")
        print("=" * 60)
        
        qr_ascii = generate_qr_code_ascii(server_data)
        print(qr_ascii)
        
        if save_image:
            # Сохраняем QR-код как изображение
            qr_filename = f"qr_server_{server_data.get('name', 'server').replace(' ', '_')}.png"
            qr_path = Path(__file__).parent.parent / qr_filename
            generate_qr_code_image(server_data, output_path=str(qr_path))

        print("=" * 60)
        
        # Показываем JSON для отладки
        print("\n📋 JSON данные в QR-коде (для разработчика):")
        qr_json = generate_qr_json(server_data)
        print(json.dumps(qr_json, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Ошибка при генерации QR-кода: {e}")
        import traceback
        traceback.print_exc()

# Для обратной совместимости со старым кодом
def generate_qr_code_legacy():
    """Старая функция для генерации QR-кода только с API ключом"""
    API_KEY = os.getenv("API_TOKEN")
    if not API_KEY:
        print("❌ API_TOKEN не найден в .env файле!")
        return
    
    qr = qrcode.QRCode(box_size=10, border=4, version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(API_KEY)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())
    print("\n\n⚠️  Это старый формат QR-кода (только API ключ)")
    print("Рекомендуется использовать новый формат с полными данными сервера\n\n")