from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.common.models import UUIDModel

User = get_user_model()


class Tag(UUIDModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('user')
    )
    text = models.CharField(
        max_length=32,
        verbose_name=_('text')
    )

    def __str__(self):
        return f'"{self.text}" of {self.user}'


class Note(UUIDModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('user'),
    )
    title = models.CharField(
        max_length=256,
        verbose_name=_('title')
    )
    content = models.TextField(
        max_length=524288,
        verbose_name=_('content')
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name=_('color')
    )
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_('icon name')
    )
    data_size = models.IntegerField(
        default=0,
        verbose_name=_('data size')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name=_('tags')
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return f'"{self.title}" of {self.user}'
