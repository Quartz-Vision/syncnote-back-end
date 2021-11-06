from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.urls import reverse

register = template.Library()


@register.simple_tag
def backend_full_url(url=''):
    return urljoin(settings.BACKEND_DOMAIN, url)


@register.simple_tag
def api_full_url(url_name):
    return backend_full_url(reverse(url_name))
