import uuid
import os
from django.db import models

from core.models import User


def image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'image', filename)


class Image(models.Model):
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(null=False, upload_to=image_file_path)
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
