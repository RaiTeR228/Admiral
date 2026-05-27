from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import InfoPage
from .serializers import InfoPageSerializer

class InfoPageViewSet(ReadOnlyModelViewSet):
    queryset = InfoPage.objects.all()
    serializer_class = InfoPageSerializer
    lookup_field = 'slug'