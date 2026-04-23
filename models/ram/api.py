# apps/servers/api.py

import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from .models import Server

INSTALL_TOKEN = "SUPER_SECRET_123"  # потом вынесешь в settings


class RegisterServerView(APIView):
    def post(self, request):
        if request.data.get("install_token") != INSTALL_TOKEN:
            return Response({"error": "Invalid install token"}, status=403)

        name = request.data.get("name")
        
        # Пытаемся найти существующий сервер по имени
        server, created = Server.objects.update_or_create(
            name=name,  # условие для поиска
            defaults={  # значения для обновления или создания
                
                "MAX_RAM": request.data.get("MAX_RAM"),
                "RAM_CHARACTERISTICS": request.data.get("RAM_CHARACTERISTICS"),
                "DISK_NAME": request.data.get("DISK_NAME"),
                "UuidServer": request.data.get("UuidServer"),
            }
        )
        
        # Если сервер только что создан, генерируем api_key
        if created:
            server.api_key = secrets.token_hex(32)
            server.save()
            message = "Server created"
        else:
            message = "Server updated"
        
        return Response({
            "message": message,
            "server_id": server.id,
            "api_key": server.api_key,
            "MAX_RAM": server.MAX_RAM,
            "RAM_CHARACTERISTICS": server.RAM_CHARACTERISTICS,
            "UuidServer": server.UuidServer,
        })