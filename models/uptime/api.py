from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Uptime
from server.models import Server 

def get_server_from_request(request):
    auth_header = request.headers.get("Authorization", '')
    
    if not auth_header:
        return None
    
    try:
        prefix, api_key = auth_header.split()
    except ValueError:
        return None
    
    if prefix != "Api-Key":
        return None
    
    try:
        # Ищем в модели Server, а не в Uptime
        return Server.objects.get(api_key=api_key)
    except Server.DoesNotExist:
        return None

class UptimeView(APIView):
    def post(self, request):
        try:
            install_token = request.data.get("INSTALL_TOKEN")
            uptime_seconds = request.data.get("uptime")
            server = get_server_from_request(request)
            
            # Проверка INSTALL_TOKEN (опционально, если нужно)
            if install_token != settings.INSTALL_TOKEN:
                return Response({"error": "Invalid API token"}, status=403)
            
            if not server:
                return Response({"error": "Unauthorized"}, status=403)
            
            if uptime_seconds is None:
                return Response({"error": "uptime is required"}, status=400)
            
            try:
                # Создаем запись uptime, связанную с сервером
                uptime = Uptime.objects.create(
                    server=server,  # связываем с сервером
                    server_uuid=str(server.id),  # или server.name
                    uptime_seconds=uptime_seconds
                )
                
                return Response({"message": "Uptime received successfully"}, status=200)
            
            except Exception as e:
                return Response({"error": str(e)}, status=500)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def get(self, request):
        try:
            server = get_server_from_request(request)
            if not server:
                return Response({"error": "Unauthorized"}, status=403)
            
            # Получаем последние 10 записей uptime для этого сервера
            uptime_records = Uptime.objects.filter(server=server).order_by('-created_at')[:10]
            
            # Сериализуем данные для ответа
            uptime_data = [
                {
                    "uptime_seconds": record.uptime_seconds,
                    "created_at": record.created_at
                }
                for record in uptime_records
            ]
            
            return Response({"uptime": uptime_data}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)