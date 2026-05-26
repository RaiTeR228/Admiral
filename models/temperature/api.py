# apps/temp/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Temp
from server.models import Server
from django.db.models import Avg, Max, Min


def get_server_from_api_key(request):
    """Вспомогательная функция для получения сервера по API ключу"""
    api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
    if not api_key:
        api_key = request.headers.get('X-API-Key', '')
    
    if not api_key:
        return None, Response({
            "error": "API key required",
            "details": "Please provide API key in Authorization header"
        }, status=401)
    
    try:
        server = Server.objects.get(api_key=api_key)
        return server, None
    except Server.DoesNotExist:
        return None, Response({
            "error": "Invalid API key",
            "details": "No server found with this API key"
        }, status=401)


class TempMetricsView(APIView):
    """API для приема и сохранения данных о температуре"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # 1. Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # 2. Получаем и валидируем данные о температуре
            current_temp_raw = request.data.get("current_temp")
            
            # Проверка, что температура передана
            if current_temp_raw is None:
                return Response({
                    "error": "Temperature data required",
                    "details": "Please provide 'current_temp' field"
                }, status=400)
            
            # Валидация числового значения температуры
            try:
                current_temp = float(current_temp_raw)
            except (TypeError, ValueError):
                return Response({
                    "error": "Invalid temperature value",
                    "details": "current_temp must be a number"
                }, status=400)
            
            # 3. Обработка status_critical (опциональное поле)
            status_critical_raw = request.data.get("status_critical")
            if status_critical_raw is not None:
                # Приводим к 0 или 1 (булево значение)
                try:
                    status_critical = 1 if status_critical_raw else 0
                except Exception:
                    status_critical = 0
            else:
                status_critical = None
            
            # 4. Создаем новую запись температуры
            temp_instance = Temp.objects.create(
                current_temp=current_temp,
                status_critical=status_critical,
                UuidServer=str(server.uuid)
            )
            
            return Response({
                "success": True,
                "message": "Temperature metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "temp_id": temp_instance.id,
                "data": {
                    "current_temp": current_temp,
                    "status_critical": temp_instance.status_critical,
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
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Получаем последнюю запись температуры для сервера
            temp_data = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by('-created_at').first()
            
            if temp_data:
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "temperature": {
                        "current_temp": temp_data.current_temp,
                        "status_critical": temp_data.status_critical,
                        "created_at": temp_data.created_at
                    }
                })
            else:
                return Response({
                    "success": False,
                    "message": "Temperature data not found for this server"
                }, status=404)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempHistoryView(APIView):
    """Получение истории измерений температуры"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение истории температуры по API ключу с пагинацией"""
        try:
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Параметры пагинации с валидацией
            try:
                limit = min(int(request.GET.get('limit', 50)), 200)  # Максимум 200 записей
                offset = max(int(request.GET.get('offset', 0)), 0)
            except (TypeError, ValueError):
                limit = 50
                offset = 0
            
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
                    "temp": temp.current_temp,
                    "status_critical": temp.status_critical,
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
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempListView(APIView):
    """Получение списка всех температурных записей (только для админов)"""
    permission_classes = [IsAdminUser]  # Только для аутентифицированных админов
    
    def get(self, request):
        try:
            # Параметры пагинации с валидацией
            try:
                limit = min(int(request.GET.get('limit', 100)), 500)  # Максимум 500 записей
                offset = max(int(request.GET.get('offset', 0)), 0)
            except (TypeError, ValueError):
                limit = 100
                offset = 0
            
            # Фильтрация по серверу (опционально)
            server_uuid = request.GET.get('server_uuid')
            temps_query = Temp.objects.all()
            if server_uuid:
                temps_query = temps_query.filter(UuidServer=server_uuid)
            
            temps = temps_query.order_by('-created_at')[offset:offset+limit]
            total_count = temps_query.count()
            
            data = []
            for temp in temps:
                data.append({
                    "id": temp.id,
                    "temp": temp.current_temp,
                    "status_critical": temp.status_critical,
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
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Получаем статистику по температуре
            stats = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).aggregate(
                min_temp=Min('current_temp'),
                max_temp=Max('current_temp'),
                avg_temp=Avg('current_temp')
            )
            
            # Получаем последнее измерение
            last_measurement = Temp.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by('-created_at').first()
            
            # Получаем количество критических состояний
            critical_count = Temp.objects.filter(
                UuidServer=str(server.uuid),
                status_critical=1
            ).count()
            
            # Формируем ответ с проверкой на None
            response_data = {
                "success": True,
                "server_uuid": str(server.uuid),
                "statistics": {
                    "min_temperature": stats['min_temp'],
                    "max_temperature": stats['max_temp'],
                    "average_temperature": round(stats['avg_temp'], 2) if stats['avg_temp'] is not None else None,
                    "last_temperature": last_measurement.current_temp if last_measurement else None,
                    "last_measurement_time": last_measurement.created_at if last_measurement else None,
                    "total_measurements": Temp.objects.filter(UuidServer=str(server.uuid)).count(),
                    "critical_events_count": critical_count
                }
            }
            
            return Response(response_data)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class TempCleanupView(APIView):
    """Очистка старых записей температуры (только для админов)"""
    permission_classes = [IsAdminUser]
    
    def delete(self, request):
        """Удаление старых записей температуры"""
        try:
            # Параметры: удалить записи старше N дней
            days = int(request.GET.get('days', 30))
            
            from django.utils import timezone
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=days)
            
            # Удаляем старые записи
            deleted_count, _ = Temp.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            return Response({
                "success": True,
                "message": f"Deleted {deleted_count} temperature records older than {days} days",
                "deleted_count": deleted_count,
                "days_old": days
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)