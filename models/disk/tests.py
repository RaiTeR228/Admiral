# disk/tests.py
from django.test import TestCase
from .models import Disk


class DiskModelTest(TestCase):
    """Базовые тесты модели Disk"""
    
    def setUp(self):
        """Подготовка данных"""
        self.disk_data = {
            'UuidServer': 'server-uuid-001',
            'MAX_SWAP': '8192',
            'MAX_DISK': '1048576',
            'DISK_NAME': 'sda'
        }
    
    def test_create_disk_full(self):
        """Тест создания диска со всеми полями"""
        disk = Disk.objects.create(**self.disk_data)
        
        self.assertIsNotNone(disk.id)
        self.assertEqual(disk.UuidServer, 'server-uuid-001')
        self.assertEqual(disk.MAX_SWAP, '8192')
        self.assertEqual(disk.MAX_DISK, '1048576')
        self.assertEqual(disk.DISK_NAME, 'sda')
    
    def test_create_disk_minimal(self):
        """Тест создания диска только с UUID"""
        disk = Disk.objects.create(UuidServer='uuid-minimal')
        
        self.assertEqual(disk.UuidServer, 'uuid-minimal')
        self.assertIsNone(disk.MAX_SWAP)
        self.assertIsNone(disk.MAX_DISK)
        self.assertIsNone(disk.DISK_NAME)
    
    def test_multiple_disks_per_server(self):
        """Тест нескольких дисков на одном сервере"""
        uuid_server = 'server-001'
        
        disk1 = Disk.objects.create(
            UuidServer=uuid_server,
            DISK_NAME='sda',
            MAX_DISK='500000'
        )
        disk2 = Disk.objects.create(
            UuidServer=uuid_server,
            DISK_NAME='sdb',
            MAX_DISK='1000000'
        )
        
        disks = Disk.objects.filter(UuidServer=uuid_server)
        self.assertEqual(disks.count(), 2)
    
    def test_update_disk(self):
        """Тест обновления диска"""
        disk = Disk.objects.create(UuidServer='uuid-upd')
        
        disk.MAX_SWAP = '16384'
        disk.MAX_DISK = '2097152'
        disk.DISK_NAME = 'nvme0n1'
        disk.save()
        
        updated = Disk.objects.get(id=disk.id)
        self.assertEqual(updated.MAX_SWAP, '16384')
        self.assertEqual(updated.MAX_DISK, '2097152')
        self.assertEqual(updated.DISK_NAME, 'nvme0n1')


class DiskFilterTest(TestCase):
    """Тесты фильтрации"""
    
    def setUp(self):
        """Создание тестовых данных"""
        self.disk1 = Disk.objects.create(
            UuidServer='server-1',
            DISK_NAME='sda',
            MAX_DISK='500000'
        )
        self.disk2 = Disk.objects.create(
            UuidServer='server-1',
            DISK_NAME='sdb',
            MAX_DISK='1000000'
        )
        self.disk3 = Disk.objects.create(
            UuidServer='server-2',
            DISK_NAME='nvme0n1',
            MAX_DISK='2000000'
        )
    
    def test_filter_by_uuid_server(self):
        """Тест фильтрации по серверу"""
        disks = Disk.objects.filter(UuidServer='server-1')
        self.assertEqual(disks.count(), 2)
    
    def test_filter_by_disk_name(self):
        """Тест фильтрации по названию диска"""
        disks = Disk.objects.filter(DISK_NAME='sda')
        self.assertEqual(disks.count(), 1)
        self.assertEqual(disks.first().UuidServer, 'server-1')
    
    def test_count_disks_per_server(self):
        """Тест подсчета дисков"""
        count_s1 = Disk.objects.filter(UuidServer='server-1').count()
        count_s2 = Disk.objects.filter(UuidServer='server-2').count()
        
        self.assertEqual(count_s1, 2)
        self.assertEqual(count_s2, 1)
