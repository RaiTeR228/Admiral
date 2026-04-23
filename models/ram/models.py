from django.db import models
class Cpu(models.Model):
    MAX_RAM = models.CharField(max_length=255, null=True, blank=True)
    RAM_CHARACTERISTICS = models.CharField(max_length=255, null=True, blank=True)