# apps/temp/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Temp
from server.models import Server  # Предполагается, что у вас есть модель Server



# TempMetricsView - для POST (сохранение температуры) и GET (получение последней температуры)

# TempHistoryView - для получения истории измерений с пагинацией

# TempListView - админский эндпоинт для просмотра всех записей

# TempStatsView - для получения статистики (мин, макс, средняя температура)

class TempMetricsView(APIView):
    """API для приема и сохранения данных о температуре"""
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
            
            # 3. Получаем данные о температуре из запроса
            temp_data = {
                'temp': request.data.get("temp"),
            }
            
            # Проверка, что температура передана
            if temp_data['temp'] is None:
                return Response({
                    "error": "Temperature data required",
                    "details": "Please provide 'temp' field"
                }, status=400)
            
            # 4. Создаем новую запись температуры (каждое измерение сохраняется отдельно)
            temp_instance = Temp.objects.create(
                temp=temp_data['temp'],
                UuidServer=str(server.uuid)  # Преобразуем UUID в строку
            )
            
            return Response({
                "success": True,
                "message": "Temperature metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "temp_id": temp_instance.id,
                "data": {
                    "temperature": temp_data['temp'],
                    "created_at": temp_instance.created_at
                }
            }, status=201)
            
        except Exception as e:
            return Response({
                "error": "Failed to save temperature metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение последних данных о температуре по API ключу"""
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')
            
            if not api_key:
                return Response({"error": "API key required"}, status=401)
            
            server = Server.objects.get(api_key=api_key)
            
            # Получаем последнюю запись температуры для сервера
            temp_data = Temp.objects.filter(UuidServer=str(server.uuid)).order_by('-created_at').first()
            
            if temp_data:
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "temperature": {
                        "temp": temp_data.temp,
                        "created_at": temp_data.created_at
                    }
                })
            else:
                return Response({
                    "success": False,
                    "message": "Temperature data not found for this server"
                }, status=404)
                
        except Server.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempHistoryView(APIView):
    """Получение истории измерений температуры"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение истории температуры по API ключу с возможной фильтрацией по дате"""
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')
            
            if not api_key:
                return Response({"error": "API key required"}, status=401)
            
            server = Server.objects.get(api_key=api_key)
            
            # Параметры пагинации
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            
            # Получаем историю температуры для сервера
            temp_history = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by('-created_at')[offset:offset+limit]
            
            # Подсчет общего количества записей
            total_count = Temp.objects.filter(UuidServer=str(server.uuid)).count()
            
            data = []
            for temp in temp_history:
                data.append({
                    "id": temp.id,
                    "temp": temp.temp,
                    "created_at": temp.created_at
                })
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "total_count": total_count,
                "returned_count": len(data),
                "offset": offset,
                "limit": limit,
                "history": data
            })
                
        except Server.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempListView(APIView):
    """Получение списка всех температурных записей (только для админов)"""
    permission_classes = [AllowAny]  # Измените на IsAdminUser при необходимости
    
    def get(self, request):
        try:
            # Проверка админского ключа (опционально)
            admin_key = request.headers.get('X-Admin-Key')
            if admin_key != getattr(settings, 'INSTALL_TOKEN', None):
                return Response({"error": "Admin access required"}, status=403)
            
            # Параметры пагинации
            limit = int(request.GET.get('limit', 100))
            offset = int(request.GET.get('offset', 0))
            
            temps = Temp.objects.all().order_by('-created_at')[offset:offset+limit]
            total_count = Temp.objects.all().count()
            
            data = []
            for temp in temps:
                data.append({
                    "id": temp.id,
                    "temp": temp.temp,
                    "server_uuid": temp.UuidServer,
                    "created_at": temp.created_at
                })
            
            return Response({
                "success": True,
                "total_count": total_count,
                "returned_count": len(data),
                "offset": offset,
                "limit": limit,
                "temperatures": data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempStatsView(APIView):
    """Статистика по температуре для сервера"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение статистики температуры (мин, макс, средняя)"""
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')
            
            if not api_key:
                return Response({"error": "API key required"}, status=401)
            
            server = Server.objects.get(api_key=api_key)
            
            from django.db.models import Avg, Max, Min
            
            # Получаем статистику по температуре
            stats = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).aggregate(
                min_temp=Min('temp'),
                max_temp=Max('temp'),
                avg_temp=Avg('temp')
            )
            
            # Получаем последнее измерение
            last_measurement = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by('-created_at').first()
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "statistics": {
                    "min_temperature": stats['min_temp'],
                    "max_temperature": stats['max_temp'],
                    "average_temperature": round(stats['avg_temp'], 2) if stats['avg_temp'] else None,
                    "last_temperature": last_measurement.temp if last_measurement else None,
                    "last_measurement_time": last_measurement.created_at if last_measurement else None,
                    "total_measurements": Temp.objects.filter(UuidServer=str(server.uuid)).count()
                }
            })
                
        except Server.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=500)