from django.db import models

class Uptime(models.Model):
    server_uuid = models.CharField(max_length=255)
    uptime = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)