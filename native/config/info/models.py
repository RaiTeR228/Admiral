from django.db import models

class InfoPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title