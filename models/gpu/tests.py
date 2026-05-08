# gpu/tests.py
from django.test import TestCase
from .models import gpu


class GpuModelTest(TestCase):
    """Базовые тесты модели gpu"""
    
    def setUp(self):
        """Подготовка данных"""
        self.gpu_data = {
            'UuidServer': 'server-gpu-001',
            'MAX_GPU_THREADS': '5120',
            'GPU_NAME': 'NVIDIA RTX 3080',
            'GPU_SIZE_GB': '10'
        }
    
    def test_create_gpu_full(self):
        """Тест создания GPU со всеми полями"""
        gpu_obj = gpu.objects.create(**self.gpu_data)
        
        self.assertIsNotNone(gpu_obj.id)
        self.assertEqual(gpu_obj.UuidServer, 'server-gpu-001')
        self.assertEqual(gpu_obj.MAX_GPU_THREADS, '5120')
        self.assertEqual(gpu_obj.GPU_NAME, 'NVIDIA RTX 3080')
        self.assertEqual(gpu_obj.GPU_SIZE_GB, '10')
    
    def test_create_gpu_minimal(self):
        """Тест создания GPU только с UUID"""
        gpu_obj = gpu.objects.create(UuidServer='uuid-minimal')
        
        self.assertEqual(gpu_obj.UuidServer, 'uuid-minimal')
        self.assertIsNone(gpu_obj.MAX_GPU_THREADS)
        self.assertIsNone(gpu_obj.GPU_NAME)
        self.assertIsNone(gpu_obj.GPU_SIZE_GB)
    
    def test_create_multiple_gpus_per_server(self):
        """Тест нескольких GPU на одном сервере"""
        uuid_server = 'server-multi-gpu'
        
        gpu1 = gpu.objects.create(
            UuidServer=uuid_server,
            GPU_NAME='NVIDIA RTX 3080',
            MAX_GPU_THREADS='5120',
            GPU_SIZE_GB='10'
        )
        gpu2 = gpu.objects.create(
            UuidServer=uuid_server,
            GPU_NAME='NVIDIA RTX 3090',
            MAX_GPU_THREADS='10496',
            GPU_SIZE_GB='24'
        )
        
        gpus = gpu.objects.filter(UuidServer=uuid_server)
        self.assertEqual(gpus.count(), 2)
    
    def test_update_gpu(self):
        """Тест обновления GPU"""
        gpu_obj = gpu.objects.create(UuidServer='uuid-upd')
        
        gpu_obj.GPU_NAME = 'NVIDIA RTX 4090'
        gpu_obj.MAX_GPU_THREADS = '16384'
        gpu_obj.GPU_SIZE_GB = '24'
        gpu_obj.save()
        
        updated = gpu.objects.get(id=gpu_obj.id)
        self.assertEqual(updated.GPU_NAME, 'NVIDIA RTX 4090')
        self.assertEqual(updated.MAX_GPU_THREADS, '16384')
        self.assertEqual(updated.GPU_SIZE_GB, '24')


class GpuFilterTest(TestCase):
    """Тесты фильтрации"""
    
    def setUp(self):
        """Создание тестовых данных"""
        self.gpu1 = gpu.objects.create(
            UuidServer='server-1',
            GPU_NAME='RTX 3080',
            GPU_SIZE_GB='10'
        )
        self.gpu2 = gpu.objects.create(
            UuidServer='server-2',
            GPU_NAME='RTX 3090',
            GPU_SIZE_GB='24'
        )
        self.gpu3 = gpu.objects.create(
            UuidServer='server-1',
            GPU_NAME='RTX 4090',
            GPU_SIZE_GB='24'
        )
    
    def test_filter_by_uuid_server(self):
        """Тест фильтрации по серверу"""
        gpus = gpu.objects.filter(UuidServer='server-1')
        self.assertEqual(gpus.count(), 2)
    
    def test_filter_by_gpu_name(self):
        """Тест фильтрации по названию"""
        gpus = gpu.objects.filter(GPU_NAME='RTX 3090')
        self.assertEqual(gpus.count(), 1)
    
    def test_filter_by_memory_size(self):
        """Тест фильтрации по объему памяти"""
        gpus = gpu.objects.filter(GPU_SIZE_GB='24')
        self.assertEqual(gpus.count(), 2)
