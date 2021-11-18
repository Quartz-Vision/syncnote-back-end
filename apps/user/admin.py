from django import forms
from django.contrib import admin
from django.contrib.admin.decorators import display
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from apps.common.utils import convert_size

User = get_user_model()


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(max_length=128, widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        password = self.data.get('password')
        ret = super(UserAdminForm, self).save(commit)

        if password:
            self.instance.set_password(password)
            self.instance.save()

        return ret


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # form = UserAdminForm
    fields = ('get_username',)
    readonly_fields = ('get_username', 'get_used_data_size', 'get_used_data_size')
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
