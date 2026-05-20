# models/disk/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .services import (
    ServerAuthenticationService,
    DiskDataValidationService,
    DiskMetricsService,
    DiskAlertService,
    DiskAnalyticsService
)
from .models import Disk
from server.models import Server
import logging

logger = logging.getLogger(__name__)

class DiskMetricsView(APIView):
    permission_classes = [AllowAny]
    
    def _authenticate(self, request):
        api_key = ServerAuthenticationService.extract_api_key_from_request(request)
        server, error = ServerAuthenticationService.authenticate_server(api_key)
        
        if error:
            return None, Response({"error": error}, status=401)
        return server, None

    def post(self, request):
        try:
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            is_valid, errors, cleaned_data = DiskDataValidationService.validate_disk_data(request.data)
            if not is_valid:
                return Response({
                    "error": "Validation failed",
                    "details": errors
                }, status=400)
            
            warnings = DiskAlertService.check_disk_anomalies(cleaned_data, server)
            
            disk_instance, created = DiskMetricsService.save_or_update_disk_metrics(server, cleaned_data)
            
            response_data = {
                'success': True,
                'message': 'Данные диска успешно сохранены',
                'server_id': server.id,
                'server_uuid': str(server.uuid),
                'disk_id': disk_instance.id,
                'is_new': created,
                'data': {
                    'disk_name': cleaned_data.get('DISK_NAME'),
                    'max_swap': cleaned_data.get('MAX_SWAP'),
                    'max_disk': cleaned_data.get('MAX_DISK'),
                    'free_disk': cleaned_data.get('Free_DISK'),
                }
            }
            
            if warnings:
                response_data["warnings"] = warnings
            
            usage_percent = DiskMetricsService.get_disk_usage_percentage(server)
            if usage_percent is not None:
                response_data["disk_usage_percent"] = usage_percent
            
            return Response(response_data, status=201 if created else 200)
            
        except ValidationError as e:
            return Response({
                "error": "Validation failed",
                "details": str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Failed to save disk metrics: {str(e)}", exc_info=True)
            return Response({
                'error': 'Ошибка сохранения данных диска',
                'details': str(e)
            }, status=500)

    def get(self, request):
        try:
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            disk_metrics = DiskMetricsService.get_disk_metrics_for_server(server)
            
            if not disk_metrics:
                return Response({
                    'success': False,
                    'message': 'Данные диска не найдены для этого сервера'
                }, status=404)
            
            usage_percent = DiskMetricsService.get_disk_usage_percentage(server)
            if usage_percent is not None:
                disk_metrics['usage_percent'] = usage_percent
            
            return Response({
                'success': True,
                'server_uuid': str(server.uuid),
                'disk': disk_metrics
            })
                
        except Exception as e:
            logger.error(f"Failed to get disk metrics: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)


class DiskListView(APIView):
    permission_classes = [AllowAny]

    def _check_admin_access(self, request):
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
            return Response({'error': 'Требуется доступ администратора'}, status=403)
        return None

    def get(self, request):
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            all_disks = DiskMetricsService.get_all_disks_with_servers()
            
            statistics = DiskAnalyticsService.get_disk_statistics()
            
            return Response({
                'success': True,
                'count': len(all_disks),
                'disks': all_disks,
                'statistics': statistics
            })
            
        except Exception as e:
            logger.error(f"Failed to get disk list: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)


class DiskHealthCheckView(APIView):
    
    permission_classes = [AllowAny]    
    def get(self, request):
        try:
            admin_response = self._check_admin_access(request)
            if admin_response:
                return admin_response
            
            alerts = DiskAlertService.check_all_servers_disk_space()
            statistics = DiskAnalyticsService.get_disk_statistics()
            
            return Response({
                'success': True,
                'total_alerts': len(alerts),
                'alerts': alerts,
                'statistics': statistics,
                'status': 'critical' if any(a['severity'] == 'critical' for a in alerts) else 'warning' if alerts else 'healthy'
            })
            
        except Exception as e:
            logger.error(f"Failed to check disk health: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)