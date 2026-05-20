# apps/cpu/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .services import (
    ServerAuthenticationService,
    CPUDataValidationService,
    CPUMetricsService,
    CPUAlertService
)
import logging

logger = logging.getLogger(__name__)


class CPUMetricsView(APIView):
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
            
            is_valid, errors, cleaned_data = CPUDataValidationService.validate_cpu_data(request.data)
            if not is_valid:
                return Response({
                    "error": "Validation failed",
                    "details": errors
                }, status=400)
            warnings = CPUAlertService.check_cpu_anomalies(cleaned_data, server)
            
            cpu_instance, created = CPUMetricsService.save_or_update_cpu_metrics(server, cleaned_data)

            response_data = {
                "success": True,
                "message": "CPU metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "cpu_id": cpu_instance.id,
                "is_new": created,
                "data": {
                    "cpu_name": cleaned_data.get('CPU_NAME'),
                    "cores": cleaned_data.get('MAX_CPU_CORES'),
                    "threads": cleaned_data.get('MAX_CPU_THREADS')
                }
            }
            
            if warnings:
                response_data["warnings"] = warnings
            
            return Response(response_data, status=201 if created else 200)
            
        except ValidationError as e:
            return Response({
                "error": "Validation failed",
                "details": str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Failed to save CPU metrics: {str(e)}", exc_info=True)
            return Response({
                "error": "Failed save CPU metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение данных о CPU по API ключу"""
        try:
            server, auth_response = self._authenticate(request)
            if auth_response:
                return auth_response
            
            cpu_metrics = CPUMetricsService.get_cpu_metrics_for_server(server)
            
            if not cpu_metrics:
                return Response({
                    "success": False,
                    "message": "CPU data not found for this server"
                }, status=404)
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "cpu": cpu_metrics
            })
                
        except Exception as e:
            logger.error(f"Failed to get CPU metrics: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class CPUListView(APIView):
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
            
            all_cpus = CPUMetricsService.get_all_cpus_with_servers()
            
            return Response({
                "success": True,
                "count": len(all_cpus),
                "cpus": all_cpus
            })
            
        except Exception as e:
            logger.error(f"Failed to get CPU list: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)