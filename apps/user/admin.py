from django import forms
from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from apps.common.utils import convert_size

User = get_user_model()


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # form = UserAdminForm
    fields = ('get_username', 'get_used_data_size', 'get_max_data_size', 'get_notes_count', 'get_tags_count')
    readonly_fields = ('get_username', 'get_used_data_size', 'get_max_data_size', 'get_notes_count', 'get_tags_count')
    list_display = ('get_username', 'get_used_data_size', 'get_max_data_size')
    ordering = ('-used_data_size', 'username')

    @display(ordering='max_data_size', description=_('allowed data size'))
    def get_max_data_size(self, obj):
        return convert_size(obj.max_data_size)

    @display(ordering='used_data_size', description=_('used data size'))
    def get_used_data_size(self, obj):
        return convert_size(obj.used_data_size)

    @display(ordering='username', description=_('username'))
    def get_username(self, obj):
        return obj.username

    @display(description=_('notes count'))
    def get_notes_count(self, obj):
        return obj.notes.count()

    @display(description=_('tags count'))
    def get_tags_count(self, obj):
        return obj.tags.count()
