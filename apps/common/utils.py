import math

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponsePermanentRedirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import serializers
from urllib.parse import urljoin


class FullUrlFileField(serializers.FileField):
    def to_representation(self, value):
        if value:
            return urljoin(settings.BACKEND_DOMAIN, value.url)
        else:
            return None


class FullUrlImageField(serializers.ImageField):
    def to_representation(self, value):
        if value:
            return urljoin(settings.BACKEND_DOMAIN, value.url)
        else:
            return None


class ActionSerializerClassesMixin:
    """
    Provides 'action_serializer_classes' that allows to specify
        different serializers for certain actions
    """
    action_serializer_classes = {}

    def get_serializer_class(self):
        try:
            return self.action_serializer_classes[self.action]
        except (AttributeError, KeyError):
            return super(ActionSerializerClassesMixin, self).get_serializer_class()


class ActionPermissionClassesMixin:
    """
    Provides 'action_permission_classes' that allows to specify
        different permissions for certain actions
    """
    action_permission_classes = {}

    def get_permissions(self):
        try:
            return [permission() for permission
                    in self.action_permission_classes[self.action]]
        except (AttributeError, KeyError):
            return super(ActionPermissionClassesMixin, self).get_permissions()


def send_mail_contact(subject, user, email, comment):
    send_mail(
        f'{subject}',
            f'Avsändare: {user.first_name} {user.last_name}\n'
            f'{email}\n'
            f'\n{comment}\n',
        settings.SERVER_EMAIL,
        [settings.CASAMSA_EMAIL_SUPPORT],
        fail_silently=False,
    )


def send_mail_to(subject, email, template_path, template_context={}):
    html_message = render_to_string(template_path, template_context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.SERVER_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )


class CustomSchemeRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = getattr(settings, 'REDIRECT_ALLOWED_SCHEMES', [])


def convert_size(size_bytes):
   if size_bytes < 1024:
       return f'{size_bytes} B'

   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return f'{s} {size_name[i]}'
