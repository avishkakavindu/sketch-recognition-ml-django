from django.db import models


class Label(models.Model):
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='label_images')

    def __str__(self):
        return self.name