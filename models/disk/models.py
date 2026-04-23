from django.db import models

class Disk(models.Model):
    UuidServer = models.CharField()
    MAX_SWAP = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальный объем SWAP памяти")
    MAX_DISK = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальный объем дискового пространства")
    DISK_NAME = models.CharField(max_length=255, null=True, blank=True)
