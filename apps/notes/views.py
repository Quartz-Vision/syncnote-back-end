from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework.serializers import Serializer
from rest_framework.utils import serializer_helpers
from rest_framework import status
from rest_framework.response import Response

from apps.notes.serializers import (
    NoteSerializer,
    NotesUpdateRequestSerializer,
    NotesUpdateResponseSerializer,
    NotesUploadResponseSerializer
)
from apps.notes.utils import filter_valid_uuids, get_notes_update_diff, update_notes


class NotesViewSet(viewsets.GenericViewSet):
    """
    User update view - for the currently logged in user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.request.user.notes.all()


    @swagger_auto_schema(
        operation_description="Provides notes update so you can get updated notes and what need to be uploaded list",
        responses={
            400: 'Errors',
            200: NotesUpdateResponseSerializer(many=True),
        },
        request_body=NotesUpdateRequestSerializer(many=True)
    )
    @action(methods=('POST',), detail=False, url_path='get-updates')
    def get_updates(self, request):
        serializer = NotesUpdateRequestSerializer(data=request.data or [], many=True)
        serializer.is_valid(True)

        return Response(
            data=get_notes_update_diff(self.get_queryset(), serializer.validated_data),
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_description="Provides notes update so you can get updated notes and what need to be uploaded list",
        responses={
            400: 'Errors',
            200: NotesUploadResponseSerializer(many=True),
        },
        request_body=NoteSerializer(many=True)
    )
    @action(methods=('POST',), detail=False, url_path='send-updates')
    def send_updates(self, request):
        serializer = NoteSerializer(data=request.data or [], many=True)
        serializer.is_valid(True)

        return Response(
            data=update_notes(
                self.get_queryset(),
                serializer.validated_data,
                self.get_serializer_context()
            ),
            status=status.HTTP_200_OK
        )
