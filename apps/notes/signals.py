from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.notes.models import Note


@receiver(pre_save, sender=Note)
def update_data_sizes(sender, instance, **kwargs):
    old_size = getattr(Note.objects.filter(id=instance.id).first(), 'data_size', 0)
    delta_size = instance.data_size - old_size

    user = instance.user

    if (user.used_data_size + delta_size) > user.max_data_size:
        raise ValidationError({
            "data_size": _("The user has exceeded data size limit")
        })

    user.used_data_size += delta_size
    user.save()
