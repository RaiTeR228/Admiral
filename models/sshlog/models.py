from django.db import models

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


# models.py
from django.db import models
from django.utils import timezone

class SSHLogEntry(models.Model):
    EVENT_TYPES = (
        ('success', 'Успешный вход'),
        ('failed', 'Неудачная попытка'),
    )
    
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    raw_log = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.username} from {self.ip_address} at {self.timestamp}"