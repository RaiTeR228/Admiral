from django.db import models
class Cpu(models.Model):
    UuidServer = models.CharField()
    MAX_CPU_CORES = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество ядер CPU")
    MAX_CPU_THREADS = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество потоков CPU")
    CPU_NAME = models.CharField(max_length=255, null=True, blank=True)
    freq = models.FloatField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPUs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.CPU_NAME} - {self.UuidServer}"