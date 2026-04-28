# apps/servers/api.py

import secrets
import hashlib
import hmac
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.core.cache import cache
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .models import Server

# В settings.py лучше добавить:
# INSTALL_TOKEN = os.getenv('INSTALL_TOKEN', secrets.token_hex(32))
# REGISTRATION_TIMEOUT = 3600  # 1 час

class RegisterServerView(APIView):
    """Регистрация нового сервера с получением API токена"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # 1. Проверка install_token
            install_token = request.data.get("install_token")
            if not install_token:
                return Response({
                    "error": "install_token is required",
                    "details": "Please provide valid installation token"
                }, status=400)
            
            if install_token != settings.INSTALL_TOKEN:
                return Response({
                    "error": "Invalid install token",
                    "details": "The installation token is incorrect"
                }, status=403)
            
            # 2. Получаем данные сервера
            name = request.data.get("name")
            if not name:
                return Response({
                    "error": "Server name is required"
                }, status=400)
            
            # Валидация имени сервера
            if len(name) < 3 or len(name) > 255:
                return Response({
                    "error": "Server name must be between 3 and 255 characters"
                }, status=400)
            
            # 3. Получаем IP адрес (из запроса или из данных)
            ip = request.data.get("ip") or self.get_client_ip(request)
            
            # 4. Дополнительная информация о сервере
            system_pc = request.data.get("system_pc")
            local_name_pc = request.data.get("local_name_pc")
            
            # 5. Проверяем, не зарегистрирован ли уже сервер с таким именем
            existing_server = Server.objects.filter(name=name).first()
            
            if existing_server:
                # Обновляем существующий сервер
                existing_server.ip = ip
                if system_pc:
                    existing_server.SystemPC = system_pc
                if local_name_pc:
                    existing_server.Local_Name_PC = local_name_pc
                existing_server.save()
                
                return Response({
                    "success": True,
                    "message": "Server updated successfully",
                    "server_id": existing_server.id,
                    "server_uuid": str(existing_server.uuid),
                    "name": existing_server.name,
                    "api_key": existing_server.api_key,
                    "is_new": False,
                    "created_at": existing_server.created_at.isoformat()
                })
            else:
                # Создаем новый сервер
                api_key = self.generate_api_key(name)
                
                server = Server.objects.create(
                    name=name,
                    api_key=api_key,
                    ip=ip,
                    SystemPC=system_pc,
                    Local_Name_PC=local_name_pc
                )
                
                # Сохраняем информацию о регистрации в кэше (опционально)
                cache.set(f"server_registered_{server.id}", True, 3600)
                
                response_data = {
                    "success": True,
                    "message": "Server registered successfully",
                    "server_id": server.id,
                    "server_uuid": str(server.uuid),
                    "name": server.name,
                    "api_key": server.api_key,
                    "is_new": True,
                    "created_at": server.created_at.isoformat(),
                    "instructions": {
                        "how_to_use": "Use this API key in X-API-Key header for all subsequent requests",
                        "example": "curl -H 'X-API-Key: YOUR_API_KEY' http://your-server/api/endpoint/",
                        "endpoints": [
                            "/api/metrics/ - Send server metrics",
                            "/api/status/ - Check server status"
                        ]
                    }
                }
                
                return Response(response_data, status=201)
                
        except Exception as e:
            return Response({
                "error": "Registration failed",
                "details": str(e)
            }, status=500)
    
    def get_client_ip(self, request):
        """Получение реального IP клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def generate_api_key(self, server_name):
        """Генерация уникального API ключа"""
        # Используем имя сервера для создания более читаемого ключа
        base_key = secrets.token_hex(32)
        
        # Добавляем хэш от имени сервера для уникальности
        name_hash = hashlib.sha256(server_name.encode()).hexdigest()[:8]
        
        return f"{base_key[:40]}_{name_hash}"


class GetAPIKeyView(APIView):
    """Получение API ключа для уже зарегистрированного сервера"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        install_token = request.data.get("install_token")
        server_name = request.data.get("name")
        
        if not install_token or not server_name:
            return Response({
                "error": "Both install_token and name are required"
            }, status=400)
        
        if install_token != settings.INSTALL_TOKEN:
            return Response({"error": "Invalid install token"}, status=403)
        
        try:
            server = Server.objects.get(name=server_name)
            return Response({
                "success": True,
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "name": server.name,
                "api_key": server.api_key,
                "created_at": server.created_at.isoformat()
            })
        except ObjectDoesNotExist:
            return Response({
                "error": "Server not found",
                "details": f"No server registered with name '{server_name}'"
            }, status=404)


class RegenerateAPIKeyView(APIView):
    """Перегенерация API ключа"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        install_token = request.data.get("install_token")
        server_name = request.data.get("name")
        
        if not install_token or not server_name:
            return Response({
                "error": "Both install_token and name are required"
            }, status=400)
        
        if install_token != settings.INSTALL_TOKEN:
            return Response({"error": "Invalid install token"}, status=403)
        
        try:
            server = Server.objects.get(name=server_name)
            # Генерируем новый ключ
            new_api_key = secrets.token_hex(32)
            server.api_key = new_api_key
            server.save()
            
            return Response({
                "success": True,
                "message": "API key regenerated successfully",
                "new_api_key": new_api_key,
                "server_id": server.id,
                "server_name": server.name,
                "warning": "Old API key is no longer valid. Update your configuration."
            })
        except ObjectDoesNotExist:
            return Response({
                "error": "Server not found"
            }, status=404)