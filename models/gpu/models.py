from django.db import models
class gpu(models.Model):
    UuidServer = models.CharField()
    MAX_GPU_THREADS = models.CharField(max_length=255, null=True, blank=True)
    GPU_NAME = models.CharField(max_length=255, null=True, blank=True)
    GPU_SIZE_GB = models.CharField(max_length=255, null=True, blank=True)
