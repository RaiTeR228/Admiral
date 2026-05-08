# metric/tests.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from server.models import Server
from .models import ServerStat


class ServerStatModelTest(TestCase):
    """Базовые тесты модели ServerStat"""
    
    def setUp(self):
        """Подготовка данных"""
        self.server = Server.objects.create(
            name='Test Server',
            api_key='test_key_123'
        )
        
        self.stat_data = {
            'server': self.server,
            'Use_Cpu': 45,
            'Use_Ram': 60,
            'Use_Swap': 10,
            'IO': 25.5
        }
    
    def test_create_server_stat_full(self):
        """Тест создания статистики со всеми полями"""
        stat = ServerStat.objects.create(**self.stat_data)
        
        self.assertIsNotNone(stat.id)
        self.assertEqual(stat.server, self.server)
        self.assertEqual(stat.Use_Cpu, 45)
        self.assertEqual(stat.Use_Ram, 60)
        self.assertEqual(stat.Use_Swap, 10)
        self.assertEqual(stat.IO, 25.5)
        self.assertIsNotNone(stat.created_at)
    
    def test_create_server_stat_minimal(self):
        """Тест создания статистики с минимальными данными"""
        stat = ServerStat.objects.create(server=self.server)
        
        self.assertEqual(stat.server, self.server)
        self.assertIsNone(stat.Use_Cpu)
        self.assertIsNone(stat.Use_Ram)
        self.assertIsNone(stat.Use_Swap)
        self.assertIsNone(stat.IO)
    
    def test_created_at_auto_set(self):
        """Тест автоматической установки created_at"""
        before = timezone.now()
        stat = ServerStat.objects.create(server=self.server)
        after = timezone.now()
        
        self.assertIsNotNone(stat.created_at)
        self.assertGreaterEqual(stat.created_at, before)
        self.assertLessEqual(stat.created_at, after)


class ServerStatFilterTest(TestCase):
    """Тесты фильтрации статистики"""
    
    def setUp(self):
        """Создание серверов и статистики"""
        self.server1 = Server.objects.create(name='Server 1', api_key='key1')
        self.server2 = Server.objects.create(name='Server 2', api_key='key2')
        
        self.stat1 = ServerStat.objects.create(
            server=self.server1,
            Use_Cpu=30,
            Use_Ram=50
        )
        self.stat2 = ServerStat.objects.create(
            server=self.server1,
            Use_Cpu=70,
            Use_Ram=80
        )
        self.stat3 = ServerStat.objects.create(
            server=self.server2,
            Use_Cpu=40,
            Use_Ram=60
        )
    
    def test_filter_by_server(self):
        """Тест фильтрации по серверу"""
        stats = ServerStat.objects.filter(server=self.server1)
        self.assertEqual(stats.count(), 2)
    
    def test_filter_by_cpu_usage(self):
        """Тест фильтрации по использованию CPU"""
        high_cpu = ServerStat.objects.filter(Use_Cpu__gte=70)
        self.assertEqual(high_cpu.count(), 1)
        
        low_cpu = ServerStat.objects.filter(Use_Cpu__lt=50)
        self.assertEqual(low_cpu.count(), 2)
    
    def test_combined_filter(self):
        """Тест комбинированной фильтрации"""
        stats = ServerStat.objects.filter(
            server=self.server1,
            Use_Cpu__gte=50
        )
        self.assertEqual(stats.count(), 1)
        self.assertEqual(stats.first().Use_Cpu, 70)


class ServerStatMetricsRangeTest(TestCase):
    """Тесты диапазонов значений метрик"""
    
    def setUp(self):
        """Создание тестового сервера"""
        self.server = Server.objects.create(
            name='Metrics Server',
            api_key='metrics_key'
        )
    
    def test_cpu_percentage_0_to_100(self):
        """Тест процентов CPU от 0 до 100"""
        cpu_values = [0, 25, 50, 75, 100]
        
        for cpu in cpu_values:
            stat = ServerStat.objects.create(
                server=self.server,
                Use_Cpu=cpu
            )
            self.assertEqual(stat.Use_Cpu, cpu)
            self.assertGreaterEqual(stat.Use_Cpu, 0)
            self.assertLessEqual(stat.Use_Cpu, 100)
