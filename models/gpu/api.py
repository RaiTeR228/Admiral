# models/gpu/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .services import (
    ServerAuthenticationService,
    GPUDataValidationService,
    GPUMetricsService,
    GPUAlertService,
    GPUAnalyticsService,
    GPURecommendationService
)
from .models import gpu
from server.models import Server
import logging

logger = logging.getLogger(__name__)


class GPUMetricsView(APIView):
    """API для приема и сохранения данных о GPU"""
    permission_classes = [AllowAny]
    
    def _authenticate(self, request):
        """Аутентификация сервера по API ключу"""
        api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
        if not api_key:
            api_key = request.headers.get('X-API-Key', '')
        
        if not api_key:
            return None, Response({
                "error": "API key required",
                "details": "Please provide API key in Authorization header"
            }, status=401)
        
        try:
            server = Server.objects.get(api_key=api_key)
            return server, None
        except Server.DoesNotExist:
            return None, Response({
                "error": "Invalid API key",
                "details": "No server found with this API key"
            }, status=401)
    
    def post(self, request):
        try:
            # 1. Аутентификация
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            # 2. Получаем данные о GPU из запроса
            gpu_name = request.data.get("GPU_NAME") or request.data.get("gpu_name")
            max_threads = request.data.get("MAX_GPU_THREADS") or request.data.get("max_threads") or request.data.get("max_gpu_threads")
            gpu_size = request.data.get("GPU_SIZE_GB") or request.data.get("gpu_size") or request.data.get("gpu_size_gb")
            
            # 3. Валидация: проверяем, есть ли хоть какие-то данные
            if not any([gpu_name, max_threads, gpu_size]):
                return Response({
                    "error": "Validation failed",
                    "details": "At least one GPU field is required (GPU_NAME, MAX_GPU_THREADS, GPU_SIZE_GB)"
                }, status=400)
            
            # 4. Валидация GPU_NAME
            if gpu_name is not None:
                gpu_name = str(gpu_name).strip()
                if len(gpu_name) > 255:
                    return Response({
                        "error": "Validation failed",
                        "details": {"GPU_NAME": "GPU name is too long (max 255 chars)"}
                    }, status=400)
                if not gpu_name:
                    gpu_name = None
            
            # 5. Валидация MAX_GPU_THREADS
            if max_threads is not None:
                try:
                    threads_value = int(str(max_threads).strip())
                    if threads_value < 0:
                        return Response({
                            "error": "Validation failed",
                            "details": {"MAX_GPU_THREADS": "Threads cannot be negative"}
                        }, status=400)
                    elif threads_value == 0:
                        return Response({
                            "error": "Validation failed",
                            "details": {"MAX_GPU_THREADS": "Threads cannot be zero (no GPU?)"}
                        }, status=400)
                    elif threads_value > 65536:
                        return Response({
                            "error": "Validation failed",
                            "details": {"MAX_GPU_THREADS": f"Unusually high threads count: {threads_value}"}
                        }, status=400)
                    max_threads = str(threads_value)
                except (ValueError, TypeError):
                    return Response({
                        "error": "Validation failed",
                        "details": {"MAX_GPU_THREADS": f"Invalid threads format: {max_threads}. Must be a number"}
                    }, status=400)
            
            # 6. Валидация GPU_SIZE_GB
            if gpu_size is not None:
                try:
                    size_str = str(gpu_size).strip().upper()
                    # Удаляем GB/MB и пробелы
                    size_str_clean = size_str.replace('GB', '').replace('GIB', '').replace('MB', '').replace('MIB', '').replace(' ', '')
                    size_value = float(size_str_clean)
                    
                    # Определяем единицу измерения
                    if 'MB' in size_str or 'MIB' in size_str:
                        size_value = size_value / 1024  # Переводим MB в GB
                    
                    if size_value < 0:
                        return Response({
                            "error": "Validation failed",
                            "details": {"GPU_SIZE_GB": "GPU size cannot be negative"}
                        }, status=400)
                    elif size_value == 0:
                        return Response({
                            "error": "Validation failed",
                            "details": {"GPU_SIZE_GB": "GPU size cannot be zero"}
                        }, status=400)
                    elif size_value > 256:
                        return Response({
                            "error": "Validation failed",
                            "details": {"GPU_SIZE_GB": f"Unusually large GPU memory: {size_value}GB"}
                        }, status=400)
                    
                    # Форматируем для хранения
                    if size_value < 1:
                        stored_size = f"{int(size_value * 1024)}MB"
                    else:
                        stored_size = f"{size_value:.1f}GB".rstrip('0').rstrip('.') if size_value % 1 != 0 else f"{int(size_value)}GB"
                    gpu_size = stored_size
                    
                except (ValueError, TypeError):
                    return Response({
                        "error": "Validation failed",
                        "details": {"GPU_SIZE_GB": f"Invalid GPU size format: {gpu_size}. Use format like '8GB', '4096MB', '6'"}
                    }, status=400)
            
            # 7. Сохраняем или обновляем данные GPU
            # Подготавливаем данные для сохранения (только не-None поля)
            gpu_data = {}
            if gpu_name is not None:
                gpu_data['GPU_NAME'] = gpu_name
            if max_threads is not None:
                gpu_data['MAX_GPU_THREADS'] = max_threads
            if gpu_size is not None:
                gpu_data['GPU_SIZE_GB'] = gpu_size
            
            gpu_instance, created = gpu.objects.update_or_create(
                UuidServer=server.uuid,
                defaults=gpu_data
            )
            
            # 8. Формируем ответ
            return Response({
                "success": True,
                "message": "GPU metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "gpu_id": gpu_instance.id,
                "is_new": created,
                "data": {
                    "gpu_name": gpu_instance.GPU_NAME,
                    "max_threads": gpu_instance.MAX_GPU_THREADS,
                    "gpu_size": gpu_instance.GPU_SIZE_GB,
                }
            }, status=201 if created else 200)
            
        except Exception as e:
            logger.error(f"Failed to save GPU metrics: {str(e)}", exc_info=True)
            return Response({
                "error": "Failed to save GPU metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение данных о GPU по API ключу"""
        try:
            # Аутентификация
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            # Получаем данные
            try:
                gpu_data = gpu.objects.get(UuidServer=server.uuid)
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "server_name": server.name,
                    "gpu": {
                        "gpu_name": gpu_data.GPU_NAME,
                        "max_threads": gpu_data.MAX_GPU_THREADS,
                        "gpu_size": gpu_data.GPU_SIZE_GB,
                        "created_at": gpu_data.created_at,
                        "updated_at": gpu_data.updated_at
                    }
                })
            except gpu.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "GPU data not found for this server"
                }, status=404)
                
        except Exception as e:
            logger.error(f"Failed to get GPU metrics: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class GPUListView(APIView):
    permission_classes = [AllowAny]
    
    def _check_admin_access(self, request):
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
            return Response({"error": "Admin access required"}, status=403)
        return None
    
    def get(self, request):
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            all_gpus = GPUMetricsService.get_all_gpus_with_servers()
            
            statistics = GPUAnalyticsService.get_gpu_statistics()
            
            powerful_gpus = GPUAnalyticsService.get_powerful_gpus()
            
            return Response({
                "success": True,
                "count": len(all_gpus),
                "gpus": all_gpus,
                # "statistics": statistics,
                # "powerful_gpus": powerful_gpus
            })
            
        except Exception as e:
            logger.error(f"Failed to get GPU list: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class GPUHealthCheckView(APIView):
    permission_classes = [AllowAny]
    
    def _check_admin_access(self, request):
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
            return Response({"error": "Admin access required"}, status=403)
        return None
    
    def get(self, request):
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            alerts = GPUAlertService.check_all_gpus_health()
            statistics = GPUAnalyticsService.get_gpu_statistics()
            
            has_critical = any(a.get('severity') == 'critical' for a in alerts)
            has_warning = any(a.get('severity') == 'warning' for a in alerts)
            
            if has_critical:
                status = 'critical'
            elif has_warning:
                status = 'warning'
            elif alerts:
                status = 'info'
            else:
                status = 'healthy'
            
            return Response({
                'success': True,
                'total_alerts': len(alerts),
                'alerts': alerts,
                'statistics': statistics,
                'status': status
            })
            
        except Exception as e:
            logger.error(f"Failed to check GPU health: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)


class GPUPerformanceView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response

            all_gpus = GPUMetricsService.get_all_gpus_with_servers()
            
            for gpu_data in all_gpus:
                try:
                    server = Server.objects.get(uuid=gpu_data['server_uuid'])
                    score = GPUMetricsService.get_gpu_performance_score(server)
                    gpu_data['performance_score'] = score
                except Server.DoesNotExist:
                    gpu_data['performance_score'] = None
            
            all_gpus.sort(key=lambda x: x.get('performance_score') or 0, reverse=True)
            
            return Response({
                'success': True,
                'count': len(all_gpus),
                'gpu_performance_ranking': all_gpus
            })
            
        except Exception as e:
            logger.error(f"Failed to get GPU performance: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)