from django.contrib import admin
from .models import InfoPage

@admin.register(InfoPage)
class InfoPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title')
    prepopulated_fields = {'slug': ('title',)}
    # prepopulated_fields = {"title","slug"}