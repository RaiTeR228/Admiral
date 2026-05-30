# apps/Metric/api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from metric.models import ServerStat
from rest_framework.serializers import ModelSerializer

from server.models import Server
from metric.models import ServerStat


def get_server_from_request(request):
    auth_header = request.headers.get("Authorization",'')

    if not auth_header:
        return None
        # return Response ({
        #     "error":"Api key required",
        #     "details":"Please provide API key in Authorization header"
        # }, status= 401)

    try:
        prefix, api_key = auth_header.split()
    except:
        return None

    if prefix != "Api-Key":
        return None

    try:
        return Server.objects.get(api_key=api_key)
    except Server.DoesNotExist:
        return None
        # return Response ({
        #     "error": "Invalid API key",
        #     "details": "No server found with this API key"
        # }, status=401)

class ReceiveStatsView(APIView):

    def post(self, request):
        server = get_server_from_request(request)

        def clean_percent(value):
            if not value:
                return None  # Возвращаем None, а не Response
            try:
                return float(str(value).replace('%', '').strip())
            except (ValueError, TypeError):
                return None  # При ошибке конвертации тоже возвращаем None

        if not server:
            return Response({"error": "Unauthorized"}, status=403)

        # Очищаем значения
        cpu_value = clean_percent(request.data.get("Use_Cpu"))
        ram_value = clean_percent(request.data.get("Use_Ram"))
        swap_value = clean_percent(request.data.get("Use_Swap"))

        # Проверяем, что значения успешно очищены
        if cpu_value is None or ram_value is None or swap_value is None:
            return Response({
                "error": "Invalid data",
                "details": "CPU, RAM, and Swap values must be valid numbers"
            }, status=400)

        ServerStat.objects.create(
            server=server,
            Use_Cpu=cpu_value, 
            Use_Ram=ram_value,    
            Use_Swap=swap_value,  
            # IO=request.data.get("IO"),
        )

        return Response({"status": "ok"})
    
    def get (self, request):
        server = get_server_from_request(request)

        def clean_percent(value):
            if not value:
                return None  # Возвращаем None, а не Response
            try:
                return float(str(value).replace('%', '').strip())
            except (ValueError, TypeError):
                return None  # При ошибке конвертации тоже возвращаем None

        if not server:
            return Response({"error": "Unauthorized"}, status=403)
        
        try:
            stats = ServerStat.objects.filter(server__id=server.id).order_by('-created_at').first()
            return Response({
                "success":True,
                "id":stats.id,
                "server_id": server.id,
                "Use_Cpu": stats.Use_Cpu,
                "Use_Ram": stats.Use_Ram,
                "Use_Swap": stats.Use_Swap,
                "created_at": stats.created_at
            })
        except ServerStat.DoesNotExist:
            return Response({"error": "No stats found for this server"}, status=404)
        # queryset = ServerStat.objects.all().order_by("-created_at")
        # serializer_class = ServerStatSerializer

    
class ServerStatSerializer(ModelSerializer):
    class Meta:
        model = ServerStat
        fields = "__all__"


class ServerStatListView(ListAPIView):
    queryset = ServerStat.objects.all().order_by("-created_at")
    serializer_class = ServerStatSerializer