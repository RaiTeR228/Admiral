# apps/servers/models.py

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
    
# class List_Ssh(models.Model):
#     # Accepted password for root from 192.168.1.219 port 37327 ssh2
#     # 2026-03-27T17:28:10.658373+00:00 Scan-ingram sshd[19328]: Failed password for root from 192.168.1.219 port 37625 ssh2
#     # 2026-03-27T17:28:10.658373+00:00 Scan-ingram sshd[19328]: Failed password for root from 192.168.1.219 port 37625 ssh2
#     # 2026-03-27T17:28:59.002414+00:00 Scan-ingram sshd[19328]: message repeated 2 times: [ Failed password for root from 192.168.1.219 port 37625 ssh2]
#     # 2026-03-27T17:28:59.666846+00:00 Scan-ingram sshd[19328]: Connection reset by authenticating user root 192.168.1.219 port 37625 [preauth]
#     # 2026-03-27T17:28:59.667394+00:00 Scan-ingram sshd[19328]: PAM 2 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.1.219  user=root

#     server = models.CharField(max_length=255)
#     timestamp = models.DateTimeField()
#     ip = models.GenericIPAddressField()
#     port = models.IntegerField()
#     username = models.CharField(max_length=255)
#     status = models.CharField(max_length=255)  # "Accepted" or "Failed"
#     full_message_log = models.TextField() # полный текст из лога
