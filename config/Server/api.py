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
                "MAX_CPU_CORES": request.data.get("MAX_CPU_CORES"),
                "MAX_CPU_THREADS": request.data.get("MAX_CPU_THREADS"),
                "CPU_NAME": request.data.get("CPU_NAME"),
                "MAX_RAM": request.data.get("MAX_RAM"),
                "RAM_CHARACTERISTICS": request.data.get("RAM_CHARACTERISTICS"),
                "MAX_GPU_THREADS": request.data.get("MAX_GPU_THREADS"),
                "GPU_NAME": request.data.get("GPU_NAME"),
                "GPU_SIZE_GB": request.data.get("GPU_SIZE_GB"),
                "MAX_SWAP": request.data.get("MAX_SWAP"),
                "MAX_DISK": request.data.get("MAX_DISK"),
                "DISK_NAME": request.data.get("DISK_NAME"),
                "ip": request.data.get("ip"),
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
            "MAX_CPU_CORES": server.MAX_CPU_CORES,
            "MAX_CPU_THREADS": server.MAX_CPU_THREADS,
            "CPU_NAME": server.CPU_NAME,
            "MAX_RAM": server.MAX_RAM,
            "RAM_CHARACTERISTICS": server.RAM_CHARACTERISTICS,
            "MAX_GPU_THREADS": server.MAX_GPU_THREADS,
            "GPU_NAME": server.GPU_NAME,
            "GPU_SIZE_GB": server.GPU_SIZE_GB,
            "MAX_SWAP": server.MAX_SWAP,
            "MAX_DISK": server.MAX_DISK,
            "DISK_NAME": server.DISK_NAME,
        })