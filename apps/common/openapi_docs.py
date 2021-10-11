from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING
from rest_framework import serializers


class SendMailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    comment = serializers.CharField(
        max_length=512,
        required=False,
        allow_blank=True,
        allow_null=True
    )


redirect_parameters = [
    Parameter('url', IN_QUERY, type=TYPE_STRING, required=True)
]
