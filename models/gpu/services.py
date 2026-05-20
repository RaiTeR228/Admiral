# models/gpu/services.py
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import gpu
from server.models import Server
import logging
import re

logger = logging.getLogger(__name__)


class ServerAuthenticationService:
    """Сервис для аутентификации серверов по API ключу"""
    
    @staticmethod
    def authenticate_server(api_key):
        """
        Аутентификация сервера по API ключу.
        Возвращает (server, error_message)
        """
        if not api_key:
            return None, "API key required"
        
        try:
            server = Server.objects.get(api_key=api_key)
            return server, None
        except Server.DoesNotExist:
            return None, "Invalid API key"
    
    @staticmethod
    def extract_api_key_from_request(request):
        """Извлекает API ключ из заголовков запроса"""
        api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
        if not api_key:
            api_key = request.headers.get('X-API-Key', '')
        return api_key


class GPUDataValidationService:
    """Сервис для валидации данных GPU"""
    
    @staticmethod
    def validate_gpu_threads(threads_value):
        """
        Валидация количества потоков GPU
        """
        if threads_value is None:
            return None, None
        
        # Преобразуем в строку для обработки
        value_str = str(threads_value).strip()
        
        if not value_str:
            return None, None
        
        # Проверяем, что это число
        try:
            threads_int = int(value_str)
            
            # Бизнес-логика: проверка разумных пределов
            if threads_int < 0:
                return None, "GPU threads cannot be negative"
            elif threads_int == 0:
                return None, "GPU threads cannot be zero (no GPU?)"
            elif threads_int > 65536:  # Максимальное разумное количество потоков
                return None, f"Unusually high GPU threads count: {threads_int}"
            elif threads_int > 16384:
                logger.warning(f"High GPU thread count detected: {threads_int}")
            
            return threads_int, None
            
        except (ValueError, TypeError):
            return None, f"Invalid GPU threads format: {threads_value}. Must be a number"
    
    @staticmethod
    def validate_gpu_size(size_value):
        """
        Валидация размера видеопамяти GPU (может быть в GB, MB или просто число)
        """
        if size_value is None:
            return None, None, None
        
        # Преобразуем в строку для обработки
        value_str = str(size_value).strip().upper()
        
        if not value_str:
            return None, None, None
        
        # Паттерны для разных форматов
        patterns = [
            (r'^(\d+(?:\.\d+)?)\s*(?:GB|GIB?)$', 1, 'GB'),        # GB, GiB
            (r'^(\d+(?:\.\d+)?)\s*(?:MB|MIB?)$', 0.001, 'MB'),    # MB, MiB
            (r'^(\d+(?:\.\d+)?)\s*(?:TB|TIB?)$', 1024, 'TB'),     # TB, TiB
            (r'^(\d+(?:\.\d+)?)\s*$', 1, 'GB'),                   # просто число (в GB)
        ]
        
        for pattern, multiplier, unit in patterns:
            match = re.match(pattern, value_str)
            if match:
                try:
                    numeric_value = float(match.group(1))
                    gb_value = numeric_value * multiplier
                    
                    # Бизнес-логика: проверка разумных пределов
                    if gb_value < 0:
                        return None, None, "GPU size cannot be negative"
                    elif gb_value == 0:
                        return None, None, "GPU size cannot be zero"
                    elif gb_value > 256:  # Максимум 256GB видеопамяти (на 2024-2025 год)
                        return None, None, f"Unusually large GPU memory: {gb_value}GB"
                    elif gb_value < 1 and gb_value > 0:
                        logger.info(f"Small GPU memory detected: {gb_value}GB (maybe integrated GPU)")
                    
                    # Округляем до 2 знаков
                    gb_value = round(gb_value, 2)
                    
                    # Форматируем для хранения
                    if unit == 'MB' and gb_value < 1:
                        stored_value = f"{int(numeric_value)}MB"
                    else:
                        stored_value = f"{gb_value}GB"
                    
                    return gb_value, stored_value, None
                    
                except (ValueError, TypeError):
                    return None, None, f"Invalid GPU size format: {size_value}"
        
        return None, None, f"Invalid GPU size format: {size_value}. Use format like '8GB', '4096MB', '6'"
    
    @staticmethod
    def validate_gpu_name(gpu_name):
        """
        Валидация названия GPU
        """
        if gpu_name is None:
            return None, None
        
        name_str = str(gpu_name).strip()
        
        if not name_str:
            return None, "GPU name cannot be empty"
        
        if len(name_str) > 255:
            return None, "GPU name is too long (max 255 chars)"
        
        # Бизнес-логика: проверка на подозрительные названия
        suspicious_patterns = [
            (r'(?i)virtual', "Virtual GPU detected"),
            (r'(?i)unknown', "Unknown GPU model"),
            (r'(?i)generic', "Generic GPU model"),
        ]
        
        for pattern, warning in suspicious_patterns:
            if re.search(pattern, name_str):
                logger.warning(f"Suspicious GPU name for validation: {name_str}")
                # Не блокируем, но логируем
        
        return name_str, None
    
    @staticmethod
    def validate_gpu_data(data):
        """
        Валидация входящих данных о GPU.
        Возвращает (is_valid, errors_dict, cleaned_data)
        """
        errors = {}
        cleaned_data = {}
        warnings = []
        
        # Валидация MAX_GPU_THREADS
        max_threads = data.get('MAX_GPU_THREADS')
        if max_threads is not None:
            threads_value, error = GPUDataValidationService.validate_gpu_threads(max_threads)
            if error:
                errors['MAX_GPU_THREADS'] = error
            else:
                cleaned_data['MAX_GPU_THREADS'] = str(threads_value)
                # Добавляем предупреждение для очень мощных GPU
                if threads_value and threads_value > 8192:
                    warnings.append({
                        "field": "MAX_GPU_THREADS",
                        "message": f"Very high GPU thread count: {threads_value} (professional GPU?)",
                        "severity": "info"
                    })
        
        # Валидация GPU_SIZE_GB
        gpu_size = data.get('GPU_SIZE_GB')
        if gpu_size is not None:
            gb_value, stored_value, error = GPUDataValidationService.validate_gpu_size(gpu_size)
            if error:
                errors['GPU_SIZE_GB'] = error
            else:
                cleaned_data['GPU_SIZE_GB'] = stored_value
                # Добавляем предупреждения для нестандартных размеров
                if gb_value:
                    if gb_value > 48:
                        warnings.append({
                            "field": "GPU_SIZE_GB",
                            "message": f"Very large GPU memory: {gb_value}GB (enterprise GPU?)",
                            "severity": "info"
                        })
                    elif gb_value < 2 and gb_value > 0:
                        warnings.append({
                            "field": "GPU_SIZE_GB",
                            "message": f"Small GPU memory: {gb_value}GB (integrated or legacy GPU?)",
                            "severity": "info"
                        })
        
        # Валидация GPU_NAME
        gpu_name = data.get('GPU_NAME')
        if gpu_name is not None:
            name_value, error = GPUDataValidationService.validate_gpu_name(gpu_name)
            if error:
                errors['GPU_NAME'] = error
            else:
                cleaned_data['GPU_NAME'] = name_value
        
        # Логируем предупреждения
        if warnings:
            logger.info(f"GPU validation warnings: {warnings}")
        
        return len(errors) == 0, errors, cleaned_data, warnings


