# serializers.py
from rest_framework import serializers
from .models import SSHLogEntry

class SSHLogEntrySerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = SSHLogEntry
        fields = ['id', 'event_type', 'event_type_display', 'username', 
                  'ip_address', 'timestamp', 'raw_log']