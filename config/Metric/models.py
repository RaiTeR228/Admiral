# apps/monitoring/models.py

from django.db import models
from Server.models import Server

class ServerStat(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE,null=True, blank=True)
    # server = models.IntegerField(null=True, blank=True)
   
    Use_Cpu = models.IntegerField(help_text="CPU(%)",null=True, blank=True)
    Use_Ram = models.IntegerField(help_text="RAM(%)",null=True, blank=True)
    Use_Swap = models.IntegerField(help_text="SWAP",null=True, blank=True)
    IO = models.FloatField(help_text="Input/Output(%)", null=True, blank=True)

    # Cpu_Info = models.IntegerField(help_text="Total CPU Cores", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)