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
        """Аутентификация"""
        api_key = ServerAuthenticationService.extract_api_key_from_request(request)
        server, error = ServerAuthenticationService.authenticate_server(api_key)
        
        if error:
            return None, Response({"error": error}, status=401)
        return server, None
    
    def post(self, request):
        try:
            # 1. Аутентификация
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            # 2. Валидация данных (с предупреждениями)
            is_valid, errors, cleaned_data, validation_warnings = GPUDataValidationService.validate_gpu_data(request.data)
            
            if not is_valid:
                return Response({
                    "error": "Validation failed",
                    "details": errors
                }, status=400)
            
            # 3. Проверка аномалий
            anomaly_warnings = GPUAlertService.check_gpu_anomalies(cleaned_data, server)
            
            # 4. Сохранение метрик
            gpu_instance, created, save_warnings = GPUMetricsService.save_or_update_gpu_metrics(server, cleaned_data)
            
            # 5. Формирование ответа
            response_data = {
                "success": True,
                "message": "GPU metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "gpu_id": gpu_instance.id,
                "is_new": created,
                "data": {
                    "gpu_name": cleaned_data.get('GPU_NAME'),
                    "max_threads": cleaned_data.get('MAX_GPU_THREADS'),
                    "gpu_size": cleaned_data.get('GPU_SIZE_GB'),
                }
            }
            
            # Добавляем все предупреждения
            all_warnings = validation_warnings + anomaly_warnings + save_warnings
            if all_warnings:
                response_data["warnings"] = all_warnings
            
            # Добавляем оценку производительности
            performance_score = GPUMetricsService.get_gpu_performance_score(server)
            if performance_score:
                response_data["performance_score"] = performance_score
            
            return Response(response_data, status=201 if created else 200)
            
        except ValidationError as e:
            return Response({
                "error": "Validation failed",
                "details": str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Failed to save GPU metrics: {str(e)}", exc_info=True)
            return Response({
                "error": "Failed to save GPU metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение данных о GPU по API ключу"""
        try:
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            gpu_metrics = GPUMetricsService.get_gpu_metrics_for_server(server)
            
            if not gpu_metrics:
                return Response({
                    "success": False,
                    "message": "GPU data not found for this server"
                }, status=404)
            
            recommendations = GPURecommendationService.get_upgrade_recommendations(server)
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "gpu": gpu_metrics,
                "recommendations": recommendations
            })
                
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
                "statistics": statistics,
                "powerful_gpus": powerful_gpus
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