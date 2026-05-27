from rest_framework import serializers
from .models import InfoPage

class InfoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ['id','slug', 'title', 'text']