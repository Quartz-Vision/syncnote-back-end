from smtplib import SMTPException

from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.openapi_docs import (
    SendMailSerializer,
    redirect_parameters
)
from apps.common.utils import send_mail_contact, CustomSchemeRedirect


class CommonViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        operation_description="Send the e-mail",
        responses={
            200: 'OK',
            400: 'Error text'
        },
        request_body=SendMailSerializer()
    )
    @action(methods=('post',), detail=False, url_path='send-mail-support')
    def send_mail_support(self, *args, **kwargs):
        serializer = SendMailSerializer(data=self.request.data)
        serializer.is_valid(True)
        data = serializer.validated_data

        try:
            send_mail_contact(
                'Zammans - supportförfrågan',
                self.request.user,
                data.get("email", ""),
                data.get("comment", "")
            )
        except SMTPException as e:
            print(e)
            return Response('Mail sending error', status=status.HTTP_400_BAD_REQUEST)

        return Response('OK', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="link redirection",
        responses={
            301: 'redirect',
        },
        manual_parameters=redirect_parameters
    )
    @action(methods=('get',), detail=False, url_path='redirect-to', url_name='redirect_to')
    def redirect_to(self, *args, **kwargs):
        return CustomSchemeRedirect(self.request.query_params.get('url'))
