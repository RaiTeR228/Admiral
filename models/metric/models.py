# apps/metric/models.py

from django.db import models
from server.models import Server

class ServerStat(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE,null=True, blank=True)
    # server = models.IntegerField(null=True, blank=True)
   
    Use_Cpu = models.IntegerField(help_text="CPU(%)")#,null=True, blank=True
    Use_Ram = models.IntegerField(help_text="RAM(%)")
    Use_Swap = models.IntegerField(help_text="SWAP")
    # IO = models.FloatField(help_text="Input/Output(%)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['server', 'created_at'], name='unique_server_stat')
        ]