from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.common.models import UUIDModel


class User(AbstractUser, UUIDModel):
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('email')
    )

    used_data_size = models.IntegerField(
        default=0,
        verbose_name=_('used data size')
    )
    max_data_size = models.IntegerField(
        default=1048576,
        verbose_name=_('allowed data size')
    )
    lang = models.CharField(
        max_length=10,
        default='en-us',
        verbose_name=_('language')
    )
