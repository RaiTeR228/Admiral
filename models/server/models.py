from django.db import models
import uuid

class Server(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ip = models.GenericIPAddressField(null=True, blank=True) # ip будет скорее динамичным и не будет в бд храниться, но на всякий случай добавим
    SystemPC = models.CharField(max_length=100,null=True, blank=True, help_text="Система пк")
    Local_Name_PC = models.CharField(max_length=100,null=True, blank=True, help_text="Локальное имя пк")

    def __str__(self):
        return self.name