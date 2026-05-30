from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServerStat  # или ваша модель

@receiver(post_save, sender=ServerStat)
def limit_table_size(sender, instance, **kwargs):
    max_records = 120960
    # Получаем количество записей
    
    count = sender.objects.count()
    print (count)
    
    if count > max_records:
        # Удаляем самые старые записи (кроме последних max_records)
        records_to_delete = count - max_records
        # Получаем ID самых старых записей и удаляем их
        oldest_ids = sender.objects.values_list('id', flat=True).order_by('id')[:records_to_delete]
        sender.objects.filter(id__in=list(oldest_ids)).delete()