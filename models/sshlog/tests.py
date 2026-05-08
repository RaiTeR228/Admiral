# sshlog/tests.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import SSHLogEntry


class SSHLogEntryModelTest(TestCase):
    """Базовые тесты модели SSHLogEntry"""
    
    def setUp(self):
        """Подготовка данных"""
        self.log_data = {
            'UuidServer': 'server-001',
            'event_type': 'success',
            'username': 'root',
            'ip_address': '192.168.1.100',
            'raw_log': 'Accepted password for root from 192.168.1.100 port 22 ssh2'
        }
    
    def test_create_successful_login(self):
        """Тест создания записи об успешном входе"""
        log = SSHLogEntry.objects.create(**self.log_data)
        
        self.assertIsNotNone(log.id)
        self.assertEqual(log.UuidServer, 'server-001')
        self.assertEqual(log.event_type, 'success')
        self.assertEqual(log.username, 'root')
        self.assertEqual(log.ip_address, '192.168.1.100')
        self.assertIsNotNone(log.timestamp)
    
    def test_create_failed_login(self):
        """Тест создания записи о неудачном входе"""
        log = SSHLogEntry.objects.create(
            UuidServer='server-002',
            event_type='failed',
            username='user',
            ip_address='10.0.0.50',
            raw_log='Failed password for user from 10.0.0.50 port 22 ssh2'
        )
        
        self.assertEqual(log.event_type, 'failed')
        self.assertEqual(log.username, 'user')
    
    def test_timestamp_auto_set(self):
        """Тест автоматической установки timestamp"""
        before = timezone.now()
        log = SSHLogEntry.objects.create(
            UuidServer='server-003',
            event_type='success',
            username='admin',
            ip_address='192.168.1.1'
        )
        after = timezone.now()
        
        self.assertIsNotNone(log.timestamp)
        self.assertGreaterEqual(log.timestamp, before)
        self.assertLessEqual(log.timestamp, after)


class SSHLogEventTypesTest(TestCase):
    """Тесты типов событий"""
    
    def test_event_type_choices(self):
        """Тест доступных типов событий"""
        log_success = SSHLogEntry.objects.create(
            UuidServer='server-001',
            event_type='success',
            username='root',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log_success.get_event_type_display(), 'Успешный вход')
        
        log_failed = SSHLogEntry.objects.create(
            UuidServer='server-002',
            event_type='failed',
            username='hacker',
            ip_address='10.0.0.1'
        )
        self.assertEqual(log_failed.get_event_type_display(), 'Неудачная попытка')


class SSHLogFilterTest(TestCase):
    """Тесты фильтрации логов"""
    
    def setUp(self):
        """Создание тестовых данных"""
        self.log1 = SSHLogEntry.objects.create(
            UuidServer='server-1',
            event_type='success',
            username='admin',
            ip_address='192.168.1.100'
        )
        self.log2 = SSHLogEntry.objects.create(
            UuidServer='server-1',
            event_type='failed',
            username='attacker',
            ip_address='10.0.0.1'
        )
        self.log3 = SSHLogEntry.objects.create(
            UuidServer='server-2',
            event_type='success',
            username='user',
            ip_address='192.168.1.50'
        )
    
    def test_filter_by_uuid_server(self):
        """Тест фильтрации по серверу"""
        logs = SSHLogEntry.objects.filter(UuidServer='server-1')
        self.assertEqual(logs.count(), 2)
    
    def test_filter_by_event_type(self):
        """Тест фильтрации по типу события"""
        success_logs = SSHLogEntry.objects.filter(event_type='success')
        failed_logs = SSHLogEntry.objects.filter(event_type='failed')
        
        self.assertEqual(success_logs.count(), 2)
        self.assertEqual(failed_logs.count(), 1)
    
    def test_filter_by_username(self):
        """Тест фильтрации по имени пользователя"""
        admin_logs = SSHLogEntry.objects.filter(username='admin')
        self.assertEqual(admin_logs.count(), 1)
    
    def test_combined_filter(self):
        """Тест комбинированной фильтрации"""
        logs = SSHLogEntry.objects.filter(
            UuidServer='server-1',
            event_type='failed'
        )
        self.assertEqual(logs.count(), 1)
