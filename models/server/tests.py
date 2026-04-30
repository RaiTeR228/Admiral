# server/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DataError
from django.utils import timezone
from django.db import connection
from .models import Server
import uuid
from datetime import timedelta

class ServerModelTest(TestCase):
    """Базовые тесты модели Server"""
    
    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.server_data = {
            'name': 'Test Server',
            'api_key': 'test_api_key_12345',
            'ip': '192.168.1.100',
            'SystemPC': 'Ubuntu 20.04',
            'Local_Name_PC': 'test-pc-01'
        }
    
    def test_create_server(self):
        """Тест создания сервера со всеми полями"""
        server = Server.objects.create(**self.server_data)
        
        self.assertIsNotNone(server.id)
        self.assertIsInstance(server.uuid, uuid.UUID)
        self.assertEqual(server.name, 'Test Server')
        self.assertEqual(server.api_key, 'test_api_key_12345')
        self.assertEqual(server.ip, '192.168.1.100')
        self.assertEqual(server.SystemPC, 'Ubuntu 20.04')
        self.assertEqual(server.Local_Name_PC, 'test-pc-01')
        self.assertIsNotNone(server.created_at)
    
    def test_create_server_minimal_fields(self):
        """Тест создания сервера только с обязательными полями"""
        server = Server.objects.create(
            name='Minimal Server',
            api_key='minimal_key'
        )
        
        self.assertIsNotNone(server.id)
        self.assertIsNotNone(server.uuid)
        self.assertEqual(server.name, 'Minimal Server')
        self.assertEqual(server.api_key, 'minimal_key')
        self.assertIsNone(server.ip)
        self.assertIsNone(server.SystemPC)
        self.assertIsNone(server.Local_Name_PC)
    
    def test_uuid_auto_generation(self):
        """Тест автоматической генерации UUID"""
        server1 = Server.objects.create(name='Server 1', api_key='key1')
        server2 = Server.objects.create(name='Server 2', api_key='key2')
        
        self.assertIsNotNone(server1.uuid)
        self.assertIsNotNone(server2.uuid)
        self.assertNotEqual(server1.uuid, server2.uuid)
        self.assertIsInstance(server1.uuid, uuid.UUID)
    
    def test_uuid_uniqueness(self):
        """Тест уникальности UUID"""
        server1 = Server.objects.create(name='Server 1', api_key='key1')
        server2 = Server.objects.create(name='Server 2', api_key='key2')
        
        # UUID должны быть разными
        self.assertNotEqual(server1.uuid, server2.uuid)
        
        # Попытка создать сервер с таким же UUID должна вызвать ошибку
        with self.assertRaises(IntegrityError):
            Server.objects.create(
                name='Server 3',
                api_key='key3',
                uuid=server1.uuid
            )
    
    def test_created_at_auto_now_add(self):
        """Тест автоматической установки даты создания"""
        server = Server.objects.create(name='Test', api_key='key')
        
        self.assertIsNotNone(server.created_at)
        self.assertLessEqual(server.created_at, timezone.now())
        
        # Проверяем, что created_at не меняется при обновлении
        original_created_at = server.created_at
        server.name = 'Updated Name'
        server.save()
        server.refresh_from_db()
        
        self.assertEqual(server.created_at, original_created_at)
    
    def test_string_representation(self):
        """Тест строкового представления модели"""
        server = Server.objects.create(name='My Server', api_key='key')
        self.assertEqual(str(server), 'My Server')
        
        server2 = Server.objects.create(name='Another Server', api_key='key2')
        self.assertEqual(str(server2), 'Another Server')
    
    def test_name_max_length(self):
        """Тест максимальной длины поля name"""
        # Проверяем, что имя длиной 255 символов сохраняется
        long_name = 'A' * 255
        server = Server.objects.create(name=long_name, api_key='key')
        self.assertEqual(server.name, long_name)
        self.assertEqual(len(server.name), 255)
        
        # Проверяем, что имя короче 255 символов сохраняется
        short_name = 'Short Name'
        server2 = Server.objects.create(name=short_name, api_key='key2')
        self.assertEqual(server2.name, short_name)
        
        # Django не выбрасывает исключение при длине > max_length на уровне модели
        # Вместо этого БД может обрезать строку или выбросить ошибку
        # Проверяем, что при попытке сохранить слишком длинное имя,
        # либо выбрасывается исключение, либо строка обрезается
        too_long_name = 'A' * 300
        
        try:
            server3 = Server.objects.create(name=too_long_name, api_key='key3')
            # Если исключение не выброшено, проверяем что строка была обрезана
            self.assertLessEqual(len(server3.name), 255)
        except (DataError, IntegrityError):
            # Исключение выброшено - это тоже приемлемо
            pass
    
    def test_api_key_max_length(self):
        """Тест максимальной длины поля api_key"""
        # Проверяем, что ключ длиной 255 символов сохраняется
        long_key = 'B' * 255
        server = Server.objects.create(name='Test', api_key=long_key)
        self.assertEqual(server.api_key, long_key)
        self.assertEqual(len(server.api_key), 255)
        
        # Проверяем нормальный ключ
        normal_key = 'normal_key_123'
        server2 = Server.objects.create(name='Test2', api_key=normal_key)
        self.assertEqual(server2.api_key, normal_key)
        
        # Проверяем слишком длинный ключ
        too_long_key = 'C' * 300
        
        try:
            server3 = Server.objects.create(name='Test3', api_key=too_long_key)
            # Если исключение не выброшено, проверяем обрезание
            self.assertLessEqual(len(server3.api_key), 255)
        except (DataError, IntegrityError):
            # Исключение выброшено - приемлемо
            pass
    
    def test_name_max_length_validation(self):
        """Тест валидации максимальной длины name через full_clean"""
        # Создаем сервер без сохранения
        server = Server(name='A' * 300, api_key='key')
        
        # full_clean должен выбросить ValidationError
        with self.assertRaises(ValidationError):
            server.full_clean()
    
    def test_api_key_max_length_validation(self):
        """Тест валидации максимальной длины api_key через full_clean"""
        # Создаем сервер без сохранения
        server = Server(name='Test', api_key='B' * 300)
        
        # full_clean должен выбросить ValidationError
        with self.assertRaises(ValidationError):
            server.full_clean()
    
    def test_ip_address_validation(self):
        """Тест валидации IP адресов"""
        # IPv4
        server_ipv4 = Server.objects.create(
            name='IPv4 Server',
            api_key='key',
            ip='192.168.1.1'
        )
        self.assertEqual(server_ipv4.ip, '192.168.1.1')
        
        # IPv6
        server_ipv6 = Server.objects.create(
            name='IPv6 Server',
            api_key='key',
            ip='2001:0db8:85a3:0000:0000:8a2e:0370:7334'
        )
        self.assertEqual(server_ipv6.ip, '2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        
        # localhost
        server_localhost = Server.objects.create(
            name='Localhost',
            api_key='key',
            ip='127.0.0.1'
        )
        self.assertEqual(server_localhost.ip, '127.0.0.1')
        
        # Null IP
        server_null_ip = Server.objects.create(
            name='No IP',
            api_key='key',
            ip=None
        )
        self.assertIsNone(server_null_ip.ip)
        
        # Невалидный IP должен вызвать ошибку
        with self.assertRaises(ValidationError):
            server = Server(name='Invalid IP', api_key='key', ip='invalid_ip')
            server.full_clean()
    
    def test_update_server(self):
        """Тест обновления сервера"""
        server = Server.objects.create(
            name='Original Name',
            api_key='original_key'
        )
        
        # Обновляем поля
        server.name = 'Updated Name'
        server.api_key = 'updated_key'
        server.ip = '10.0.0.1'
        server.SystemPC = 'Windows 10'
        server.Local_Name_PC = 'updated-pc'
        server.save()
        
        # Получаем свежие данные из БД
        updated_server = Server.objects.get(id=server.id)
        
        self.assertEqual(updated_server.name, 'Updated Name')
        self.assertEqual(updated_server.api_key, 'updated_key')
        self.assertEqual(updated_server.ip, '10.0.0.1')
        self.assertEqual(updated_server.SystemPC, 'Windows 10')
        self.assertEqual(updated_server.Local_Name_PC, 'updated-pc')


class ServerModelFieldValidationTest(TestCase):
    """Тесты валидации полей модели"""
    
    def test_name_cannot_be_null(self):
        """Тест: name не может быть null"""
        with self.assertRaises(IntegrityError):
            Server.objects.create(name=None, api_key='key')
    
    def test_api_key_cannot_be_null(self):
        """Тест: api_key не может быть null"""
        with self.assertRaises(IntegrityError):
            Server.objects.create(name='Test', api_key=None)
    
    def test_max_length_validation_with_form(self):
        """Тест валидации max_length"""
        server = Server()
        
        # Устанавливаем слишком длинные значения
        server.name = 'A' * 300
        server.api_key = 'B' * 300
        
        # Проверяем валидацию
        with self.assertRaises(ValidationError) as cm:
            server.full_clean()
        
        # Проверяем, что ошибки валидации содержат нужные поля
        self.assertIn('name', cm.exception.message_dict)
        self.assertIn('api_key', cm.exception.message_dict)


class ServerQueryTest(TestCase):
    """Тесты запросов к модели Server"""
    
    def setUp(self):
        """Создаем тестовые данные"""
        self.servers = [
            Server.objects.create(name='Server 1', api_key='key1', ip='192.168.1.1'),
            Server.objects.create(name='Server 2', api_key='key2', ip='192.168.1.2'),
            Server.objects.create(name='Server 3', api_key='key3', ip='10.0.0.1'),
            Server.objects.create(name='Server 4', api_key='key4', ip=None),
        ]
    
    def test_filter_by_name(self):
        """Тест фильтрации по имени"""
        server = Server.objects.filter(name='Server 1').first()
        self.assertIsNotNone(server)
        self.assertEqual(server.name, 'Server 1')
        self.assertEqual(server.api_key, 'key1')
    
    def test_filter_by_ip(self):
        """Тест фильтрации по IP"""
        servers = Server.objects.filter(ip='192.168.1.1')
        self.assertEqual(servers.count(), 1)
        self.assertEqual(servers.first().name, 'Server 1')
        
        # Фильтрация по subnet
        servers_192 = Server.objects.filter(ip__startswith='192.168')
        self.assertEqual(servers_192.count(), 2)
    
    def test_filter_by_null_ip(self):
        """Тест фильтрации серверов без IP"""
        servers_without_ip = Server.objects.filter(ip__isnull=True)
        self.assertEqual(servers_without_ip.count(), 1)
        self.assertEqual(servers_without_ip.first().name, 'Server 4')
    
    def test_order_by_created_at(self):
        """Тест сортировки по дате создания"""
        import time
        time.sleep(0.01)
        
        server_new = Server.objects.create(name='New Server', api_key='new_key')
        
        servers_ordered = Server.objects.order_by('-created_at')
        self.assertEqual(servers_ordered.first().name, 'New Server')
    
    def test_exclude_query(self):
        """Тест исключения из запроса"""
        servers = Server.objects.exclude(ip__isnull=True)
        self.assertEqual(servers.count(), 3)
        
        servers = Server.objects.exclude(name__contains='Server 1')
        self.assertEqual(servers.count(), 3)
    
    def test_count_servers(self):
        """Тест подсчета серверов"""
        count = Server.objects.count()
        self.assertEqual(count, 4)
        
        # Добавляем еще один
        Server.objects.create(name='Server 5', api_key='key5')
        self.assertEqual(Server.objects.count(), 5)


class ServerAPITest(TestCase):
    """Тесты API ключей и уникальности"""
    
    def test_unique_api_keys_not_required(self):
        """Тест: API ключи НЕ обязаны быть уникальными"""
        server1 = Server.objects.create(name='Server 1', api_key='same_key')
        server2 = Server.objects.create(name='Server 2', api_key='same_key')
        
        self.assertEqual(server1.api_key, server2.api_key)
        self.assertNotEqual(server1.id, server2.id)
    
    def test_unique_names_not_required(self):
        """Тест: имена НЕ обязаны быть уникальными"""
        server1 = Server.objects.create(name='Same Name', api_key='key1')
        server2 = Server.objects.create(name='Same Name', api_key='key2')
        
        self.assertEqual(server1.name, server2.name)
        self.assertNotEqual(server1.id, server2.id)
        self.assertNotEqual(server1.uuid, server2.uuid)
    
    def test_long_api_key(self):
        """Тест длинных API ключей"""
        import secrets
        long_key = secrets.token_hex(64)  # 128 символов
        server = Server.objects.create(name='Secure Server', api_key=long_key)
        
        self.assertEqual(len(server.api_key), 128)
        self.assertEqual(server.api_key, long_key)
    
    def test_multiple_servers_same_ip(self):
        """Тест: несколько серверов могут иметь одинаковый IP"""
        server1 = Server.objects.create(name='Server 1', api_key='key1', ip='192.168.1.1')
        server2 = Server.objects.create(name='Server 2', api_key='key2', ip='192.168.1.1')
        
        self.assertEqual(server1.ip, server2.ip)
        self.assertNotEqual(server1.id, server2.id)


class ServerBulkOperationsTest(TestCase):
    """Тесты массовых операций с серверами"""
    
    def test_bulk_create(self):
        """Тест массового создания серверов"""
        servers_data = [
            Server(name=f'Bulk Server {i}', api_key=f'key_{i}')
            for i in range(10)
        ]
        
        created_servers = Server.objects.bulk_create(servers_data)
        self.assertEqual(len(created_servers), 10)
        self.assertEqual(Server.objects.count(), 10)
    
    def test_bulk_update(self):
        """Тест массового обновления"""
        # Создаем серверы
        servers = [
            Server.objects.create(name=f'Server {i}', api_key=f'key{i}')
            for i in range(5)
        ]
        
        # Массово обновляем IP
        for server in servers:
            server.ip = '10.0.0.1'
        
        Server.objects.bulk_update(servers, ['ip'])
        
        # Проверяем
        updated_servers = Server.objects.all()
        for server in updated_servers:
            self.assertEqual(server.ip, '10.0.0.1')
    
    def test_delete_all(self):
        """Тест удаления всех серверов"""
        # Создаем несколько серверов
        for i in range(5):
            Server.objects.create(name=f'Delete Server {i}', api_key=f'key{i}')
        
        self.assertEqual(Server.objects.count(), 5)
        
        # Удаляем все
        Server.objects.all().delete()
        self.assertEqual(Server.objects.count(), 0)


class ServerEdgeCasesTest(TestCase):
    """Тесты граничных случаев"""
    
    def test_empty_strings(self):
        """Тест пустых строк"""
        server = Server.objects.create(
            name='',  # Пустое имя
            api_key='key',
            SystemPC='',
            Local_Name_PC=''
        )
        
        self.assertEqual(server.name, '')
        self.assertEqual(server.SystemPC, '')
        self.assertEqual(server.Local_Name_PC, '')
    
    def test_special_characters_in_name(self):
        """Тест специальных символов в имени"""
        special_name = "Test-Server_123!@#$%^&*()"
        server = Server.objects.create(name=special_name, api_key='key')
        
        self.assertEqual(server.name, special_name)
    
    def test_unicode_characters(self):
        """Тест Unicode символов"""
        unicode_name = "Сервер-Тест-サーバー"
        server = Server.objects.create(name=unicode_name, api_key='key')
        
        self.assertEqual(server.name, unicode_name)
    
    def test_whitespace_in_fields(self):
        """Тест пробелов в полях"""
        whitespace_name = "  Server With Spaces  "
        server = Server.objects.create(name=whitespace_name, api_key='key')
        
        # Проверяем, что пробелы сохраняются
        self.assertEqual(server.name, whitespace_name)
        self.assertEqual(server.name.strip(), "Server With Spaces")
    
    def test_get_or_create(self):
        """Тест метода get_or_create"""
        # Создаем новый сервер
        server, created = Server.objects.get_or_create(
            name='Unique Server',
            defaults={'api_key': 'unique_key'}
        )
        self.assertTrue(created)
        self.assertEqual(server.name, 'Unique Server')
        
        # Получаем существующий
        server2, created2 = Server.objects.get_or_create(
            name='Unique Server',
            defaults={'api_key': 'another_key'}
        )
        self.assertFalse(created2)
        self.assertEqual(server2.id, server.id)
        self.assertEqual(server2.api_key, 'unique_key')  # Ключ не изменился


class ServerPerformanceTest(TestCase):
    """Тесты производительности (опционально)"""
    
    def test_large_number_of_servers(self):
        """Тест работы с большим количеством серверов"""
        import time
        
        # Создаем 1000 серверов
        start_time = time.time()
        
        servers = []
        for i in range(1000):
            servers.append(
                Server(name=f'Performance Server {i}', api_key=f'key_{i}')
            )
        
        Server.objects.bulk_create(servers)
        creation_time = time.time() - start_time
        
        print(f"\n✅ Создано 1000 серверов за {creation_time:.2f} секунд")
        
        # Проверяем количество
        self.assertEqual(Server.objects.count(), 1000)
        
        # Тест выборки
        start_time = time.time()
        all_servers = Server.objects.all()
        count = all_servers.count()
        query_time = time.time() - start_time
        
        print(f"✅ Выборка 1000 серверов за {query_time:.2f} секунд")
        self.assertEqual(count, 1000)