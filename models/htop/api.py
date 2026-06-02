# apps/htop/api.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Htop
from server.models import Server
from django.db.models import Avg, Max, Min
from datetime import datetime, timedelta


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


class HtopMetricsView(APIView):
    """API для приема и сохранения данных о процессах (htop)"""
    # permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # 1. Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # 2. Получаем данные о процессах
            processes_data = request.data.get("processes", [])
            
            # Проверка, что данные о процессах переданы
            if not processes_data:
                return Response({
                    "error": "Processes data required",
                    "details": "Please provide 'processes' field with list of processes"
                }, status=400)
            
            # 3. Очищаем старые записи для этого сервера (опционально)
            # Можно хранить последние N записей или очищать по времени
            old_records = Htop.objects.filter(
                UuidServer=str(server.uuid)
            )
            
            # Ограничиваем количество записей на сервер (например, храним последние 500)
            max_records_per_server = 500
            if old_records.count() > max_records_per_server:
                # Удаляем самые старые записи
                records_to_delete = old_records.order_by('created_at')[:old_records.count() - max_records_per_server]
                records_to_delete.delete()
            
            # 4. Сохраняем данные о процессах
            saved_processes = []
            for proc in processes_data:
                # Валидация данных процесса
                pid = proc.get("pid")
                proccess_name = proc.get("name", "")
                cpu_usage = proc.get("cpu_percent", 0.0)
                
                if pid is None:
                    continue  # Пропускаем процессы без PID
                
                # Создаем запись процесса
                htop_instance = Htop.objects.create(
                    pid=pid,
                    proccess_name=proccess_name,
                    cpu_usage=float(cpu_usage),
                    UuidServer=str(server.uuid)
                )
                
                saved_processes.append({
                    "id": htop_instance.id,
                    "pid": pid,
                    "name": proccess_name,
                    "cpu_usage": float(cpu_usage)
                })
            
            return Response({
                "success": True,
                "message": f"Process metrics saved successfully",
                "server_id": server.id,
                "server_uuid": str(server.uuid),
                "processes_count": len(saved_processes),
                "processes": saved_processes[:10]  # Возвращаем только первые 10 для краткости
            }, status=201)
            
        except Exception as e:
            return Response({
                "error": "Failed to save process metrics",
                "details": str(e)
            }, status=500)
    
    def get(self, request):
        """Получение последних данных о процессах по API ключу"""
        try:
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Получаем последние записи процессов для сервера (топ по CPU)
            processes = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by( '-cpu_usage')[:20]  # Последние 20 процессов с высоким CPU
            
            if processes.exists():
                process_list = []
                for proc in processes:
                    process_list.append({
                        "pid": proc.pid,
                        "name": proc.proccess_name,
                        "cpu_usage": proc.cpu_usage,
                        "created_at": proc.created_at
                    })
                
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "processes_count": len(process_list),
                    "processes": process_list
                })
            else:
                return Response({
                    "success": False,
                    "message": "Process data not found for this server"
                }, status=404)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class HtopHistoryView(APIView):
    """Получение истории измерений процессов"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение истории процессов по API ключу с пагинацией"""
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
            
            # Фильтрация по PID (опционально)
            pid_filter = request.GET.get('pid')
            processes_query = Htop.objects.filter(UuidServer=str(server.uuid))
            
            if pid_filter:
                try:
                    processes_query = processes_query.filter(pid=int(pid_filter))
                except ValueError:
                    pass
            
            # Получаем историю процессов
            processes_history = processes_query.order_by('-created_at')[offset:offset+limit]
            
            # Подсчет общего количества записей
            total_count = processes_query.count()
            
            data = []
            for proc in processes_history:
                data.append({
                    "id": proc.id,
                    "pid": proc.pid,
                    "process_name": proc.proccess_name,
                    "cpu_usage": proc.cpu_usage,
                    "created_at": proc.created_at
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


class HtopTopProcessesView(APIView):
    """Получение топ процессов по CPU usage"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение топ N процессов с наибольшим использованием CPU"""
        try:
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Параметр top_n (сколько процессов показать)
            try:
                top_n = min(int(request.GET.get('top', 10)), 50)  # Максимум 50 процессов
            except (TypeError, ValueError):
                top_n = 10
            
            # Получаем топ процессов по CPU usage из последних записей
            # Сначала получаем последние уникальные процессы по времени
            latest_timestamp = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).values('created_at').order_by('-created_at').first()
            
            if latest_timestamp:
                latest_processes = Htop.objects.filter(
                    UuidServer=str(server.uuid),
                    created_at=latest_timestamp['created_at']
                ).order_by('-cpu_usage')[:top_n]
                
                process_list = []
                for proc in latest_processes:
                    process_list.append({
                        "pid": proc.pid,
                        "name": proc.proccess_name,
                        "cpu_usage": proc.cpu_usage,
                        "created_at": proc.created_at
                    })
                
                return Response({
                    "success": True,
                    "server_uuid": str(server.uuid),
                    "top_count": top_n,
                    "timestamp": latest_timestamp['created_at'],
                    "processes": process_list
                })
            else:
                return Response({
                    "success": False,
                    "message": "No process data found for this server"
                }, status=404)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class HtopProcessStatsView(APIView):
    """Статистика по процессам для сервера"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Получение статистики процессов (средний CPU, максимальный и т.д.)"""
        try:
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Получаем статистику по CPU usage
            stats = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).aggregate(
                max_cpu=Max('cpu_usage'),
                avg_cpu=Avg('cpu_usage')
            )
            
            # Получаем процесс с максимальным CPU
            max_cpu_process = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).order_by('-cpu_usage').first()
            
            # Получаем общее количество уникальных процессов
            unique_processes = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).values('proccess_name').distinct().count()
            
            # Получаем общее количество записей
            total_measurements = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).count()
            
            # Статистика по последнему измерению
            latest_timestamp = Htop.objects.filter(
                UuidServer=str(server.uuid)
            ).values('created_at').order_by('-created_at').first()
            
            latest_processes_count = 0
            if latest_timestamp:
                latest_processes_count = Htop.objects.filter(
                    UuidServer=str(server.uuid),
                    created_at=latest_timestamp['created_at']
                ).count()
            
            response_data = {
                "success": True,
                "server_uuid": str(server.uuid),
                "statistics": {
                    "max_cpu_usage": round(stats['max_cpu'], 2) if stats['max_cpu'] is not None else None,
                    "average_cpu_usage": round(stats['avg_cpu'], 2) if stats['avg_cpu'] is not None else None,
                    "unique_processes_count": unique_processes,
                    "total_measurements": total_measurements,
                    "latest_measurement_time": latest_timestamp['created_at'] if latest_timestamp else None,
                    "latest_processes_count": latest_processes_count,
                    "top_cpu_process": {
                        "pid": max_cpu_process.pid if max_cpu_process else None,
                        "name": max_cpu_process.proccess_name if max_cpu_process else None,
                        "cpu_usage": max_cpu_process.cpu_usage if max_cpu_process else None
                    } if max_cpu_process else None
                }
            }
            
            return Response(response_data)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class HtopProcessSearchView(APIView):
    """Поиск процессов по имени"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Поиск процессов по имени (частичное совпадение)"""
        try:
            # Проверяем API ключ и получаем сервер
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Получаем поисковый запрос
            query = request.GET.get('q', '')
            if not query:
                return Response({
                    "error": "Search query required",
                    "details": "Please provide 'q' parameter for search"
                }, status=400)
            
            # Параметры пагинации
            try:
                limit = min(int(request.GET.get('limit', 50)), 200)
                offset = max(int(request.GET.get('offset', 0)), 0)
            except (TypeError, ValueError):
                limit = 50
                offset = 0
            
            # Поиск процессов по имени (частичное совпадение, регистронезависимый)
            processes = Htop.objects.filter(
                UuidServer=str(server.uuid),
                proccess_name__icontains=query
            ).order_by('-created_at', '-cpu_usage')[offset:offset+limit]
            
            total_count = Htop.objects.filter(
                UuidServer=str(server.uuid),
                proccess_name__icontains=query
            ).count()
            
            data = []
            for proc in processes:
                data.append({
                    "id": proc.id,
                    "pid": proc.pid,
                    "name": proc.proccess_name,
                    "cpu_usage": proc.cpu_usage,
                    "created_at": proc.created_at
                })
            
            return Response({
                "success": True,
                "server_uuid": str(server.uuid),
                "query": query,
                "total_count": total_count,
                "returned_count": len(data),
                "offset": offset,
                "limit": limit,
                "processes": data
            })
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class HtopCleanupView(APIView):
    """Очистка старых записей процессов (только для админов)"""
    permission_classes = [IsAdminUser]
    
    def delete(self, request):
        """Удаление старых записей процессов"""
        try:
            # Параметры: удалить записи старше N дней
            days = int(request.GET.get('days', 7))  # По умолчанию 7 дней для процессов
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Удаляем старые записи
            deleted_count, _ = Htop.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            
            return Response({
                "success": True,
                "message": f"Deleted {deleted_count} process records older than {days} days",
                "deleted_count": deleted_count,
                "days_old": days
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)