from django.db import models
class Ram(models.Model):
    id = models.AutoField(primary_key=True)
    UuidServer = models.CharField(max_length=255)
    MAX_RAM = models.CharField(max_length=255, null=True, blank=True)