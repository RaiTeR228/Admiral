from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Uptime

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
        return Uptime.objects.get(api_key=api_key)
    except Uptime.DoesNotExist:
        return None
        # return Response ({
        #     "error": "Invalid API key",
        #     "details": "No server found with this API key"
        # }, status=401)

class UptimeView(APIView):
    def post(self, request):
        try:
            # server_uuid = request.data.get("server_uuid")
            install_token = request.data.get("API_TOKEN")
            uptime_seconds = request.data.get("uptime")
            server = get_server_from_request(request)

            if not server:
                return Response({"error": "Unauthorized"}, status=403)
            if not install_token:
                return Response({"error":"API_TOKEN no api token"}, status=400)
            if install_token != settings.INSTALL_TOKEN:
                return Response({"error":"Invalid API token"}, status=403)
            if uptime_seconds is None:
                return Response({"error":"uptime is required"}, status=400)
            try:
                uptime = Uptime.objects.create(
                    # server_uuid=server_uuid,
                    uptime_seconds=uptime_seconds
                )

                return Response({"message":"Uptime received successfully"}, status=200)

            except Exception as e:
                return Response({"error": str(e)}, status=500)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def get(self, request):
        try:
            server = get_server_from_request(request)
            if not server:
                return Response({"error": "Unauthorized"}, status=403)

            uptime = Uptime.objects.all().order_by('-created_at')[:0]
            return Response({"uptime": uptime}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)