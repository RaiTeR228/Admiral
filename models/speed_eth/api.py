from django.conf import settings
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import SpeedEth
from server.models import Server

def get_server_from_api_key(request):
    """Вспомогательная функция для получения сервера по API ключу"""
    api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
    # if not api_key:
    #     api_key = request.headers.get('X-API-Key', '')
    
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
    
class SpeedEthView(APIView):
    def post(self, request):
        try:
            server, error_response = get_server_from_api_key(request)
            if error_response:
                return error_response
            
            # Забираем данные из headers вместо request.data
            eth_sent = request.headers.get('Eth_Sent')
            eth_recv = request.headers.get('Eth_Recv')
            bytes_total_sent = request.headers.get('Bytes_total_Sent')
            bytes_total_recv = request.headers.get('Bytes_total_Recv')
            
            # Преобразуем в числа
            if eth_sent is not None:
                try:
                    eth_sent = int(eth_sent)
                    eth_recv = int(eth_recv)
                    bytes_total_sent = int(bytes_total_sent)
                    bytes_total_recv = int(bytes_total_recv)
                except (ValueError, TypeError):
                    return Response({
                        "error": "Invalid data types",
                        "details": "All fields must be numbers"
                    }, status=400)
            
            if None in [eth_sent, eth_recv, bytes_total_sent, bytes_total_recv]:
                return Response({
                    "error": "Missing fields",
                    "details": "Please provide Eth_Sent, Eth_Recv, Bytes_total_Sent, and Bytes_total_Recv in headers"
                }, status=400)
            
            SpeedEth.objects.create(
                server=server,
                Eth_sent=eth_sent,
                Eth_recv=eth_recv,
                Bytes_total_sent=bytes_total_sent,
                Bytes_total_recv=bytes_total_recv
            )
            return Response({"message": "SpeedEth data saved successfully"}, status=201)
        except Exception as e:
            return Response({"error": "An error occurred", "details": str(e)}, status=500)
        
    def get(self, request):
        
        server, error_response = get_server_from_api_key(request)

        if not server:
                return Response({"error": "Unauthorized"}, status=403)
            
        try:
            speed_eth_data = SpeedEth.objects.filter(server=server).order_by('-created_at').first()
            if not speed_eth_data:
                return Response({"error": "No SpeedEth data found for this server"}, status=404)
            return Response({
                "Eth_Sent": speed_eth_data.Eth_sent,
                "Eth_Recv": speed_eth_data.Eth_recv,
                "Bytes_total_Sent": speed_eth_data.Bytes_total_sent,
                "Bytes_total_Recv": speed_eth_data.Bytes_total_recv,
                "created_at": speed_eth_data.created_at
            })
        except SpeedEth.DoesNotExist:
            return Response({"error": "No SpeedEth data found for this server"}, status=404)