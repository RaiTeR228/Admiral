# ram/tests.py
from django.test import TestCase
from .models import Ram


class RamModelTest(TestCase):
    """Базовые тесты модели Ram"""
    
    def setUp(self):
        """Подготовка данных"""
        self.ram_data = {
            'UuidServer': 'server-uuid-001',
            'MAX_RAM': '16384'
        }
    
    def test_create_ram_full(self):
        """Тест создания записи RAM со всеми полями"""
        ram = Ram.objects.create(**self.ram_data)
        
        self.assertIsNotNone(ram.id)
        self.assertEqual(ram.UuidServer, 'server-uuid-001')
        self.assertEqual(ram.MAX_RAM, '16384')
    
    def test_create_ram_minimal(self):
        """Тест создания с минимальными данными"""
        ram = Ram.objects.create(UuidServer='uuid-min')
        
        self.assertEqual(ram.UuidServer, 'uuid-min')
        self.assertIsNone(ram.MAX_RAM)
    
    def test_create_ram_with_null_max_ram(self):
        """Тест создания с NULL MAX_RAM"""
        ram = Ram.objects.create(
            UuidServer='uuid-null',
            MAX_RAM=None
        )
        
        self.assertIsNone(ram.MAX_RAM)
    
    def test_update_ram(self):
        """Тест обновления RAM"""
        ram = Ram.objects.create(UuidServer='uuid-upd', MAX_RAM='8192')
        
        ram.MAX_RAM = '32768'
        ram.save()
        
        updated = Ram.objects.get(id=ram.id)
        self.assertEqual(updated.MAX_RAM, '32768')
    
    def test_delete_ram(self):
        """Тест удаления RAM"""
        ram = Ram.objects.create(UuidServer='uuid-delete')
        ram_id = ram.id
        
        ram.delete()
        self.assertFalse(Ram.objects.filter(id=ram_id).exists())


class RamMemorySizeTest(TestCase):
    """Тесты различных размеров памяти"""
    
    def test_ram_sizes(self):
        """Тест различных размеров RAM"""
        sizes = [
            ('512', 'RAM 512 MB'),
            ('1024', 'RAM 1 GB'),
            ('8192', 'RAM 8 GB'),
            ('16384', 'RAM 16 GB'),
            ('32768', 'RAM 32 GB'),
        ]
        
        for i, (size, description) in enumerate(sizes):
            ram = Ram.objects.create(
                UuidServer=f'server-{i}',
                MAX_RAM=size
            )
            self.assertEqual(ram.MAX_RAM, size)
    
    def test_very_large_ram(self):
        """Тест очень большого объема RAM"""
        large_ram = '1048576'
        ram = Ram.objects.create(
            UuidServer='uuid-large',
            MAX_RAM=large_ram
        )
        
        self.assertEqual(ram.MAX_RAM, large_ram)


class RamFilterTest(TestCase):
    """Тесты фильтрации"""
    
    def setUp(self):
        """Создание тестовых данных"""
        self.ram1 = Ram.objects.create(UuidServer='server-1', MAX_RAM='8192')
        self.ram2 = Ram.objects.create(UuidServer='server-2', MAX_RAM='16384')
        self.ram3 = Ram.objects.create(UuidServer='server-3', MAX_RAM='32768')
    
    def test_filter_by_uuid_server(self):
        """Тест фильтрации по UUID сервера"""
        rams = Ram.objects.filter(UuidServer='server-1')
        self.assertEqual(rams.count(), 1)
    
    def test_filter_by_max_ram(self):
        """Тест фильтрации по размеру"""
        rams = Ram.objects.filter(MAX_RAM='16384')
        self.assertEqual(rams.count(), 1)
        self.assertEqual(rams.first().UuidServer, 'server-2')
    
    def test_exclude_filter(self):
        """Тест исключения"""
        rams = Ram.objects.exclude(UuidServer='server-1')
        self.assertEqual(rams.count(), 2)
