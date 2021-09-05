import django.contrib.auth.password_validation as validators
from django.contrib.auth import get_user_model
from django.core import exceptions
from rest_auth.serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField

from apps.common.utils import send_mail_to

User = get_user_model()


class UserRetrieveSerializer(serializers.ModelSerializer):
    """
    User retrieve serializer
    """
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username'
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User creation serializer with password setting
    """
    old_password = serializers.CharField(
        max_length=32,
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'old_password', 'username'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
                'trim_whitespace': False,
                'allow_blank': True,
                'allow_null': True
            },
            'email': {'required': False},
        }
        read_only_fields = ('pk', 'is_invited')

    # def send_registration_greeting(self, user, password):
    #     send_mail_to(
    #         "Välkommen till Zammans!",
    #         user.email,
    #         'registration_greeting.html',
    #         {
    #             'user': user,
    #             'password': password
    #         }
    #     )
    #
    # def validate(self, data):
    #     password = data.get('password')
    #     if password:
    #         validators.validate_password(password=password, user=User)
    #
    #     return super(UserCreateSerializer, self).validate(data)

    def update(self, instance, validated_data):
        """
        If there is a password changing - check if the old one is correct
        """
        password = validated_data.pop('password', None)
        old_password = validated_data.pop('old_password', None)
        if password:
            if not instance.check_password(old_password):
                raise serializers.ValidationError("wrong password")

            instance.set_password(password)
            instance.save()

        return super(UserCreateSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        """
        Creates new user with an e-mail and a password, then calls 'update' to add another fields
        """
        password = validated_data.pop('password', '')
        user = User(email=validated_data.pop('email', ''))
        user.set_password(password)
        user.save()

        # self.send_registration_greeting(user, password)

        return self.update(user, validated_data)


# class CustomPasswordField(PasswordField):
#     def __init__(self, *args, **kwargs):
#         # kwargs['trim_whitespace'] = False
#         super(CustomPasswordField, self).__init__(*args, **kwargs)
#
#
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def __init__(self, *args, **kwargs):
#         super(CustomTokenObtainPairSerializer, self).__init__(*args, **kwargs)
#         self.fields['password'] = CustomPasswordField()


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    new_password1 = serializers.CharField(max_length=128, trim_whitespace=False)
    new_password2 = serializers.CharField(max_length=128, trim_whitespace=False)

    def custom_validation(self, data):
        # errors = dict()
        # for field_name in ('new_password1', 'new_password2'):
        #     password = data.get(field_name)
        #
        #     if password:
        #         try:
        #             validators.validate_password(password=password, user=self.user)
        #         except exceptions.ValidationError as e:
        #             errors[field_name] = list(e.messages)
        # if errors:
        #     raise serializers.ValidationError(errors)

        return super(CustomPasswordResetConfirmSerializer, self).custom_validation(data)


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        try:
            user = User.objects.get(email=self.reset_form.data["email"])
        except User.DoesNotExist as e:
            user = None

        return {
            'email_template_name': 'user/password_reset_email.html',
            'html_email_template_name': 'user/password_reset_email.html',
            'subject_template_name': 'user/password_reset_email_subject.txt',
            'extra_email_context': {
                'user': user,
            }
        }
