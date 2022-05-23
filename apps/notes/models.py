from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

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
        blank=True,
        verbose_name=_('content')
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
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

    updated_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        verbose_name=_('update time')
    )

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return _('"{}" of {}').format(self.title, self.user)


class Deletion(UUIDModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deletions',
        verbose_name=_('user'),
    )
    note_static_id = models.UUIDField(verbose_name=_('note id'))
    note = models.ForeignKey(
        Note,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deletions',
        verbose_name=_('note'),
    )
    deleted_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        verbose_name=_('deletion time')
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        verbose_name=_('deletion creation time')
    )

    class Meta:
        verbose_name = _("Deletion")
        verbose_name_plural = _("Deletions")

    def __str__(self):
        return _('Note {} of {}').format(
            f'<{self.note_static_id}>' if not self.note else f'"{self.note.title}"',
            self.user
        )
