# views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db import models
from .models import SSHLogEntry
from .serializers import SSHLogEntrySerializer

class SSHLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра логов SSH подключений
    """
    queryset = SSHLogEntry.objects.all()
    serializer_class = SSHLogEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['event_type', 'username', 'ip_address']
    search_fields = ['username', 'ip_address']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по подключениям"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            'total_success': SSHLogEntry.objects.filter(event_type='success').count(),
            'total_failed': SSHLogEntry.objects.filter(event_type='failed').count(),
            'today_success': SSHLogEntry.objects.filter(
                event_type='success', 
                timestamp__date=today
            ).count(),
            'today_failed': SSHLogEntry.objects.filter(
                event_type='failed',
                timestamp__date=today
            ).count(),
            'week_success': SSHLogEntry.objects.filter(
                event_type='success',
                timestamp__date__gte=week_ago
            ).count(),
            'week_failed': SSHLogEntry.objects.filter(
                event_type='failed',
                timestamp__date__gte=week_ago
            ).count(),
            'top_failed_ips': list(SSHLogEntry.objects.filter(
                event_type='failed'
            ).values('ip_address').annotate(
                count=models.Count('id')
            ).order_by('-count')[:10]),
            'top_usernames': list(SSHLogEntry.objects.values('username').annotate(
                count=models.Count('id')
            ).order_by('-count')[:10]),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def failed_recent(self, request):
        """Недавние неудачные попытки (последние 24 часа)"""
        day_ago = timezone.now() - timedelta(hours=24)
        recent_failed = SSHLogEntry.objects.filter(
            event_type='failed',
            timestamp__gte=day_ago
        )
        serializer = self.get_serializer(recent_failed, many=True)
        return Response(serializer.data)