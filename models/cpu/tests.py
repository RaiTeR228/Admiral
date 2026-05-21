import pytest
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db

class TestCpuModel:
    """Базовые тесты модели Cpu"""
    
    @pytest.fixture
    def cpu_data(self):
        """Фикстура с данными для создания CPU"""
        return {
            'UuidServer': 'test-uuid-12345',
            'MAX_CPU_CORES': '8',
            'MAX_CPU_THREADS': '16',
            'CPU_NAME': 'Intel Core i7-9700K'
        }
    
    def test_create_cpu_with_all_fields(self, cpu_data):
        """Тест создания CPU с полной информацией"""
        from cpu.models import Cpu
        
        cpu = Cpu.objects.create(**cpu_data)
        
        assert cpu.id is not None
        assert cpu.UuidServer == 'test-uuid-12345'
        assert cpu.MAX_CPU_CORES == '8'
        assert cpu.MAX_CPU_THREADS == '16'
        assert cpu.CPU_NAME == 'Intel Core i7-9700K'
    
    def test_create_cpu_minimal(self):
        """Тест создания CPU только с обязательным полем"""
        from cpu.models import Cpu
        
        cpu = Cpu.objects.create(UuidServer='uuid-123')
        
        assert cpu.id is not None
        assert cpu.UuidServer == 'uuid-123'
        assert cpu.MAX_CPU_CORES is None
        assert cpu.MAX_CPU_THREADS is None
        assert cpu.CPU_NAME is None
    
    def test_update_cpu(self):
        """Тест обновления CPU"""
        from cpu.models import Cpu
        
        cpu = Cpu.objects.create(UuidServer='uuid-789')
        
        cpu.MAX_CPU_CORES = '16'
        cpu.MAX_CPU_THREADS = '32'
        cpu.CPU_NAME = 'AMD Ryzen 9'
        cpu.save()
        
        updated_cpu = Cpu.objects.get(id=cpu.id)
        assert updated_cpu.MAX_CPU_CORES == '16'
        assert updated_cpu.MAX_CPU_THREADS == '32'
        assert updated_cpu.CPU_NAME == 'AMD Ryzen 9'
    
    def test_delete_cpu(self):
        """Тест удаления CPU"""
        from cpu.models import Cpu
        
        cpu = Cpu.objects.create(UuidServer='uuid-delete')
        cpu_id = cpu.id
        
        cpu.delete()
        assert not Cpu.objects.filter(id=cpu_id).exists()


class TestCpuFilter:
    """Тесты фильтрации CPU"""
    
    @pytest.fixture
    def test_cpus(self):
        """Фикстура с тестовыми данными CPU"""
        from cpu.models import Cpu
        
        cpu1 = Cpu.objects.create(
            UuidServer='uuid-1',
            MAX_CPU_CORES='8',
            CPU_NAME='Intel i7'
        )
        cpu2 = Cpu.objects.create(
            UuidServer='uuid-2',
            MAX_CPU_CORES='16',
            CPU_NAME='AMD Ryzen'
        )
        cpu3 = Cpu.objects.create(
            UuidServer='uuid-1',
            MAX_CPU_CORES='4',
            CPU_NAME='Intel i5'
        )
        return [cpu1, cpu2, cpu3]
    
    def test_filter_by_uuid_server(self, test_cpus):
        """Тест фильтрации по UuidServer"""
        from cpu.models import Cpu
        
        cpus = Cpu.objects.filter(UuidServer='uuid-1')
        assert cpus.count() == 2
    
    def test_filter_by_cpu_name(self, test_cpus):
        """Тест фильтрации по названию CPU"""
        from cpu.models import Cpu
        
        cpus = Cpu.objects.filter(CPU_NAME='Intel i7')
        assert cpus.count() == 1
        assert cpus.first().MAX_CPU_CORES == '8'
    
    def test_count_cpu(self, test_cpus):
        """Тест подсчета CPU"""
        from cpu.models import Cpu
        
        count = Cpu.objects.count()
        assert count == 3


class TestCpuParameterized:
    """Параметризованные тесты CPU"""
    
    @pytest.mark.parametrize("uuid_server,cores,threads,name", [
        ('uuid-1', '4', '8', 'Intel i3'),
        ('uuid-2', '6', '12', 'Intel i5'),
        ('uuid-3', '8', '16', 'Intel i7'),
    ])
    def test_create_multiple_cpus(self, uuid_server, cores, threads, name):
        """Тест создания CPU с разными параметрами"""
        from cpu.models import Cpu
        
        cpu = Cpu.objects.create(
            UuidServer=uuid_server,
            MAX_CPU_CORES=cores,
            MAX_CPU_THREADS=threads,
            CPU_NAME=name
        )
        
        assert cpu.UuidServer == uuid_server
        assert cpu.MAX_CPU_CORES == cores
        assert cpu.MAX_CPU_THREADS == threads
        assert cpu.CPU_NAME == name