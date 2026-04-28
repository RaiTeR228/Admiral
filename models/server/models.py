from django.db import models
import uuid

class Server(models.Model):
    id = models.AutoField(primary_key=True)  # явно указываем
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    SystemPC = models.CharField(max_length=100, null=True, blank=True, help_text="Система пк")
    Local_Name_PC = models.CharField(max_length=100, null=True, blank=True, help_text="Локальное имя пк")

    def __str__(self):
        return self.name