from django.db import models

class Temp(models.Model):
    temp = models.FloatField(help_text="Temperature Celsius")
    UuidServer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)