class GPUMetricsService:
    """Сервис для работы с метриками GPU"""
    
    @staticmethod
    def save_or_update_gpu_metrics(server, gpu_data):
        """
        Сохраняет или обновляет метрики GPU для сервера.
        Возвращает (gpu_instance, created_flag, warnings)
        """
        # Валидируем данные
        is_valid, errors, cleaned_data, warnings = GPUDataValidationService.validate_gpu_data(gpu_data)
        
        if not is_valid:
            raise ValidationError(f"Invalid GPU data: {errors}")
        
        # Бизнес-логика: проверяем, нужно ли обновлять
        try:
            existing_gpu = gpu.objects.get(UuidServer=server.uuid)
            
            # Проверяем, изменились ли данные
            has_changes = False
            for field, value in cleaned_data.items():
                if getattr(existing_gpu, field) != value:
                    has_changes = True
                    break
            
            if not has_changes:
                logger.info(f"No changes in GPU metrics for server {server.uuid}")
                return existing_gpu, False, warnings
            
            # Обновляем существующую запись
            for field, value in cleaned_data.items():
                setattr(existing_gpu, field, value)
            existing_gpu.save()
            
            logger.info(f"Updated GPU metrics for server {server.uuid}")
            return existing_gpu, False, warnings
            
        except gpu.DoesNotExist:
            # Создаем новую запись
            gpu_instance = gpu.objects.create(
                UuidServer=server.uuid,
                **cleaned_data
            )
            logger.info(f"Created new GPU metrics for server {server.uuid}")
            return gpu_instance, True, warnings
    
    @staticmethod
    def get_gpu_metrics_for_server(server):
        """Получает метрики GPU для конкретного сервера"""
        try:
            gpu_instance = gpu.objects.get(UuidServer=server.uuid)
            
            # Парсим размер для отображения в GB
            size_gb = None
            if gpu_instance.GPU_SIZE_GB:
                match = re.search(r'(\d+(?:\.\d+)?)', str(gpu_instance.GPU_SIZE_GB))
                if match:
                    size_gb = float(match.group(1))
            
            return {
                "gpu_name": gpu_instance.GPU_NAME,
                "max_threads": gpu_instance.MAX_GPU_THREADS,
                "gpu_size_gb": gpu_instance.GPU_SIZE_GB,
                "gpu_size_gb_numeric": size_gb,
                "server_uuid": gpu_instance.UuidServer,
                "created_at": getattr(gpu_instance, 'created_at', None),
                "updated_at": getattr(gpu_instance, 'updated_at', None)
            }
        except gpu.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_gpus_with_servers():
        """Получает все GPU с информацией о серверах"""
        gpus = gpu.objects.all()
        result = []
        
        for gpu_instance in gpus:
            # Парсим размер
            size_gb = None
            if gpu_instance.GPU_SIZE_GB:
                match = re.search(r'(\d+(?:\.\d+)?)', str(gpu_instance.GPU_SIZE_GB))
                if match:
                    size_gb = float(match.group(1))
            
            result.append({
                "id": gpu_instance.id,
                "server_uuid": gpu_instance.UuidServer,
                "gpu_name": gpu_instance.GPU_NAME,
                "max_threads": gpu_instance.MAX_GPU_THREADS,
                "gpu_size": gpu_instance.GPU_SIZE_GB,
                "gpu_size_gb": size_gb,
                "created_at": getattr(gpu_instance, 'created_at', None),
                "updated_at": getattr(gpu_instance, 'updated_at', None)
            })
        
        return result
    
    @staticmethod
    def get_gpu_performance_score(server):
        """
        Рассчитывает примерную производительность GPU на основе параметров
        (упрощенная метрика для сравнения)
        """
        metrics = GPUMetricsService.get_gpu_metrics_for_server(server)
        if not metrics:
            return None
        
        score = 0
        
        # Учитываем количество потоков
        threads = metrics.get('max_threads')
        if threads:
            try:
                threads_int = int(threads)
                if threads_int < 1000:
                    score += threads_int * 0.1
                elif threads_int < 5000:
                    score += threads_int * 0.05
                else:
                    score += threads_int * 0.02
            except (ValueError, TypeError):
                pass
        
        # Учитываем объем видеопамяти
        size_gb = metrics.get('gpu_size_gb_numeric')
        if size_gb:
            if size_gb < 4:
                score += size_gb * 10
            elif size_gb < 8:
                score += size_gb * 15
            else:
                score += size_gb * 20
        
        # Учитываем название (упрощенно)
        gpu_name = metrics.get('gpu_name', '').lower()
        if 'rtx' in gpu_name or 'radeon' in gpu_name:
            score *= 1.5
        elif 'gtx' in gpu_name:
            score *= 1.2
        elif 'quadro' in gpu_name or 'a100' in gpu_name:
            score *= 2.0
        
        return round(score, 2)


