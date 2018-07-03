from django.contrib.auth.models import AbstractUser
from django.db import models

from dice_world.standard import create_uuid


class User(AbstractUser):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name
