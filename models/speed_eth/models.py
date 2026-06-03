from django.db import models
from server.models import Server

class SpeedEth(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE,null=True, blank=True)
    
    Interface_name = models.CharField(max_length=255, help_text="Название сетевого интерфейса", default="")
    Eth_sent = models.BigIntegerField(help_text="скорость интернета(отправлено)(bytes)", default=0)
    Eth_recv = models.BigIntegerField(help_text="скорость интернета(получено)(bytes)", default=0)
    Bytes_total_sent = models.BigIntegerField(help_text="Количесво пакетов в байтах, отправленных сервером(bytes)", default=0)
    Bytes_total_recv = models.BigIntegerField(help_text="Количесво пакетов в байтах, полученных сервером(bytes)", default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['server', 'created_at'], name='unique_server_stat')
    #     ]