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
                # 'Local_Name_PC': request.data.get("Local_Name_PC", server.Local_Name_PC),
                # 'MAX_RAM': request.data.get("MAX_RAM"),
                # 'MAX_SWAP': request.data.get("MAX_SWAP"),
            }
            
            # 4. Сохраняем или обновляем данные CPU
            cpu_instance, created = Cpu.objects.update_or_create(
                UuidServer=server.uuid,
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
                    "threads": cpu_data['MAX_CPU_THREADS']
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
                cpu_data = Cpu.objects.get(UuidServer=server.uuid)
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "cpu": {
                        "name": cpu_data.CPU_NAME,
                        "max_cores": cpu_data.MAX_CPU_CORES,
                        "max_threads": cpu_data.MAX_CPU_THREADS,
                        "max_ram": cpu_data.MAX_RAM,
                        "max_swap": cpu_data.MAX_SWAP,
                        "local_name": cpu_data.Local_Name_PC,
                        "created_at": cpu_data.created_at,
                        "updated_at": cpu_data.updated_at
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
    """Получение списка всех CPU (только для админов)"""
    permission_classes = [AllowAny]  # Измените на IsAdminUser при необходимости
    
    def get(self, request):
        try:
            # Проверка админского ключа (опционально)
            admin_key = request.headers.get('X-Admin-Key')
            if admin_key != settings.INSTALL_TOKEN:  # Настройте в settings.py
                return Response({"error": "Admin access required"}, status=403)
            
            cpus = Cpu.objects.all().select_related('UuidServer')
            data = []
            for cpu in cpus:
                data.append({
                    "id": cpu.id,
                    "server_uuid": cpu.UuidServer,
                    "cpu_name": cpu.CPU_NAME,
                    "cores": cpu.MAX_CPU_CORES,
                    "threads": cpu.MAX_CPU_THREADS,
                    "local_name": cpu.Local_Name_PC,
                    "created_at": cpu.created_at,
                    "updated_at": cpu.updated_at
                })
            
            return Response({
                "success": True,
                "count": len(data),
                "cpus": data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)