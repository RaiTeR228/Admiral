from django.db import models

class Temp(models.Model):
    # 'acpitz': [shwtemp(label='', current=47.0, high=None, critical=None)]
    current_temp = models.FloatField(help_text="Temperature Celsius", null=True, blank=True)
    status_critical = models.BooleanField(null=True, blank=True)
    temp_for_core = models.

    UuidServer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)