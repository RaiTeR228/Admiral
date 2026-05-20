# models/ram/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .services import (
    ServerAuthenticationService,
    RAMDataValidationService,
    RAMMetricsService,
    RAMAlertService,
    RAMAnalyticsService
)
from .models import Ram
from server.models import Server
import logging

logger = logging.getLogger(__name__)


class RamMetricsView(APIView):
    """API для приема и сохранения данных о RAM"""
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
            
            # 2. Валидация данных
            is_valid, errors, cleaned_data, validation_warnings = RAMDataValidationService.validate_ram_data(request.data)
            
            if not is_valid:
                return Response({
                    "error": "Validation failed",
                    "details": errors
                }, status=400)
            
            # 3. Проверка аномалий
            anomaly_warnings = RAMAlertService.check_ram_anomalies(cleaned_data, server)
            
            # 4. Сохранение метрик
            ram_instance, created, save_warnings = RAMMetricsService.save_or_update_ram_metrics(server, cleaned_data)
            
            # 5. Формирование ответа
            response_data = {
                "success": True,
                "message": "RAM metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "ram_id": ram_instance.id,
                "is_new": created,
                "data": {
                    "max_ram": cleaned_data.get('MAX_RAM'),
                }
            }
            
            # Добавляем предупреждения
            all_warnings = validation_warnings + anomaly_warnings + save_warnings
            if all_warnings:
                response_data["warnings"] = all_warnings
            
            return Response(response_data, status=201 if created else 200)
            
        except ValidationError as e:
            return Response({
                "error": "Validation failed",
                "details": str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Failed to save RAM metrics: {str(e)}", exc_info=True)
            return Response({
                "error": "Failed to save RAM metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение данных о RAM по API ключу"""
        try:
            # Аутентификация
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            # Получение метрик
            ram_metrics = RAMMetricsService.get_ram_metrics_for_server(server)
            
            if not ram_metrics:
                return Response({
                    "success": False,
                    "message": "RAM data not found for this server"
                }, status=404)
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "ram": ram_metrics
            })
                
        except Exception as e:
            logger.error(f"Failed to get RAM metrics: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class RAMListView(APIView):
    """Получение списка всех RAM (только для админов)"""
    permission_classes = [AllowAny]
    
    def _check_admin_access(self, request):
        """Проверка админского доступа"""
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
            return Response({"error": "Admin access required"}, status=403)
        return None
    
    def get(self, request):
        try:
            # Проверка админского доступа
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            # Получение всех данных
            all_rams = RAMMetricsService.get_all_rams_with_servers()
            
            # Получаем статистику
            statistics = RAMAnalyticsService.get_ram_statistics()
            
            # Получаем рекомендации
            recommendations = RAMAnalyticsService.get_ram_recommendations()
            
            return Response({
                "success": True,
                "count": len(all_rams),
                "rams": all_rams,
                "statistics": statistics,
                "recommendations": recommendations
            })
            
        except Exception as e:
            logger.error(f"Failed to get RAM list: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class RAMHealthCheckView(APIView):
    """API для проверки здоровья RAM"""
    permission_classes = [AllowAny]
    
    def _check_admin_access(self, request):
        """Проверка админского доступа"""
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
            return Response({"error": "Admin access required"}, status=403)
        return None
    
    def get(self, request):
        """Проверка здоровья всей RAM"""
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            alerts = RAMAlertService.check_all_rams_health()
            statistics = RAMAnalyticsService.get_ram_statistics()
            
            # Определяем статус
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
            logger.error(f"Failed to check RAM health: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)
        