class GPUAlertService:
    """Сервис для уведомлений о состоянии GPU"""
    
    @staticmethod
    def check_gpu_anomalies(gpu_data, server):
        """
        Проверяет аномалии в данных GPU.
        """
        warnings = []
        
        # Проверка на отсутствие GPU (все поля пустые)
        has_data = any([
            gpu_data.get('MAX_GPU_THREADS'),
            gpu_data.get('GPU_SIZE_GB'),
            gpu_data.get('GPU_NAME')
        ])
        
        if not has_data:
            warnings.append({
                "type": "no_gpu",
                "message": "No GPU detected on this server",
                "severity": "info"
            })
        
        # Проверка на несовместимые параметры
        threads = gpu_data.get('MAX_GPU_THREADS')
        size = gpu_data.get('GPU_SIZE_GB')
        
        if threads and size:
            try:
                threads_int = int(threads)
                # Парсим размер
                match = re.search(r'(\d+(?:\.\d+)?)', str(size))
                if match:
                    size_gb = float(match.group(1))
                    
                    # Бизнес-логика: несоответствие потоков и памяти
                    if threads_int > 10000 and size_gb < 8:
                        warnings.append({
                            "type": "mismatch",
                            "message": f"Unusual configuration: {threads_int} threads but only {size_gb}GB VRAM",
                            "severity": "warning"
                        })
                    elif threads_int < 1000 and size_gb > 16:
                        warnings.append({
                            "type": "mismatch",
                            "message": f"Unusual configuration: {size_gb}GB VRAM but only {threads_int} threads",
                            "severity": "warning"
                        })
            except (ValueError, TypeError):
                pass
        
        # Проверка на подозрительно большое количество потоков
        if threads:
            try:
                threads_int = int(threads)
                if threads_int > 32768:
                    warnings.append({
                        "type": "extreme_threads",
                        "message": f"Extremely high GPU thread count: {threads_int} (check if this is correct)",
                        "severity": "critical"
                    })
                elif threads_int > 16384:
                    warnings.append({
                        "type": "high_threads",
                        "message": f"Very high GPU thread count: {threads_int} (professional/compute GPU)",
                        "severity": "info"
                    })
            except (ValueError, TypeError):
                pass
        
        if warnings:
            logger.warning(f"GPU anomalies detected for server {server.uuid}: {warnings}")
        
        return warnings
    
    @staticmethod
    def check_all_gpus_health():
        """Проверка здоровья всех GPU в системе"""
        all_warnings = []
        gpus = gpu.objects.all()
        
        for gpu_instance in gpus:
            try:
                server = Server.objects.get(uuid=gpu_instance.UuidServer)
                gpu_data = {
                    'MAX_GPU_THREADS': gpu_instance.MAX_GPU_THREADS,
                    'GPU_SIZE_GB': gpu_instance.GPU_SIZE_GB,
                    'GPU_NAME': gpu_instance.GPU_NAME
                }
                warnings = GPUAlertService.check_gpu_anomalies(gpu_data, server)
                if warnings:
                    all_warnings.extend(warnings)
            except Server.DoesNotExist:
                continue
        
        return all_warnings


