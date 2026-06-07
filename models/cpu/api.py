# apps/cpu/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Cpu
from server.models import Server 

class CPUMetricsView(APIView):
    """API для приема и сохранения данных о CPU"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # 1. Проверяем API ключ
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')
            
            if not api_key:
                return Response({
                    "error": "API key required",
                    "details": "Please provide API key in Authorization header"
                }, status=401)
            
            # 2. Находим сервер по API ключу
            try:
                server = Server.objects.get(api_key=api_key)
            except Server.DoesNotExist:
                return Response({
                    "error": "Invalid API key",
                    "details": "No server found with this API key"
                }, status=401)
            
            # 3. Получаем данные о CPU из запроса
            cpu_data = {
                'MAX_CPU_CORES': request.data.get("MAX_CPU_CORES"),
                'MAX_CPU_THREADS': request.data.get("MAX_CPU_THREADS"),
                'CPU_NAME': request.data.get("CPU_NAME"),
                'FREQ':request.data.get("FREQ"),
            }
            
            # 4. Сохраняем или обновляем данные CPU
            cpu_instance, created = Cpu.objects.update_or_create(
                UuidServer=str(server.uuid),  # Преобразуем UUID в строку
                defaults=cpu_data
            )
            
            return Response({
                "success": True,
                "message": "CPU metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "cpu_id": cpu_instance.id,
                "is_new": created,
                "data": {
                    "cpu_name": cpu_data['CPU_NAME'],
                    "cores": cpu_data['MAX_CPU_CORES'],
                    "threads": cpu_data['MAX_CPU_THREADS'],
                    "freq":cpu_data["FREQ"],
                }
            }, status=201 if created else 200)
            
        except Exception as e:
            return Response({
                "error": "Failed to save CPU metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение данных о CPU по API ключу"""
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')
            
            if not api_key:
                return Response({"error": "API key required"}, status=401)
            
            server = Server.objects.get(api_key=api_key)
            
            try:
                cpu_data = Cpu.objects.get(UuidServer=str(server.uuid))
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "cpu": {
                        "name": cpu_data.CPU_NAME,
                        "max_cores": cpu_data.MAX_CPU_CORES,
                        "max_threads": cpu_data.MAX_CPU_THREADS,
                        "created_at": cpu_data.created_at,
                        "updated_at": cpu_data.updated_at,
                        "freq":cpu_data.freq,
                    }
                })
            except Cpu.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "CPU data not found for this server"
                }, status=404)
                
        except Server.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CPUListView(APIView):
    """Получение списка всех CPU из БД"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Получаем все записи CPU из БД
            cpus = Cpu.objects.all().order_by('-created_at')
            
            if not cpus.exists():
                return Response({
                    "success": True,
                    "message": "No CPU data found in database",
                    "count": 0,
                    "cpus": []
                })
            
            data = []
            for cpu in cpus:
                server_info = None
                try:
                    server = Server.objects.get(uuid=cpu.UuidServer)
                    server_info = {
                        "id": server.id,
                        "name": server.name if hasattr(server, 'name') else None,
                        "ip_address": server.ip_address if hasattr(server, 'ip_address') else None,
                    }
                except Server.DoesNotExist:
                    server_info = None
                
                data.append({
                    "id": cpu.id,
                    "server_uuid": cpu.UuidServer,
                    "server_info": server_info,
                    "cpu_name": cpu.CPU_NAME,
                    "cores": cpu.MAX_CPU_CORES,
                    "threads": cpu.MAX_CPU_THREADS,
                    "created_at": cpu.created_at,
                    "updated_at": cpu.updated_at
                })
            
            return Response({
                "success": True,
                "count": len(data),
                "cpus": data
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to retrieve CPU data",
                "details": str(e)
            }, status=500)


class CPUSpecificView(APIView):
    """Получение данных о CPU по UUID сервера"""
    permission_classes = [AllowAny]
    
    def get(self, request, server_uuid):
        try:
            # Получаем CPU данные по UUID сервера
            cpu_data = Cpu.objects.get(UuidServer=server_uuid)
            
            return Response({
                "success": True,
                "server_uuid": server_uuid,
                "cpu": {
                    "id": cpu_data.id,
                    "name": cpu_data.CPU_NAME,
                    "max_cores": cpu_data.MAX_CPU_CORES,
                    "max_threads": cpu_data.MAX_CPU_THREADS,
                    "created_at": cpu_data.created_at,
                    "updated_at": cpu_data.updated_at
                }
            })
            
        except Cpu.DoesNotExist:
            return Response({
                "success": False,
                "message": f"CPU data not found for server UUID: {server_uuid}"
            }, status=404)
        except Exception as e:
            return Response({
                "error": "Failed to retrieve CPU data",
                "details": str(e)
            }, status=500)