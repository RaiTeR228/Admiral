from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True) # ip будет скорее динамичным и не будет в бд храниться, но на всякий случай добавим

    SystemPC = models.CharField(max_length=100,null=True, blank=True, help_text="Система пк")
    Local_Name_PC = models.CharField(max_length=100,null=True, blank=True, help_text="Локальное имя пк")
    # Release = models.IntegerField()
    
    MAX_CPU_CORES = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество ядер CPU")
    MAX_CPU_THREADS = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальное количество потоков CPU")
    CPU_NAME = models.CharField(max_length=255, null=True, blank=True)
    
    MAX_RAM = models.CharField(max_length=255, null=True, blank=True)
    RAM_CHARACTERISTICS = models.CharField(max_length=255, null=True, blank=True)
    
    MAX_GPU_THREADS = models.CharField(max_length=255, null=True, blank=True)
    GPU_NAME = models.CharField(max_length=255, null=True, blank=True)
    GPU_SIZE_GB = models.CharField(max_length=255, null=True, blank=True)

    MAX_SWAP = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальный объем SWAP памяти")
    MAX_DISK = models.CharField(max_length=255, null=True, blank=True, help_text="Максимальный объем дискового пространства")
    DISK_NAME = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name