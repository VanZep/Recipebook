from django.db import models

from .constants import CHARFIELD_MAX_LENGTH


class NameModel(models.Model):
    """Абстрактная модель с общим полем name."""

    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Название'
    )

    class Meta:
        abstract = True
