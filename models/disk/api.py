from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Disk
from server.models import Server


class DiskMetricsView(APIView):
    """API для приема и сохранения данных о диске"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')

            if not api_key:
                return Response({
                    'error': 'Требуется ключ API',
                    'details': 'Пожалуйста, укажите ключ API в заголовке авторизации'
                }, status=401)

            try:
                server = Server.objects.get(api_key=api_key)
            except Server.DoesNotExist:
                return Response({
                    'error': 'Неверный API ключ',
                    'details': 'Сервер с этим API-ключом не найден'
                }, status=401)

            disk_data = {
                'MAX_SWAP': request.data.get('MAX_SWAP'),
                'MAX_DISK': request.data.get('MAX_DISK'),
                'DISK_NAME': request.data.get('DISK_NAME'),
                'Free_DISK': request.data.get('Free_DISK'),
            }

            disk_instance, created = Disk.objects.update_or_create(
                UuidServer=server.uuid,
                defaults=disk_data
            )

            return Response({
                'success': True,
                'message': 'Данные диска успешно сохранены',
                'server_id': server.id,
                'server_uuid': str(server.uuid),
                'disk_id': disk_instance.id,
                'is_new': created,
                'data': {
                    'disk_name': disk_data['DISK_NAME'],
                    'max_swap': disk_data['MAX_SWAP'],
                    'max_disk': disk_data['MAX_DISK'],
                    'free_disk': disk_data['Free_DISK'],
                }
            }, status=201 if created else 200)
        except Exception as e:
            return Response({
                'error': 'Ошибка сохранения данных диска',
                'details': str(e)
            }, status=500)

    def get(self, request):
        try:
            api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
            if not api_key:
                api_key = request.headers.get('X-API-Key', '')

            if not api_key:
                return Response({'error': 'требуется API ключ'}, status=401)

            server = Server.objects.get(api_key=api_key)
            try:
                disk_data = Disk.objects.get(UuidServer=server.uuid)
                return Response({
                    'success': True,
                    'server_uuid': str(server.uuid),
                    'disk': {
                        'disk_name': disk_data.DISK_NAME,
                        'max_swap': disk_data.MAX_SWAP,
                        'max_disk': disk_data.MAX_DISK,
                        'free_disk': disk_data.Free_DISK,
                        'server_uuid': disk_data.UuidServer,
                    }
                })
            except Disk.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Данные диска не найдены для этого сервера'
                }, status=404)
        except Server.DoesNotExist:
            return Response({'error': 'Неверный API ключ'}, status=401)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class DiskListView(APIView):
    """Получение списка всех дисков (только для админов)"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            admin_key = request.headers.get('X-Admin-Key')
            if admin_key != settings.INSTALL_TOKEN:
                return Response({'error': 'Требуется доступ администратора'}, status=403)

            disks = Disk.objects.all()
            data = [
                {
                    'id': disk.id,
                    'server_uuid': disk.UuidServer,
                    'max_swap': disk.MAX_SWAP,
                    'max_disk': disk.MAX_DISK,
                    'disk_name': disk.DISK_NAME,
                    'free_disk': disk.Free_DISK,
                }
                for disk in disks
            ]

            return Response({
                'success': True,
                'count': len(data),
                'disks': data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)