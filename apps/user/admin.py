from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

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
    fields = ('username', 'used_data_size', 'max_data_size')
    display_fields = ('username', 'used_data_size', 'max_data_size')
    ordering = ('username',)
