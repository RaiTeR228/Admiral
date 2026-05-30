# models.py
from django.db import models

class Htop(models.Model):
    pid = models.IntegerField()
    proccess_name = models.CharField(max_length=255)
    cpu_usage = models.FloatField()
    UuidServer = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at', '-cpu_usage']
        indexes = [
            models.Index(fields=['UuidServer', 'created_at']),
            models.Index(fields=['proccess_name']),
            models.Index(fields=['pid']),
        ]
    
    def __str__(self):
        return f"PID: {self.pid} - {self.proccess_name} - CPU: {self.cpu_usage}%"