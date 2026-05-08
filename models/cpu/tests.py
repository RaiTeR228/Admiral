# cpu/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Cpu


class CpuModelTest(TestCase):
    """Базовые тесты модели Cpu"""
    
    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.cpu_data = {
            'UuidServer': 'test-uuid-12345',
            'MAX_CPU_CORES': '8',
            'MAX_CPU_THREADS': '16',
            'CPU_NAME': 'Intel Core i7-9700K'
        }
    
    def test_create_cpu_with_all_fields(self):
        """Тест создания CPU с полной информацией"""
        cpu = Cpu.objects.create(**self.cpu_data)
        
        self.assertIsNotNone(cpu.id)
        self.assertEqual(cpu.UuidServer, 'test-uuid-12345')
        self.assertEqual(cpu.MAX_CPU_CORES, '8')
        self.assertEqual(cpu.MAX_CPU_THREADS, '16')
        self.assertEqual(cpu.CPU_NAME, 'Intel Core i7-9700K')
    
    def test_create_cpu_minimal(self):
        """Тест создания CPU только с обязательным полем"""
        cpu = Cpu.objects.create(UuidServer='uuid-123')
        
        self.assertIsNotNone(cpu.id)
        self.assertEqual(cpu.UuidServer, 'uuid-123')
        self.assertIsNone(cpu.MAX_CPU_CORES)
        self.assertIsNone(cpu.MAX_CPU_THREADS)
        self.assertIsNone(cpu.CPU_NAME)
    
    def test_update_cpu(self):
        """Тест обновления CPU"""
        cpu = Cpu.objects.create(UuidServer='uuid-789')
        
        cpu.MAX_CPU_CORES = '16'
        cpu.MAX_CPU_THREADS = '32'
        cpu.CPU_NAME = 'AMD Ryzen 9'
        cpu.save()
        
        updated_cpu = Cpu.objects.get(id=cpu.id)
        self.assertEqual(updated_cpu.MAX_CPU_CORES, '16')
        self.assertEqual(updated_cpu.MAX_CPU_THREADS, '32')
        self.assertEqual(updated_cpu.CPU_NAME, 'AMD Ryzen 9')
    
    def test_delete_cpu(self):
        """Тест удаления CPU"""
        cpu = Cpu.objects.create(UuidServer='uuid-delete')
        cpu_id = cpu.id
        
        cpu.delete()
        self.assertFalse(Cpu.objects.filter(id=cpu_id).exists())


class CpuFilterTest(TestCase):
    """Тесты фильтрации CPU"""
    
    def setUp(self):
        """Создание тестовых данных"""
        self.cpu1 = Cpu.objects.create(
            UuidServer='uuid-1',
            MAX_CPU_CORES='8',
            CPU_NAME='Intel i7'
        )
        self.cpu2 = Cpu.objects.create(
            UuidServer='uuid-2',
            MAX_CPU_CORES='16',
            CPU_NAME='AMD Ryzen'
        )
        self.cpu3 = Cpu.objects.create(
            UuidServer='uuid-1',
            MAX_CPU_CORES='4',
            CPU_NAME='Intel i5'
        )
    
    def test_filter_by_uuid_server(self):
        """Тест фильтрации по UuidServer"""
        cpus = Cpu.objects.filter(UuidServer='uuid-1')
        self.assertEqual(cpus.count(), 2)
    
    def test_filter_by_cpu_name(self):
        """Тест фильтрации по названию CPU"""
        cpus = Cpu.objects.filter(CPU_NAME='Intel i7')
        self.assertEqual(cpus.count(), 1)
        self.assertEqual(cpus.first().MAX_CPU_CORES, '8')
    
    def test_count_cpu(self):
        """Тест подсчета CPU"""
        count = Cpu.objects.count()
        self.assertEqual(count, 3)
