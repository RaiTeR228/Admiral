from django.db import models
class Cpu(models.Model):
    MAX_CPU_CORES = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество ядер CPU")
    MAX_CPU_THREADS = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество потоков CPU")
    CPU_NAME = models.CharField(max_length=255, null=True, blank=True)
