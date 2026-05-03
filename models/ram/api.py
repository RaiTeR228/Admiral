# apps/cpu/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Ram
from server.models import Server 

class RamMetricsView(APIView):
    """API для приема и сохранения данных о RAM"""
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
            
            # 3. Получаем данные о RAM из запроса
            ram_data = {
                'MAX_RAM': request.data.get("MAX_RAM"),
            }
            
            # 4. Сохраняем или обновляем данные RAM
            ram_instance, created = Ram.objects.update_or_create(
                UuidServer=server.uuid,
                defaults=ram_data
            )
            
            return Response({
                "success": True,
                "message": "RAM metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "ram_id": ram_instance.id,
                "is_new": created,
                "data": {
                    "max_ram": ram_data['MAX_RAM'],
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
                ram_data = Ram.objects.get(UuidServer=server.uuid)
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "ram": {
                        "max_ram": ram_data.MAX_RAM,
                        "local_name": ram_data.Local_Name_PC,
                        "created_at": ram_data.created_at,
                        "updated_at": ram_data.updated_at
                    }
                })
            except Ram.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "RAM data not found for this server"
                }, status=404)
                
        except Server.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class RAMListView(APIView):
    """Получение списка всех RAM (только для админов)"""
    permission_classes = [AllowAny]  # Измените на IsAdminUser при необходимости
    
    def get(self, request):
        try:
            # Проверка админского ключа (опционально)
            admin_key = request.headers.get('X-Admin-Key')
            if admin_key != settings.INSTALL_TOKEN:  # Настройте в settings.py
                return Response({"error": "Admin access required"}, status=403)
            
            rams = Ram.objects.all().select_related('UuidServer')
            data = []
            for ram in rams:
                data.append({
                    "id": ram.id,
                    "server_uuid": ram.UuidServer,
                    "created_at": ram.created_at,
                    "updated_at": ram.updated_at
                })
            
            return Response({
                "success": True,
                "count": len(data),
                "rams": data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)