class GPUAnalyticsService:
    """Сервис для аналитики GPU"""
    
    @staticmethod
    def get_gpu_statistics():
        """Статистика по всем GPU в системе"""
        total_gpus = gpu.objects.count()
        gpus_with_data = gpu.objects.exclude(GPU_NAME__isnull=True).exclude(GPU_NAME='')
        
        # Подсчет GPU по производителям
        manufacturers = {
            'NVIDIA': 0,
            'AMD': 0,
            'Intel': 0,
            'Other': 0
        }
        
        total_threads = 0
        total_memory_gb = 0
        memory_values = []
        
        for gpu_instance in gpus_with_data:
            # Определяем производителя
            name = (gpu_instance.GPU_NAME or '').lower()
            if 'nvidia' in name or 'geforce' in name or 'quadro' in name or 'tesla' in name:
                manufacturers['NVIDIA'] += 1
            elif 'amd' in name or 'radeon' in name or 'radeon' in name:
                manufacturers['AMD'] += 1
            elif 'intel' in name or 'hd graphics' in name or 'iris' in name:
                manufacturers['Intel'] += 1
            else:
                manufacturers['Other'] += 1
            
            # Суммируем потоки
            if gpu_instance.MAX_GPU_THREADS:
                try:
                    threads = int(gpu_instance.MAX_GPU_THREADS)
                    total_threads += threads
                except (ValueError, TypeError):
                    pass
            
            # Суммируем память
            if gpu_instance.GPU_SIZE_GB:
                match = re.search(r'(\d+(?:\.\d+)?)', str(gpu_instance.GPU_SIZE_GB))
                if match:
                    memory_gb = float(match.group(1))
                    total_memory_gb += memory_gb
                    memory_values.append(memory_gb)
        
        # Расчет средних значений
        avg_threads = total_threads / total_gpus if total_gpus > 0 else 0
        avg_memory = total_memory_gb / total_gpus if total_gpus > 0 else 0
        
        # Медианный размер памяти
        memory_values.sort()
        median_memory = memory_values[len(memory_values) // 2] if memory_values else 0
        
        return {
            'total_gpus': total_gpus,
            'gpus_with_name': gpus_with_data.count(),
            'manufacturers': manufacturers,
            'total_threads': total_threads,
            'average_threads_per_gpu': round(avg_threads, 2),
            'total_memory_gb': round(total_memory_gb, 2),
            'average_memory_gb': round(avg_memory, 2),
            'median_memory_gb': round(median_memory, 2),
            'largest_gpu_memory_gb': max(memory_values) if memory_values else 0,
            'smallest_gpu_memory_gb': min(memory_values) if memory_values else 0
        }
    
    @staticmethod
    def get_powerful_gpus(threshold_threads=5000, threshold_memory=8):
        """Получение списка мощных GPU"""
        powerful_gpus = []
        gpus = gpu.objects.all()
        
        for gpu_instance in gpus:
            is_powerful = False
            reason = []
            
            # Проверяем потоки
            if gpu_instance.MAX_GPU_THREADS:
                try:
                    threads = int(gpu_instance.MAX_GPU_THREADS)
                    if threads >= threshold_threads:
                        is_powerful = True
                        reason.append(f"{threads} threads")
                except (ValueError, TypeError):
                    pass
            
            # Проверяем память
            if gpu_instance.GPU_SIZE_GB:
                match = re.search(r'(\d+(?:\.\d+)?)', str(gpu_instance.GPU_SIZE_GB))
                if match:
                    memory = float(match.group(1))
                    if memory >= threshold_memory:
                        is_powerful = True
                        reason.append(f"{memory}GB")
            
            if is_powerful:
                powerful_gpus.append({
                    "server_uuid": gpu_instance.UuidServer,
                    "gpu_name": gpu_instance.GPU_NAME,
                    "threads": gpu_instance.MAX_GPU_THREADS,
                    "memory": gpu_instance.GPU_SIZE_GB,
                    "reason": ", ".join(reason)
                })
        
        return powerful_gpus


class GPURecommendationService:
    """Сервис для рекомендаций по GPU"""
    
    @staticmethod
    def get_upgrade_recommendations(server):
        """
        Рекомендации по апгрейду GPU
        """
        metrics = GPUMetricsService.get_gpu_metrics_for_server(server)
        if not metrics:
            return {"has_gpu": False, "message": "No GPU detected on this server"}
        
        recommendations = []
        
        # Проверяем объем памяти
        size_gb = metrics.get('gpu_size_gb_numeric')
        if size_gb:
            if size_gb < 4:
                recommendations.append({
                    "type": "memory_upgrade",
                    "current": f"{size_gb}GB",
                    "recommendation": "Upgrade to at least 8GB GPU memory for better performance",
                    "priority": "high"
                })
            elif size_gb < 8:
                recommendations.append({
                    "type": "memory_upgrade",
                    "current": f"{size_gb}GB",
                    "recommendation": "Consider upgrading to 8GB+ GPU memory for modern workloads",
                    "priority": "medium"
                })
        
        # Проверяем потоки
        threads = metrics.get('max_threads')
        if threads:
            try:
                threads_int = int(threads)
                if threads_int < 1000:
                    recommendations.append({
                        "type": "performance_upgrade",
                        "current": f"{threads_int} threads",
                        "recommendation": "Consider upgrading to a GPU with more processing units",
                        "priority": "medium"
                    })
            except (ValueError, TypeError):
                pass
        
        # Проверяем возраст/тип по названию
        gpu_name = (metrics.get('gpu_name') or '').lower()
        if 'gtx' in gpu_name and '10' in gpu_name:
            recommendations.append({
                "type": "age_upgrade",
                "current": gpu_name,
                "recommendation": "This GPU model is several generations old, consider upgrade",
                "priority": "low"
            })
        
        return {
            "has_gpu": True,
            "current_gpu": metrics.get('gpu_name'),
            "recommendations": recommendations,
            "performance_score": GPUMetricsService.get_gpu_performance_score(server)
        }