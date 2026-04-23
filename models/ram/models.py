from django.db import models
class Cpu(models.Model):
    UuidServer = models.CharField()
    MAX_RAM = models.CharField(max_length=255, null=True, blank=True)
    RAM_CHARACTERISTICS = models.CharField(max_length=255, null=True, blank=True)